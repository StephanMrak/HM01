import multiprocessing
import time
import hmsysteme
from check_for_updates import CheckForUpdates, UpdateSystem
import subprocess

WIDTH = '100%'
HEIGHT = '1000px'
action_buttons = []


def start_game(gamefile, backgroundqueue):
    hmsysteme.open_game()
    time.sleep(0.5)
    game_module = __import__(gamefile)
    process = multiprocessing.Process(target=game_module.main)
    process.start()
    return process


def close_game(game_processes, buttons, backgroundqueue):
    for process in game_processes:
        if process.is_alive():
            hmsysteme.close_game()
            hmsysteme.put_button_names(False)
            time.sleep(0.5)
            process.terminate()
    for button in buttons:
        try:
            button.set_text("no function")
            button.set_enabled(False)
        except:
            pass


def is_name_unique(name, players):
    return all(player[0] != name for player in players)


def mobile_com(threadname, path2, gamefiles, backgroundqueue, debug_flag):
    import os
    import io
    import PIL.Image
    import remi.gui as gui
    from remi import start, App

    path = hmsysteme.get_path()
    game_processes = []
    backgroundqueue.put("open")

    container_home = gui.VBox(width=WIDTH, height=HEIGHT, style={'background': '#404040', 'color': 'white'})
    container_players = gui.VBox(width=WIDTH, height=HEIGHT, style={'background': '#404040', 'color': 'white'})
    container_games = gui.VBox(width=WIDTH, height=HEIGHT, style={'background': '#404040', 'color': 'white'})
    container_settings = gui.VBox(width=WIDTH, height=HEIGHT, style={'background': '#404040', 'color': 'white'})

    class PILImageViewer(gui.Image):
        def __init__(self, **kwargs):
            super().__init__(os.path.join(path, "screencapture.jpg"), **kwargs)
            self._buf = None

        def load(self, file_path_name):
            pil_image = PIL.Image.open(file_path_name)
            self._buf = io.BytesIO()
            pil_image.save(self._buf, format='JPEG')
            self.refresh()

        def refresh(self):
            timestamp = int(time.time() * 1e6)
            self.attributes['src'] = f"/{id(self)}/get_image_data?update_index={timestamp}"

        def get_image_data(self, update_index):
            if self._buf is None:
                return None
            self._buf.seek(0)
            headers = {'Content-type': 'image/jpg'}
            return [self._buf.read(), headers]

    def refresh_player_list():
        container_players.empty()

        label = gui.Label('Input Player Name:', width='50%', height='35px',
                          style={'font-size': '25px', 'text-align': 'left', 'color': 'white'})
        input_name = gui.TextInput(width='30%', height='35px',
                                   style={'font-size': '30px', 'text-align': 'left', 'background': '#606060',
                                          'color': 'white'})

        def on_name_entered(widget, new_value):
            name = input_name.get_text()
            if name and len(name) < 20:
                current_players = hmsysteme.get_playerstatus() or []
                if is_name_unique(name, current_players):
                    current_players.append([name, True])
                    hmsysteme.put_playernames(current_players)
                    refresh_player_list()

        input_name.onchange.do(on_name_entered)
        container_players.append(label)
        container_players.append(input_name)
        container_players.append(gui.Label('', height='10px'))

        player_list = hmsysteme.get_playerstatus() or []
        grid = gui.GridBox(width=500)
        grid.style.update({"background": "#404040", "color": "white"})

        layout = [['delete' + str(i), 'check' + str(i), 'label' + str(i)] for i in range(len(player_list))]
        grid.define_grid(layout)

        for i, (player_name, is_active) in enumerate(player_list):
            checkbox = gui.CheckBox(is_active, width='50px', height='50px', margin='1%',
                                    style={'font-size': '20px', 'text-align': 'center'})
            label = gui.Label(player_name, width='300px', height='50px', margin='1%',
                              style={'font-size': '30px', 'text-align': 'left'})
            delete_button = gui.Button('DELETE', width='130px', height='50px', margin='1%',
                                       style={'font-size': '20px', 'text-align': 'center', 'background': 'red'})

            def toggle_active(widget, new_value, index=i):
                player_list[index][1] = new_value
                hmsysteme.put_playernames(player_list)

            def delete_player(widget, index=i):
                player_list.pop(index)
                hmsysteme.put_playernames(player_list)
                refresh_player_list()

            checkbox.onchange.do(toggle_active)
            delete_button.onclick.do(delete_player)
            grid.append({f'delete{i}': delete_button, f'check{i}': checkbox, f'label{i}': label})

        grid.set_row_gap(20)
        grid.set_column_gap(20)
        container_players.append(grid)

    class HMInterface(App):
        def __init__(self, *args):
            super().__init__(*args)

        def idle(self):
            time.sleep(0.1)
            if hmsysteme.screenshot_refresh():
                self.image_widget.load(file_path_name=os.path.join(path, "screencapture.jpg"))

            if hmsysteme.game_isactive():
                button_names = hmsysteme.get_button_names()
                if button_names:
                    for i, button in enumerate(action_buttons):
                        if i < len(button_names):
                            button.set_text(button_names[i])
                            button.set_enabled(True)
                        else:
                            button.set_text("no function")
                            button.set_enabled(False)

        def main(self):
            global action_buttons
            tab_box = gui.TabBox(width=WIDTH,
                                 style={'color': 'white', 'background-color': '#404040', 'font-size': '20px'})

            self.status_label = gui.Label('No game running yet', width='100%', height='35px',
                                          style={'font-size': '25px', 'text-align': 'left', 'color': 'white'})
            container_home.append(self.status_label)

            self.image_widget = PILImageViewer(width=WIDTH)
            self.image_widget.load(file_path_name=os.path.join(path2, "logo.jpg"))
            container_home.append(self.image_widget)

            for i in range(9):
                def button_action(widget, index=i):
                    hmsysteme.put_action(index + 1)

                button = gui.Button("no function", width='31%', height='50px', margin='1%',
                                    style={'font-size': '20px', 'text-align': 'center', 'background': '#606060'})
                button.onclick.do(button_action)
                button.set_enabled(False)
                action_buttons.append(button)
                container_home.append(button)

            for i, game in enumerate(gamefiles):
                def start_game_callback(widget, index=i):
                    close_game(game_processes, action_buttons, backgroundqueue)
                    game_processes.append(start_game(gamefiles[index], backgroundqueue))
                    self.status_label.set_text(f"{gamefiles[index]} now running")

                game_button = gui.Button(f'Run {game}', width='31%', height='50px', margin='1%',
                                         style={'font-size': '20px', 'text-align': 'center', 'background': '#606060'})
                game_button.onclick.do(start_game_callback)
                container_games.append(game_button)

            for label, handler in [
                ("Close all", self.on_close_all),
                ("Stop Server", self.on_stop_server),
                ("System Shutdown", self.on_shutdown),
                ("System Reset", self.on_reset),
                ("System Reboot", self.on_reboot),
                ("Check for Updates", self.on_check_updates),
                ("Add Device to Local Network", self.on_add_device)
            ]:
                button = gui.Button(label, width='31%', height='50px', margin='1%',
                                    style={'font-size': '20px', 'text-align': 'center', 'background': '#606060'})
                button.onclick.do(handler)
                container_settings.append(button)

            refresh_player_list()

            tab_box.append(container_home, 'Home')
            tab_box.append(container_players, 'Players')
            tab_box.append(container_games, 'Games')
            tab_box.append(container_settings, 'Settings')
            return tab_box

        def on_close_all(self, widget):
            close_game(game_processes, action_buttons, backgroundqueue)
            self.status_label.set_text("No game running yet")

        def on_stop_server(self, widget):
            self.server.server_starter_instance._alive = False
            self.server.server_starter_instance._sserver.shutdown()

        def on_shutdown(self, widget):
            dialog = gui.GenericDialog(width=350, title='Shutdown',
                                       message='Do you really want to shutdown the system?')
            dialog.confirm_dialog.do(lambda w: subprocess.run(["sudo", "poweroff"]))
            dialog.show(self)

        def on_reset(self, widget):
            pass  # To be implemented

        def on_reboot(self, widget):
            dialog = gui.GenericDialog(width=350, title='Reboot', message='Do you really want to reboot the system?')
            dialog.confirm_dialog.do(lambda w: subprocess.run(["sudo", "reboot"]))
            dialog.show(self)

        def on_check_updates(self, widget):
            if CheckForUpdates():
                dialog = gui.GenericDialog(width=350, title='Update Available', message='Do you want to update now?')
                dialog.confirm_dialog.do(lambda w: UpdateSystem())
            else:
                dialog = gui.GenericDialog(width=350, title='No Updates', message='No update available')
            dialog.show(self)

        def on_add_device(self, widget):
            networks = self.scan_wifi()
            dialog = gui.GenericDialog(width=350, title='Available Networks', message='Select and connect to a network')
            list_view = gui.ListView.new_from_list(networks, width=300, height=120, margin='10px')
            password_input = gui.TextInput(width='30%', height='35px', style={'font-size': '20px'})
            dialog.append(password_input)
            dialog.append(list_view)
            dialog.confirm_dialog.do(lambda w: self.connect_to_wifi(list_view.get_value(), password_input.get_text()))
            dialog.show(self)

        def scan_wifi(self):
            result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
            return [line for line in result.stdout.strip().split("\n") if line]

        def connect_to_wifi(self, ssid, password):
            if ssid:
                subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password])

    if debug_flag:
        start(HMInterface, start_browser=False)
    else:
        start(HMInterface, address='0.0.0.0', port=8081, multiple_instance=False, enable_file_cache=True,
              update_interval=0.1, start_browser=False)
