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
    ns_info.all_players = {"Alic": True, "Bob": True, "Carlos": False, "Dave": True}
    ns_info.players = ["Alice", "Bob", "Dave"]
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
    # TODO Ordner für interne dateien?
    pygame.image.save(screen, path / "resources" / "screencapture.jpg")
    with open(path / "hmscreen", "wb") as myFile:
        pickle.dump(True, myFile)
