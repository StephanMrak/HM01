import multiprocessing
import pygame
import pickle
from pathlib import Path
from random import randint

# size = (1360, 768)
# active = False
# hit = False
# pos = False
# players = False
# screen = False
# rGB = False
# temp = False
# action = False
# buttons = False

path = Path(__file__).parent


# ---- For the template and for testing ----
def initialize_info(ns_info):
    ns_info.active = True
    ns_info.debug = True
    ns_info.size = (1360, 768)
    ns_info.players = ["Alice", "Bob", "Carlos", "Dave"]
    ns_info.hit = False
    ns_info.pos = []
    ns_info.rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    ns_info.temp = 10
    ns_info.action = False  # TODO was ist action?
    ns_info.buttons = False


def randomize_new_hit(ns_info):
    ns_info.hit = True
    ns_info.pos = [randint(0, ns_info.size[0] - 1), randint(0, ns_info.size[1] - 1)]


# ---- game functions ----
def get_path():
    return path


def take_screenshot(screen):
    # TODO Ordner für spielinterne dateien?
    pygame.image.save(screen, path / "screencapture.jpg")
    with open(path / "hmscreen", "wb") as myFile:
        pickle.dump(True, myFile)


"""

def clear_pickle(filename, val):
    with open((os.path.join(path, filename)), "wb") as the_file:
        pickle.dump(val, the_file)


def clear_all():
    clear_pickle("hmplayers", False)
    clear_pickle("hmscreen", False)
    clear_pickle("hmrgb", False)


def put_rgbcolor(color):
    with open(path / "hmrgb", "wb") as rgb_file:
        pickle.dump(color, rgb_file)


def get_rgbcolor():
    try:
        with open(path / "hmrgb", "rb") as rgb_file:
            q = pickle.load(rgb_file)
            if not q:
                return False
            else:
                clear_pickle("hmrgb", False)
                return q
    # TODO das passiert wenn die Datei nicht gelesen werden kann. Das sollte nicht ignoriert werden -> rise
    except:
        return False


def screenshot_refresh():  # TODO Frage. Wofür ist die Funktion? Nur den Inhalt löschen?
    try:
        with open(path / "hmscreen", "rb") as screen_file:
            q = pickle.load(screen_file)
        if not q:
            return False
        else:
            clear_pickle("hmscreen", False)
            return True
    except:
        return False


def take_screenshot_parallel(screen):
    def create_screenshot(screen):
        # TODO muss das gelöscht werden? Kann es nicht einfach überschrieben werden?
        try:
            os.remove(path / "screencapture.jpg")
        except:
            pass
        pygame.image.save(screen, path / "screencapture.jpg")

        with open(path / "hmscreen", "wb") as screen_file:
            pickle.dump(True, screen_file)

    t = multiprocessing.Process(target=create_screenshot, args=(screen,))
    t.start()
    # t.join()


def take_screenshot(screen):
    try:
        os.remove(path / "screencapture.jpg")
    except:
        True
    pygame.image.save(screen, path / "screencapture.jpg")
    with open(path / "hmscreen", "wb") as screen_file:
        pickle.dump(True, screen_file)


# def game_isactive():
#     try:
#         file = open((os.path.join(path, "hmsys")), 'rb')
#         q = pickle.load(file)
#         file.close()
#         if q != True:
#             clear_pickle("hmsys", True)
#             return False
#         else:
#             return True
#     except:
#         return True
#
#
# def close_pygame():
#     file = open((os.path.join(path, "hmsys")), 'wb')
#     pickle.dump(False, file)
#     file.close()


def check_ifdebug():
    # TODO ggf. Pfade anpassen
    import io

    try:
        with io.open("/sys/firmware/devicetree/base/model", "r") as m:
            if "raspberry pi" in m.read().lower():
                return False
    except Exception:
        pass
    return True


def get_size():
    return size


def get_pos():
    return pos


def put_pos(pos):
    pos = pos


def get_temp():
    return temp


def put_temp(temp):
    temp = temp


def get_button_names():
    return buttons


def put_button_names(names):
    buttons = names


def hit_detected():
    if hit:
        hit = False
        return True
    else:
        return False


def put_hit():
    hit = True


def get_action():
    action = action
    action = False
    return action


def put_action(number):
    action = number


def put_playernames(playernames):
    with open((os.path.join(path, "hmplayers")), "wb") as player_file:
        pickle.dump(playernames, player_file)


def get_playerstatus():
    # Returns player names and their resprective status (active=True, inactive=False) in an array of arrays:
    # [['player name 1', True], ['player name 2', False]]
    # If there is no player, an empty array is returned: []
    try:
        with open((os.path.join(path, "hmplayers")), "rb") as player_file:
            q = pickle.load(player_file)
        if not q:
            return []
        else:
            return q
    except:
        # TODO das passiert wenn die Datei nicht gelesen werden kann. Das sollte nicht ignoriert werden -> rise
        return False


def get_all_playernames():
    q = get_playerstatus()
    return [name for name, status in q]


def get_playernames():
    q = get_playerstatus()
    return [name for name, status in q if status]
"""

# print(os.path.realpath(__file__))
# print(os.path.realpath(__file__).replace("functions_intern.py", ""))
# print("")
# print(Path.cwd())
# print(Path(__file__).parent)
# print(Path(__file__).parent / "screencapture.jpg")
