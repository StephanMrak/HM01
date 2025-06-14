import sys
import logging
import time
import multiprocessing
from random import randint
from pathlib import Path

from RemiServer import myServer

debug = True  # show debug messages

logging.basicConfig(
    level=logging.DEBUG if debug else logging.INFO,
    format="%(name)-16s %(levelname)-8s %(message)s",
)
# logging.getLogger("remi").setLevel(level=logging.DEBUG if debug else logging.INFO)


def initialize_info(ns_info):  # Initialize the shared namespace with example values.
    ns_info.active = True
    ns_info.debug = True
    ns_info.size = (1360, 768)
    ns_info.all_players.update({"Alice": True, "Bob": True, "Carlos": False, "Dave": True})
    active_players = [name for name, active in ns_info.all_players.items() if active]
    ns_info.active_players = active_players
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

    logger = logging.getLogger(__name__)
    game_path = Path(__file__).parent / "games"
    sys.path.append(str(game_path))

    with multiprocessing.Manager() as manager:
        event_warmup = manager.Event()
        event_stop = manager.Event()
        queue_hit = manager.Queue(maxsize=1)

        # Namespace must only contain manager objects like manager.dict() or manager.list()
        namespace = manager.Namespace()
        namespace.all_players = manager.dict()
        namespace.active_players = manager.list()
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
