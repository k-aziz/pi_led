import threading


class MyTimer:

    def __init__(self, interval, callback, args=None, kwargs=None):
        self.timer = None
        self.interval = interval
        self.callback = callback
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}

    def start(self):
        self.timer = threading.Timer(self.interval, self.callback, *self.args, **self.kwargs)
        print(f"starting {self.interval} second timer")
        self.timer.start()

    def cancel(self):
        print("stopping timer")
        self.timer.cancel()
