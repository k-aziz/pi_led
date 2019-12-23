import time
import typing as t

from led import Colour, RgbLED


class Mode:

    def __init__(self, leds: t.List[RgbLED], colour_cycle: t.List[Colour], active=False):
        self.leds = leds
        self.colour_cycle = colour_cycle
        self.active = active

    def run(self, manager):
        raise NotImplementedError(f"The run method has not been implemented for {self.__class__.__name__}")


class ModeManager:
    interrupted = False

    def __init__(self, modes_cycle: t.List[Mode], shutdown_mode=None):
        self.modes_cycle = modes_cycle
        self.index = 0
        self.shutting_down = False
        self.shutdown_mode = shutdown_mode

    def run(self):
        while not self.shutting_down and self.shutdown_mode:
            self.cycle_through_modes()
        else:
            self.initiate_shutdown()

    def cycle_through_modes(self):
        for mode in self.modes_cycle:
            while not self.interrupted:
                print(f"Starting {mode.__class__.__name__}")
                mode.run(self)
            else:
                self.interrupted = False
                if self.shutting_down:
                    break
                else:
                    continue

    def initiate_shutdown(self):
        print("shutting down mode started")
        if self.shutting_down and self.shutdown_mode:
            while not self.interrupted:
                self.shutdown_mode.run(self)
        self.interrupted = False

    def soft_shutdown(self):
        print("soft_shutdown initiated")
        self.interrupted = True
        self.shutting_down = True


class SoftShutdown(Mode):

    def __init__(self, leds: t.List[RgbLED]):
        super().__init__(leds, [])

    def run(self, manager):
        if manager.shutting_down:
            for led in self.leds:
                led.stop()
            time.sleep(3)
        time.sleep(0.5)
        manager.shutting_down = False


class ModeA(Mode):
    def run(self, manager):
        while not manager.interrupted:
            for index, colour in enumerate(self.colour_cycle):
                # print(f'turning {colour}')
                for led in self.leds:
                    led.set_colour(colour)
                # print('complete')

                sleep_time = 2
                poll_interval = 0.5
                for _ in range(0, int(sleep_time / poll_interval)):
                    if manager.interrupted:
                        return
                    time.sleep(poll_interval)


class ModeB(Mode):
    def run(self, manager):
        while not manager.interrupted:
            for index, colour in enumerate(self.colour_cycle):
                # print(f'turning {colour}')
                RgbLED.multi_led_phase_colour_change(self.leds, colour, manager)
                # print('complete')
                sleep_time = 2
                poll_interval = 0.5
                for _ in range(0, int(sleep_time / poll_interval)):
                    if manager.interrupted:
                        return
                    time.sleep(poll_interval)
