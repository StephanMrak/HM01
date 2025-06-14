import remi.gui as gui
from remi import start, App, Server
import time
import multiprocessing
import queue
from random import randint
from datetime import datetime


class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self, e_warmup, e_stop, q_hit, shared_ns):
        self.e_warmup = e_warmup
        self.e_stop = e_stop
        self.q_hit = q_hit
        self.shared_ns = shared_ns

        self.size = shared_ns.size  # (1360, 768). Defined during initialization in multitest.py
        container = gui.VBox(width=120, height=100)
        self.lbl = gui.Label("Hello world!")

        self.bt = gui.Button("Press me!")
        self.bt.onclick.do(self.on_button_pressed)

        self.bt_stop = gui.Button("Stop")
        self.bt_stop.onclick.do(self.button_stop_pressed)

        # appending a widget to another, the first argument is a string key
        container.append(self.lbl)
        container.append(self.bt)
        container.append(self.bt_stop)

        # returning the root widget
        return container

    # listener function
    def on_button_pressed(self, widget):
        self.bt.set_text("Press me again!")
        # print(self.shared_ns)
        # print(self.shared_ns.ii)
        # print(self.e_warmup)
        # print(self.e_warmup.is_set())
        print("MyApp: read shared_ns.ii", self.shared_ns.ii)

        x_pixel = randint(0, self.size[0] - 1)
        y_pixel = randint(0, self.size[1] - 1)
        hit = {
            "x_pixel": x_pixel,
            "y_pixel": y_pixel,
            "x_percent": x_pixel / self.size[0],
            "y_percent": y_pixel / self.size[1],
            "datetime": datetime.now(),
        }
        try:
            self.q_hit.put_nowait(hit)
        except queue.Full:
            raise Exception("Hit Queue is full.")
        print("MyApp: put a random hit in the queue q_hit", hit)

    def button_stop_pressed(self, widget):
        # self.server.server_starter_instance._alive = False
        # self.server.server_starter_instance._sserver.shutdown()
        self.server.server_starter_instance.stop()
        print("server stopped")
        self.e_stop.set()


def myServer(e_warmup, e_stop, q_hit, shared_ns):
    # start the remi server. Events and shared namespaces are passed via userdata. The parameter are received by main(). https://www.reddit.com/r/RemiGUI/comments/frswxg/how_to_pass_additional_arguments_through_start/
    start(MyApp, port=8081, userdata=(e_warmup, e_stop, q_hit, shared_ns))


def Counter(e_warmup, e_stop, q_hit, shared_ns):
    e_warmup.wait(timeout=30.0)  # blocks and waits for the warmup finished event
    if not e_warmup.is_set():  # check if it was the timeout
        print("ERROR Timeout")
        return

    i = 0
    while True:
        i += 1
        time.sleep(1)
        shared_ns.ii = i
        print("numbertwo: set shared_ns.ii", i)
        if e_stop.is_set():
            return

        try:
            hit = q_hit.get_nowait()
            print("Counter: received a hit", hit.get("x_pixel"), hit.get("y_pixel"))
        except queue.Empty:
            pass


def Warmup(e_warmup):
    time.sleep(10)
    e_warmup.set()
