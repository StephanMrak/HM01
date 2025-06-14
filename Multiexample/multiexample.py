import multiprocessing.process
import multiprocessing
import multiexample_functions


if __name__ == "__main__":

    with multiprocessing.Manager() as manager:
        # is false at the beginning. Processes that call wait() will block until set() is called to set the internal flag to true.
        event_warmup = manager.Event()
        event_stop = manager.Event()
        queue_hit = manager.Queue(maxsize=1)
        namespace = manager.Namespace()
        namespace.size = (1360, 768)
        namespace.ii = 0

        t0 = multiprocessing.Process(
            name="Warmup",
            target=multiexample_functions.Warmup,
            args=(event_warmup,),
        )
        t0.start()

        t1 = multiprocessing.Process(
            name="Server",
            target=multiexample_functions.myServer,
            args=(
                event_warmup,
                event_stop,
                queue_hit,
                namespace,
            ),
        )
        t1.start()

        t2 = multiprocessing.Process(
            name="Counter",
            target=multiexample_functions.Counter,
            args=(
                event_warmup,
                event_stop,
                queue_hit,
                namespace,
            ),
        )
        t2.start()

        t0.join()
        t1.join()
        t2.join()
