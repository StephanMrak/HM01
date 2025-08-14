import multiprocessing
import time
import hmsysteme
from check_for_updates import CheckForUpdates, UpdateSystem
import subprocess
import WiFiHelper

WIDTH = '100%'
HEIGHT = '1500px'
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

    default_style = {
        'background': '#2c2c2c',
        'color': '#ffffff',
        'font-size': '18px',
        'border-radius': '10px',
        'border': 'none',
        'padding': '10px',
        'font-family': 'Segoe UI, Roboto, sans-serif'
    }

    button_style = {
        'font-size': '18px',
        'text-align': 'center',
        'background': '#3a3a3a',
        'color': '#ffffff',
        'border': 'none',
        'border-radius': '8px',
        'margin': '10px',
        'padding': '10px 10px',
        'box-shadow': '0 4px 6px rgba(0,0,0,0.1)'
    }

    button_small_style = {
        'font-size': '18px',
        'text-align': 'center',
        'background': '#3a3a3a',
        'color': '#ffffff',
        'border': 'none',
        'border-radius': '8px',
        'margin': '10px',
        'padding': '2px 2px',
        'box-shadow': '0 4px 6px rgba(0,0,0,0.1)'
    }

    label_style = {
        'font-size': '20px',
        'color': '#ffffff',
        'margin-bottom': '10px'
    }

    input_style = {
        'text-align': 'left',
        'font-size': '18px',
        'background': '#444',
        'color': '#fff',
        'border': '1px solid #666',
        'border-radius': '8px',
        'padding': '4px',
        'line-height': '35px',
        'vertical-align': 'middle'
    }

    dialog_style = {
        'background': '#2c2c2c',
        'color': '#ffffff',
        'font-size': '18px',
        'border-radius': '12px',
        'padding': '20px',
        'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.5)'
    }

    listview_style = {
        'text-align': 'center',
        'background': '#2c2c2c',
        'color': '#ffffff',
        'font-size': '18px',
        'border-radius': '10px',
        'border': 'none',
        'font-family': 'Segoe UI, Roboto, sans-serif'
    }

    grid_style = {
        'text-align': 'left',
        'font-size': '18px',
        'color': '#fff',
        'padding': '4px',
        'line-height': '35px',
        'vertical-align': 'middle'
    }
    checkbox_style = {
        'width': '50px',
        'height': '50px',
        'margin': '1%',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
        'background-color': '#2c2c2c',
        'border-radius': '8px'
    }


    tab_active_style = {
        'width': '20%',
        'height': '35px',
        'background': '#444',
        'color': '#fff',
        'padding': '2px 2px',
        'border': '1px solid #666',
        'border-radius': '10px',
        'margin-right': '4px',
        'font-size': '16px',
        'cursor': 'pointer',
        'line-height': '35px',
        'font-weight': 'bold',
        'vertical-align': 'middle'

    }

    tab_inactive_style = {
        'width': '20%',
        'height': '35px',
        'background': '#3a3a3a',
        'color': '#fff',
        'padding': '2px 2px',
        'border': '1px solid #666',
        'border-radius': '10px',
        'margin-right': '4px',
        'font-size': '16px',
        'cursor': 'pointer',
        'line-height': '35px',
        'font-weight': 'normal',
        'vertical-align': 'middle'
    }


    container_home = gui.VBox(width=WIDTH, height=HEIGHT, style=default_style.copy())
    container_players = gui.VBox(width=WIDTH, height=HEIGHT, style=default_style.copy())
    container_games = gui.VBox(width=WIDTH, height=HEIGHT, style=default_style.copy())
    container_settings = gui.VBox(width=WIDTH, height=HEIGHT, style=default_style.copy())

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

        label = gui.Label('Input Player Name:', width='50%', height='35px', style=label_style.copy())
        input_name = gui.TextInput(width='30%', height='35px', style=input_style.copy())

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
        grid.style.update(default_style.copy())
        grid.set_row_gap(20)
        grid.set_column_gap(20)

        layout = [['delete' + str(i), 'check' + str(i), 'label' + str(i)] for i in range(len(player_list))]
        grid.define_grid(layout)

        for i, (player_name, is_active) in enumerate(player_list):
            checkbox = gui.CheckBox(is_active, width='35px', height='35px', margin='1%', style=checkbox_style.copy())
            label = gui.Label(player_name, width='300px', height='35px', margin='1%', style=grid_style.copy())
            delete_button = gui.Button('DELETE', width='130px', height='35px', margin='1%',
                                       style={**button_small_style.copy(), 'background': 'red'})

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

        container_players.append(grid)

    class HMDialog(gui.GenericDialog):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        def apply_style(self):
            self.style.update(dialog_style.copy())
            for key, child in self.children.items():
                if isinstance(child, gui.Container):
                    child.style.update(default_style.copy())  # or dialog_style if you prefer
                    for subchild in child.children.values():
                        if isinstance(subchild, gui.Widget):
                            subchild.style.update(default_style.copy())
                else:
                    child.style.update(default_style.copy())
            self.conf.style.update(button_small_style.copy())
            self.cancel.style.update(button_small_style.copy())
            self.container.style.update(default_style.copy())

    def get_wifi_helper():
        global _wifi_helper
        if _wifi_helper is None:
            _wifi_helper = WifiHelper()
        return _wifi_helper

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
            tab_box = gui.TabBox(width=WIDTH, style=default_style.copy())

            self.status_label = gui.Label('No game running yet', width='100%', height='35px', style=label_style.copy())
            container_home.append(self.status_label)

            self.image_widget = PILImageViewer(width='100%', height='auto',
                                               style={'border-radius': '12px', 'box-shadow': '0 2px 12px rgba(0,0,0,0.2)'})
            self.image_widget.load(file_path_name=os.path.join(path2, "logo.jpg"))
            container_home.append(self.image_widget)

            for i in range(9):
                def button_action(widget, index=i):
                    hmsysteme.put_action(index + 1)

                button = gui.Button("no function", width='31%', height='50px', style=button_style.copy())
                button.onclick.do(button_action)
                button.set_enabled(False)
                action_buttons.append(button)
                container_home.append(button)

            for i, game in enumerate(gamefiles):
                def start_game_callback(widget, index=i):
                    close_game(game_processes, action_buttons, backgroundqueue)
                    game_processes.append(start_game(gamefiles[index], backgroundqueue))
                    self.status_label.set_text(f"{gamefiles[index]} now running")

                game_button = gui.Button(f'Run {game}', width='31%', height='50px', style=button_style.copy())
                game_button.onclick.do(start_game_callback)
                container_games.append(game_button)

            for label, handler in [
                ("Close all", self.on_close_all),
                ("System Shutdown", self.on_shutdown),
                ("System Reboot", self.on_reboot),
                ("Check for Updates", self.on_check_updates),
                ("Add Device to Local Network", self.on_add_device)
            ]:
                button = gui.Button(label, width='31%', height='50px', style=button_style.copy())
                button.onclick.do(handler)
                container_settings.append(button)

            refresh_player_list()

            tab_box.append(container_home, 'Home')
            tab_box.append(container_players, 'Players')
            tab_box.append(container_games, 'Games')
            tab_box.append(container_settings, 'Settings')

            self.update_tab_styles(tab_box,'Home')
            tab_box.on_tab_selection.do(lambda widget, tab_name: self.update_tab_styles(widget,tab_name))


            return tab_box

        def on_close_all(self, widget):
            close_game(game_processes, action_buttons, backgroundqueue)
            self.status_label.set_text("No game running yet")

        def on_stop_server(self, widget):
            self.server.server_starter_instance._alive = False
            self.server.server_starter_instance._sserver.shutdown()

        def on_shutdown(self, widget):
            dialog = HMDialog(width=350, title='Shutdown', message='Do you really want to shutdown the system?')
            dialog.apply_style()
            dialog.confirm_dialog.do(lambda w: subprocess.run(["sudo", "poweroff"]))
            dialog.show(self)

        def on_reset(self, widget):
            pass

        def on_reboot(self, widget):
            dialog = HMDialog(width=350, title='Reboot', message='Do you really want to reboot the system?')
            dialog.apply_style()
            dialog.confirm_dialog.do(lambda w: subprocess.run(["sudo", "reboot"]))
            dialog.show(self)

        def on_check_updates(self, widget):
            if CheckForUpdates():
                dialog = HMDialog(width=350, title='Update Available', message='Do you want to update now?')
                dialog.style.update(default_style.copy())
                dialog.confirm_dialog.do(lambda w: UpdateSystem())
            else:
                dialog = HMDialog(width=350, title='No Updates', message='No update available')
                dialog.style.update(default_style.copy())
            dialog.apply_style()
            dialog.show(self)

        def adddevicecallback(self, widget, selectedkey):
            for key,value in widget.children.items():
                if selectedkey==key:
                    value.style.update({**listview_style.copy(), 'background': '#444'})
                else:
                    value.style.update(listview_style.copy())

        def update_tab_styles(self, tab_box, selected_tab_name):
            for tab_name, tab_button in tab_box.children['_container_tab_titles'].children.items():
                if tab_name == selected_tab_name:
                    tab_button.style.update(tab_active_style)
                else:
                    tab_button.style.update(tab_inactive_style)


        def on_add_device(self, widget):
            networks = self.scan_wifi()
            dialog = HMDialog(width=350, title='Available Networks')
            dialog.style.update(default_style.copy())

            list_view = gui.ListView.new_from_list(networks, width=300, height=120, margin='10px')
            list_view.style.update(default_style.copy())
            list_view.onselection.do(self.adddevicecallback)
            for key, value in list_view.children.items():
                value.style.update(listview_style.copy())
            password_input = gui.TextInput(width='50%', height='35px', style=input_style.copy())

            dialog.add_field_with_label("listview_ssids","select network to connect",list_view)
            dialog.add_field_with_label("psw_input", "enter password", password_input)
            dialog.apply_style()
            dialog.confirm_dialog.do(lambda w: self.connect_to_wifi(list_view.get_value(), password_input.get_text()))
            dialog.show(self)

        def scan_wifi(self):
            return get_wifi_helper().scan_for_ssids()

        def connect_to_wifi(self, ssid, password):
            if ssid:
                get_wifi_helper().connect_to_network(ssid, password)




    if debug_flag:
        start(HMInterface, start_browser=False)
    else:
        start(HMInterface, address='0.0.0.0', port=8081, multiple_instance=False, enable_file_cache=True,
              update_interval=0.1, start_browser=False)
