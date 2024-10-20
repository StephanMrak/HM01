import sys
import remi.gui as gui
from remi import start, App, Server
import multiprocessing
from pathlib import Path
from random import randint
import importlib
import logging
import time

import mimetypes

debug = False

if False:  # logging settings
    logger = logging.getLogger("mxobile_com")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # file handler
    fh = logging.FileHandler("mobile_com.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("")
    logger.info("------------ Start of a new session -----------")
    print("aaahhh")

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, 0)
    GPIO_exessible = True
except:
    GPIO_exessible = False
else:
    import time


style_lbl_info = {
    "color": "white",
    "font-size": "20px",
    "text-align": "left",
    "background-color": "#404040",
    "padding-left": "15px",
    "display": "flex",
    "align-items": "center",
}


class SuperImage(gui.Image):
    def __init__(self, file_path_name=None, **kwargs):
        super(SuperImage, self).__init__("resources/screencapture.jpg", **kwargs)

        self.imagedata = None
        self.mimetype = None
        self.encoding = None
        self.load(file_path_name)

    def load(self, file_path_name):
        self.mimetype, self.encoding = mimetypes.guess_type(file_path_name)
        with open(file_path_name, "rb") as f:
            self.imagedata = f.read()
        self.refresh()

    def refresh(self):
        i = int(time.time() * 1e6)
        self.attributes["src"] = "/%s/get_image_data?update_index=%d" % (id(self), i)

    def get_image_data(self, update_index):
        headers = {"Content-type": self.mimetype if self.mimetype else "application/octet-stream"}
        return [self.imagedata, headers]


class MyApp(App):
    def __init__(self, *args):
        self.res_path = Path(__file__).parent / "resources"
        self.P_game = multiprocessing.Process()
        self.wait_for_warmup = True
        self.game_buttons = []
        super(MyApp, self).__init__(*args, static_file_path={"res_folder": self.res_path})

    def idle(self):
        if self.e_stop.is_set():
            self._log.warning("Mobile application shutting down now.")
            self.close()

        if self.e_warmup.is_set() and self.wait_for_warmup:
            self.wait_for_warmup = False
            self.lbl_info_game.set_text("")

            for game in self.game_buttons:
                game.set_enabled(True)

        # TODO update only every second?
        current_lstat = Path("resources", "screencapture.jpg").stat().st_mtime
        if self.screenshot_lstat != current_lstat:
            self.screenshot_lstat = current_lstat
            self.img_home_background.load(file_path_name=Path("resources", "screencapture.jpg"))
            # self.img_home_background.set_image(image="res_folder:screencapture.jpg")
            # print("3", self.img_home_background.attributes)

    def page_home(self):
        page_container = gui.VBox(
            width="100%",
            height="100%",
            style={
                # "font-size": "15px",
                # "align": "left",
                "justify-content": "space-between",
                # "align-items": "center",
                # "background-image": "url('res_folder:logo_rotate.jpg')",
            },
        )

        self.lbl_info_home = gui.Label(
            text="No game running",
            height="40px",
            style=style_lbl_info,
        )
        page_container.append(self.lbl_info_home)

        self.img_home_background = SuperImage(
            file_path_name=Path("resources", "logo_rotate.jpg"),
            style={"margin": "auto", "display": "block"},
        )
        page_container.append(self.img_home_background)
        return page_container

    def page_players(self):
        page_container = gui.VBox(
            width="100%",
            height="100%",
            style={
                # "font-size": "15px",
                # "align": "left",
                "background-color": "white",
                "justify-content": "space-between",
                # "align-items": "center",
            },
        )

        lbl_info_players = gui.Label(
            text="Input player name",
            height="40px",
            style=style_lbl_info,
        )
        page_container.append(lbl_info_players)

        txt_new_player = gui.TextInput(
            single_line=True,
            # hint="Type in new player name and press Enter",
            width="30%",
            height="35px",
            style={"font-size": "20px", "color": "white", "background-color": "#606060"},
        )
        txt_new_player.onchange.do(self.create_new_player)
        page_container.append(txt_new_player)

        self.grid_player_names = gui.VBox(
            width="30%",
            style={
                "background-color": "#404040",
            },
        )
        page_container.append(self.grid_player_names)

        self.update_page_players()

        return page_container

    def update_page_players(self):
        self.grid_player_names.empty()

        for name, active in self.shared_ns.all_players.items():
            h_cont_player = gui.HBox(
                width="100%",
                style={
                    "justify-content": "flex-start",
                    "align-items": "center",
                },
            )

            btn_delete_player = gui.Button(
                text="DELETE",
                width="80px",
                user_data=name,
                style={"background-color": "red", "box-shadow": "none"},
            )
            btn_delete_player.onclick.do(self.delete_player)
            h_cont_player.append(btn_delete_player)

            chk_player_active = gui.CheckBox(checked=active, user_data=name)
            chk_player_active.onchange.do(self.player_active_change)
            chk_player_active.get_value()
            h_cont_player.append(chk_player_active)
            # self.grid_player_names.append(lbl_player_name)

            lbl_player_name = gui.Label(text=name)
            h_cont_player.append(lbl_player_name)
            # self.grid_player_names.append(lbl_player_name)

            self.grid_player_names.append(h_cont_player)

    def create_new_player(self, widget, new_name):
        self._log.debug(f"{widget=}")
        self._log.debug(f"{new_name=}")
        player_names = self.shared_ns.all_players.keys()

        if new_name not in player_names and new_name != "" and len(new_name) < 30:
            self.shared_ns.all_players.update({new_name: True})
            widget.set_text("")

        self.update_page_players()

    def player_active_change(self, widget, active):
        # The name was set with user_data. It is stored in .attributes["value"]
        name = widget.attributes["value"]

        # update the active state of a player
        self.shared_ns.all_players.update({name: active})

        # update the active player list
        active_players = [name for name, active in self.shared_ns.all_players.items() if active]
        self.shared_ns.active_players = active_players

    def delete_player(self, widget):
        self._log.info(widget)
        self._log.info(f"{widget.kwargs['user_data']} deleted")
        # The name was save with user_data. It is stored in .kwargs["user_data"]
        name = widget.kwargs["user_data"]

        # delete the selected player from the all_players list
        self.shared_ns.all_players.pop(name)
        self.update_page_players()

        # update the active player list
        active_players = [name for name, active in self.shared_ns.all_players.items() if active]
        self.shared_ns.active_players = active_players

    def page_games(self):
        vBox = gui.VBox(
            width="100%",
            height="100%",
            style={"padding-left": "0px", "font-size": "15px", "align": "left"},
        )

        self.lbl_info_game = gui.Label(
            text="Wait for warmup (~x seconds)", height="40px", style=style_lbl_info
        )
        vBox.append(self.lbl_info_game)

        # Search for all games
        games_path = Path(__file__).parent / "games"
        exclued_paths = ["game_template.py", "kalibrierung.py", "__init__.py"]
        games = [elem for elem in games_path.glob("*.py") if elem.name not in exclued_paths]

        self.game_buttons = []

        for game in games:
            self._log.info(game)
            btn_game = gui.Button(
                text=game.stem,
                user_data=game.as_posix(),
                width="31%",
                height="50px",
                margin="1%",
                style={"font-size": "20px", "text-align": "center"},
            )
            btn_game.onclick.do(self.start_game)
            btn_game.set_enabled(False)
            self.game_buttons.append(btn_game)
            vBox.append(btn_game)

        return vBox

    def start_game(self, widget):

        if self.P_game.is_alive():
            self._log.info("A game is alive. (oh nooo)")
            # TODO kill it or ignore until dead (and inform users)?
            pass
        else:
            game_path = Path(widget.kwargs["user_data"])
            game_name = game_path.stem
            self._log.info(f"---- START NEW GAME {game_name}----")
            self._log.debug(game_path)
            self._log.debug(game_path.parent)
            self._log.debug(game_name)
            self.lbl_info_home.set_text(game_name)
            # mod_game = __import__(game_name)
            # mod_game = importlib.import_module(".template", "games")

            spec = importlib.util.spec_from_file_location(game_name, str(game_path))
            module = importlib.util.module_from_spec(spec)
            sys.modules[game_name] = module
            spec.loader.exec_module(module)

            self.P_game = multiprocessing.Process(target=module.main, args=(self.shared_ns, None))
            self.P_game.start()

    def page_settings(self):
        vBox = gui.VBox(
            width="100%",
            height="100%",
            style={"padding-left": "0px", "font-size": "15px", "align": "left"},
        )
        btn_style = {
            "font-size": "20px",
            "text-align": "center",
            "background-color": "#606060",
            "box-shadow": "none",
        }

        btn_close_all = gui.Button(
            "Close all games",
            width="31%",
            height="50px",
            margin="1%",
            style=btn_style,
        )
        btn_close_all.onclick.do(self.onclick_btn_close_all)
        vBox.append(btn_close_all)

        btn_stop_server = gui.Button(
            "Stop Server",
            width="31%",
            height="50px",
            margin="1%",
            style=btn_style,
        )
        btn_stop_server.onclick.do(self.onclick_btn_stop_server)
        vBox.append(btn_stop_server)

        btn_system_shutdown = gui.Button(
            "System Shutdown",
            width="31%",
            height="50px",
            margin="1%",
            style=btn_style,
        )
        btn_system_shutdown.onclick.do(self.onclick_btn_system_shutodwn)
        vBox.append(btn_system_shutdown)

        btn_system_reset = gui.Button(
            # TODO description of what is a reset?
            "System reset",
            width="31%",
            height="50px",
            margin="1%",
            style=btn_style,
        )
        btn_system_reset.onclick.do(self.onclick_btn_system_reset)
        btn_system_reset.set_enabled(GPIO_exessible)
        vBox.append(btn_system_reset)

        return vBox

    def onclick_btn_close_all(self, widget):
        # TODO
        pass

    def onclick_btn_stop_server(self, widget):
        try:
            self.P_game.terminate()
        except:
            pass
        self.close()

    def onclick_btn_system_shutodwn(self, widget):
        dialog = gui.GenericDialog(
            width=350, title="Shutdown", message="Do you really want to shutdown the system"
        )
        dialog.confirm_dialog.do(self.shut_down_computer_now)
        dialog.show(self)

    def shut_down_computer_now(self, widget):
        import os

        if os.name == "nt":
            # For Windows operating system
            os.system("shutdown /s /t 0")
        elif os.name == "posix":
            # For Unix/Linux/Mac operating systems
            os.system("sudo shutdown now")
        else:
            logger.info("Unsupported operating system.")

    def onclick_btn_system_reset(self, widget):
        self.set_preset("0")
        self._log.info("system reset")

    def set_preset(self, percentage="0"):
        preq.put("0")
        GPIO.output(4, 1)
        time.sleep(0.1)
        GPIO.output(4, 0)

    def main(self, e_warmup, e_stop, q_hit, shared_ns):
        self._log = logging.getLogger("remi.MyApp")
        self.e_warmup = e_warmup
        self.e_stop = e_stop
        self.q_hit = q_hit
        self.shared_ns = shared_ns
        self.screenshot_lstat = Path("resources", "screencapture.jpg").stat().st_mtime

        self._log.info(f"main() Shared namespace: {self.shared_ns}")

        # style_Tab = {"color": "white", "background-color": "#404040", "font-size": "20px"}
        # tb = gui.TabBox(width="100%", height="100%", style=style_Tab)
        tb = gui.TabBox(width="100%", height="100%", style={"font-size": "25px"})

        tb_home = self.page_home()
        tb.append(tb_home, "Home")

        tb_players = self.page_players()
        tb.append(tb_players, "Players")

        tb_games = self.page_games()
        tb.append(tb_games, "Games")
        tb.select_by_name("Games")

        tb_settings = self.page_settings()
        tb.append(tb_settings, "Settings")
        # tb.select_by_name("Settings")

        return tb


def myServer(e_warmup, e_stop, q_hit, shared_ns):
    # start the remi server. Events and shared namespaces are passed via userdata. The parameter are received by main(). https://www.reddit.com/r/RemiGUI/comments/frswxg/how_to_pass_additional_arguments_through_start/
    # start(MyApp, port=8081, userdata=(e_warmup, e_stop, q_hit, shared_ns))

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(name)-16s %(levelname)-8s %(message)s",
    )
    # logging.getLogger("remi").setLevel(level=logging.DEBUG if debug else logging.INFO)
    Server(MyApp, port=8081, userdata=(e_warmup, e_stop, q_hit, shared_ns))


def initialize_info(ns_info):
    ns_info.active = True
    ns_info.debug = True
    ns_info.size = (1360, 768)
    ns_info.all_players.update({"Alice": True, "Bob": True, "Carlos": False, "Dave": True})
    ns_info.active_players = ["Alice", "Bob", "Dave"]
    ns_info.hit = False
    ns_info.pos = []
    ns_info.rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    ns_info.temp = 10
    ns_info.action = False  # TODO was ist action?
    ns_info.buttons = False


def Warmup(e_warmup):
    time.sleep(1)
    e_warmup.set()
    print("warmup finished")


if __name__ == "__main__":

    game_path = Path(__file__).parent / "games"
    sys.path.append(str(game_path))

    with multiprocessing.Manager() as manager:
        event_warmup = manager.Event()
        event_stop = manager.Event()
        queue_hit = manager.Queue(maxsize=1)
        print(queue_hit)

        namespace = manager.Namespace()
        namespace.all_players = manager.dict()
        initialize_info(namespace)

        t0 = multiprocessing.Process(
            name="Warmup",
            target=Warmup,
            args=(event_warmup,),
        )
        t0.start()

        t1 = multiprocessing.Process(
            name="mobile_com",
            target=myServer,
            args=(
                event_warmup,
                event_stop,
                queue_hit,
                namespace,
            ),
        )
        t1.start()

        t0.join()
        t1.join()
