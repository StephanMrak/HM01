import os
import time
import base64
import json
import threading
import subprocess
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_from_directory
import hmsysteme
from check_for_updates import CheckForUpdates, UpdateSystem
import WiFiHelper
import startscreen
import hardware_com_micro

# Global state management (RAM efficient)
class AppState:
    def __init__(self):
        self.game_processes = []
        self.startscreen_processes = []
        self.action_buttons = ["no function"] * 9
        self.button_states = [False] * 9
        self.current_status = "No game running yet"
        self.screenshot_cache = None
        self.screenshot_timestamp = 0
        self.wifi_helper = None
    
    def get_wifi_helper(self):
        if self.wifi_helper is None:
            self.wifi_helper = WiFiHelper.WiFiHelper()
        return self.wifi_helper
    
    def cleanup(self):
        # Clean up resources
        for process in self.game_processes + self.startscreen_processes:
            if hasattr(process, 'is_alive') and process.is_alive():
                process.terminate()
        self.game_processes.clear()
        self.startscreen_processes.clear()

# Global app state
app_state = AppState()

def mobile_com(threadname, path2, gamefiles, backgroundqueue, debug_flag):
    app = Flask(__name__)
    
    # Configure WiFi/Hotspot (simplified)
    def configure_wifi_or_hotspot():
        wifi = app_state.get_wifi_helper()
        
        if not wifi._check_setup_complete():
            print("WARNING: Setup not complete. Please run setup_wifi_helper.sh first!")
            return "ShootingRange", "123456"
        
        mode = wifi.get_current_mode()
        
        if wifi.check_internet_connection():
            ssid = wifi.get_current_ssid()
            creds = wifi.get_current_network_credentials()
            if creds:
                return creds["ssid"], creds["password"]
            return ssid, "Your Wifi Password"
        else:
            if mode != "hotspot":
                wifi.create_hotspot("ShootingRange", "123456", "DE", 7, True)
            return "ShootingRange", "123456"
    
    def show_connection_screen():
        ssid, passw = configure_wifi_or_hotspot()
        import multiprocessing
        process = multiprocessing.Process(target=startscreen.startscreen, args=(ssid, passw))
        process.start()
        return process
    
    def close_connection_screen():
        for process in app_state.startscreen_processes:
            if hasattr(process, 'is_alive') and process.is_alive():
                process.terminate()
        app_state.startscreen_processes.clear()
    
    def start_game(gamefile):
        hmsysteme.open_game()
        time.sleep(0.5)
        game_module = __import__(gamefile)
        import multiprocessing
        game_process = multiprocessing.Process(target=game_module.main)
        game_process.start()
        receiver, processor, plotter = hardware_com_micro.start(
            plot=False, process=True, debug=False, filename="", threshold=135, mode=1
        )
        return [game_process, receiver, processor]
    
    def close_game():
        for process in app_state.game_processes:
            if hasattr(process, 'is_alive') and process.is_alive():
                hmsysteme.close_game()
                hmsysteme.put_button_names(False)
                time.sleep(0.1)
                process.terminate()
        app_state.game_processes.clear()
        app_state.action_buttons = ["no function"] * 9
        app_state.button_states = [False] * 9
    
    # Initialize connection screen
    app_state.startscreen_processes.append(show_connection_screen())
    backgroundqueue.put("open")
    
    # Background update thread (lightweight)
    def background_updater():
        while True:
            try:
                # Update screenshot cache (only if changed)
                if hmsysteme.screenshot_refresh():
                    screenshot_path = os.path.join(hmsysteme.get_path(), "screencapture.jpg")
                    if os.path.exists(screenshot_path):
                        with open(screenshot_path, 'rb') as f:
                            app_state.screenshot_cache = base64.b64encode(f.read()).decode('utf-8')
                        app_state.screenshot_timestamp = time.time()
                
                # Update button states
                if hmsysteme.game_isactive():
                    button_names = hmsysteme.get_button_names()
                    if button_names:
                        for i in range(9):
                            if i < len(button_names):
                                app_state.action_buttons[i] = button_names[i]
                                app_state.button_states[i] = True
                            else:
                                app_state.action_buttons[i] = "no function"
                                app_state.button_states[i] = False
                
                time.sleep(0.5)  # Reduced update frequency
            except Exception as e:
                print(f"Background update error: {e}")
                time.sleep(1)
    
    # Start background thread
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/state')
    def get_state():
        players = hmsysteme.get_playerstatus() or []
        return jsonify({
            'status': app_state.current_status,
            'buttons': app_state.action_buttons,
            'button_states': app_state.button_states,
            'players': players,
            'games': gamefiles,
            'screenshot': app_state.screenshot_cache,
            'screenshot_timestamp': app_state.screenshot_timestamp
        })
    
    @app.route('/api/action/<int:button_id>')
    def button_action(button_id):
        if 1 <= button_id <= 9:
            hmsysteme.put_action(button_id)
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    @app.route('/api/start_game/<game_name>')
    def start_game_route(game_name):
        if game_name in gamefiles:
            close_connection_screen()
            close_game()
            app_state.game_processes.extend(start_game(game_name))
            app_state.current_status = f"{game_name} now running"
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    @app.route('/api/players', methods=['POST'])
    def manage_players():
        data = request.json
        action = data.get('action')
        
        if action == 'add':
            name = data.get('name', '').strip()
            if name and len(name) < 20:
                current_players = hmsysteme.get_playerstatus() or []
                if all(player[0] != name for player in current_players):
                    current_players.append([name, True])
                    hmsysteme.put_playernames(current_players)
                    return jsonify({'success': True})
        
        elif action == 'delete':
            index = data.get('index')
            current_players = hmsysteme.get_playerstatus() or []
            if 0 <= index < len(current_players):
                current_players.pop(index)
                hmsysteme.put_playernames(current_players)
                return jsonify({'success': True})
        
        elif action == 'toggle':
            index = data.get('index')
            current_players = hmsysteme.get_playerstatus() or []
            if 0 <= index < len(current_players):
                current_players[index][1] = not current_players[index][1]
                hmsysteme.put_playernames(current_players)
                return jsonify({'success': True})
        
        return jsonify({'success': False})
    
    @app.route('/api/system/<action>')
    def system_action(action):
        if action == 'close_all':
            close_game()
            app_state.startscreen_processes.append(show_connection_screen())
            app_state.current_status = "No game running yet"
            return jsonify({'success': True})
        
        elif action == 'shutdown':
            subprocess.run(["sudo", "poweroff"])
            return jsonify({'success': True})
        
        elif action == 'reboot':
            subprocess.run(["sudo", "reboot"])
            return jsonify({'success': True})
        
        elif action == 'check_updates':
            has_updates = CheckForUpdates()
            return jsonify({'has_updates': has_updates})
        
        elif action == 'update':
            UpdateSystem()
            return jsonify({'success': True})
        
        return jsonify({'success': False})
    
    @app.route('/api/wifi/scan')
    def scan_wifi():
        networks = app_state.get_wifi_helper().scan_for_ssids()
        return jsonify({'networks': networks})
    
    @app.route('/api/wifi/connect', methods=['POST'])
    def connect_wifi():
        data = request.json
        ssid = data.get('ssid')
        password = data.get('password')
        if ssid:
            success = app_state.get_wifi_helper().connect_to_network(ssid, password)
            return jsonify({'success': success})
        return jsonify({'success': False})
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)
    
    # Cleanup on exit
    import atexit
    atexit.register(app_state.cleanup)
    
    # Start server
    if debug_flag:
        app.run(host='127.0.0.1', port=8081, debug=True, threaded=True)
    else:
        app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
