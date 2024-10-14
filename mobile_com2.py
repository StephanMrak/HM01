import remi.gui as gui
from remi import start, App
import multiprocessing
from pathlib import Path
import functions_intern as FI
from random import randint
import pprint


class MyApp(App):
    def __init__(self, *args):
        self.res_path = Path(__file__).parent / "resources"
        super(MyApp, self).__init__(*args, static_file_path={"res_folder": self.res_path})

    def idle(self):
        pass

    def page_home(self):
        page_container = gui.VBox(
            width="100%",
            height="100%",
            style={
                # "font-size": "15px",
                # "align": "left",
                "justify-content": "space-between",
                # "align-items": "center",
            },
        )

        self.lbl_now_running = gui.Label(
            text="No game running yet",
            height="40px",
            style={
                "color": "white",
                "font-size": "20px",
                "text-align": "left",
                "background-color": "#404040",
                "padding-left": "15px",
                "display": "flex",
                "align-items": "center",
            },
        )

        img_logo = gui.Image(
            image="/res_folder:logo_rotate.jpg", style={"margin": "auto", "display": "block"}
        )  # , width="30", height="30")

        page_container.append(self.lbl_now_running)
        page_container.append(img_logo)
        return page_container

    def page_players(self):
        page_container = gui.VBox(
            width="100%",
            height="100%",
            style={
                # "font-size": "15px",
                # "align": "left",
                "background-color": "#404040",
                "justify-content": "space-between",
                # "align-items": "center",
            },
        )

        lbl_now_running = gui.Label(
            text="Input player name",
            height="40px",
            style={
                "color": "white",
                "font-size": "20px",
                "text-align": "left",
                "padding-left": "15px",
                "display": "flex",
                "align-items": "center",
            },
        )
        page_container.append(lbl_now_running)

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
        # print("widget", widget)
        # print("new text", new_name)
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
        # print(widget)
        # print(widget.kwargs["user_data"])
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
        # vBox.set_enabled(False)  # Wait for warmup to finish

        games_path = Path(__file__).parent / "games"
        # Search for all games
        exclued_paths = ["game_template.py", "kalibrierung.py"]
        games = [elem for elem in games_path.glob("*.py") if elem.name not in exclued_paths]

        for game in games:
            print(game)
            btn_game = gui.Button(
                text=game.stem,
                user_data=game.as_posix(),
                width="31%",
                height="50px",
                margin="1%",
                style={"font-size": "20px", "text-align": "center"},
            )
            btn_game.onclick.do(self.start_game)
            vBox.append(btn_game)

        return vBox

    def start_game(self, widget):
        print(widget)
        game_path = widget.kwargs["user_data"]
        self.lbl_now_running.set_text(Path(game_path).stem)
        print(game_path)
        mod_game = __import__(game_path)
        P_game = multiprocessing.Process(target=mod_game.main)
        P_game.start()
        print("ende")
        P_game.join()

    def main(self, e_warmup, e_stop, q_hit, shared_ns):
        self.shared_ns = shared_ns
        print("main() Shared namespace:", self.shared_ns)

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

        return tb


def myServer(e_warmup, e_stop, q_hit, shared_ns):
    # start the remi server. Events and shared namespaces are passed via userdata. The parameter are received by main(). https://www.reddit.com/r/RemiGUI/comments/frswxg/how_to_pass_additional_arguments_through_start/
    start(MyApp, port=8081, userdata=(e_warmup, e_stop, q_hit, shared_ns))


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


if __name__ == "__main__":

    with multiprocessing.Manager() as manager:
        event_warmup = manager.Event()
        event_stop = manager.Event()
        queue_hit = manager.Queue(maxsize=1)

        namespace = manager.Namespace()
        namespace.all_players = manager.dict()
        initialize_info(namespace)

        myServer(e_warmup=event_warmup, e_stop=event_stop, q_hit=queue_hit, shared_ns=namespace)
