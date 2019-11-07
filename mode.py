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

    def __init__(self, modes_cycle: t.List[Mode]):
        self.modes_cycle = modes_cycle

    def run(self):
        print("Running mode manager")
        while True:
            for mode in self.modes_cycle:
                while True:
                    if self.interrupted:
                        break
                    print(f"Starting {mode.__class__.__name__}")
                    mode.run(self)
                self.interrupted = False


class ModeA(Mode):
    def run(self, manager):
        for index, colour in enumerate(self.colour_cycle):
            if manager.interrupted:
                return
            if index > 0:
                time.sleep(2)
            print(f'turning {colour}')
            for led in self.leds:
                led.set_colour(colour)
            print('complete')


class ModeB(Mode):
    def run(self, manager):
        for index, colour in enumerate(self.colour_cycle):
            if manager.interrupted:
                return
            if index > 0:
                time.sleep(2)
            print(f'turning {colour}')
            RgbLED.multi_led_phase_colour_change(self.leds, colour, manager)
            print('complete')
