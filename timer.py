import threading


class MyTimer:

    def __init__(self, interval, callback):
        self.timer = None
        self.interval = interval
        self.callback = callback

    def start(self):
        self.timer = threading.Timer(self.interval, self.callback)
        print("starting timer")
        self.timer.start()

    def cancel(self):
        print("stopping timer")
        self.timer.cancel()
