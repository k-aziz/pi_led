import time
import typing as t

from led import Colour, RgbLED
from settings import MODE_B_INTERVAL, POLL_FOR_INTERRUPT_INTERVAL, MODE_A_INTERVAL


class Mode:

    def __init__(self, leds: t.List[RgbLED], colour_cycle: t.List[Colour], active=False):
        self.leds = leds
        self.colour_cycle = colour_cycle
        self.active = active

    def run(self, manager):
        raise NotImplementedError(f"The run method has not been implemented for {self.__class__.__name__}")


class ModeManager:
    interrupted = False

    def __init__(self, modes_cycle: t.List[Mode], all_rgb_leds: t.List[RgbLED], shutdown_mode=None):
        self.modes_cycle = modes_cycle
        self.index = 0
        self.shutting_down = False
        self.shutdown_mode = shutdown_mode
        self.all_rgb_leds = all_rgb_leds

    def run(self):
        self.pulse()
        while not self.shutting_down and self.shutdown_mode:
            self.cycle_through_modes()
        else:
            self.initiate_shutdown()

    def cycle_through_modes(self):
        for mode in self.modes_cycle:
            while not self.interrupted:
                print(f"Starting {mode.__class__.__name__}")
                self.pulse()
                mode.run(self)
            else:
                self.interrupted = False
                if self.shutting_down:
                    break
                else:
                    continue

    def initiate_shutdown(self):
        if self.shutting_down and self.shutdown_mode:
            self.pulse()
            self.pulse()
            while not self.interrupted:
                self.shutdown_mode.run(self)
        self.interrupted = False

    def soft_shutdown(self):
        self.interrupted = True
        self.shutting_down = True

    def pulse(self, colour: Colour = Colour.WHITE):
        for led in self.all_rgb_leds:
            led.set_colour(Colour.BLACK)

        RgbLED.multi_led_phase_colour_change(self.all_rgb_leds, colour, self, interval=0)
        RgbLED.multi_led_phase_colour_change(self.all_rgb_leds, Colour.BLACK, self, interval=0)


class SoftShutdown(Mode):

    def __init__(self, leds: t.List[RgbLED]):
        super().__init__(leds, [])

    def run(self, manager):
        if manager.shutting_down:
            for led in self.leds:
                led.stop()
            time.sleep(3)
        time.sleep(POLL_FOR_INTERRUPT_INTERVAL)
        manager.shutting_down = False


class ModeA(Mode):
    def run(self, manager):
        while not manager.interrupted:
            for index, colour in enumerate(self.colour_cycle):
                for led in self.leds:
                    led.set_colour(colour)

                for _ in range(0, int(MODE_A_INTERVAL / POLL_FOR_INTERRUPT_INTERVAL)):
                    if manager.interrupted:
                        return
                    time.sleep(POLL_FOR_INTERRUPT_INTERVAL)


class ModeB(Mode):
    def run(self, manager):
        while not manager.interrupted:
            for index, colour in enumerate(self.colour_cycle):
                RgbLED.multi_led_phase_colour_change(self.leds, colour, manager)

                for _ in range(0, int(MODE_B_INTERVAL / POLL_FOR_INTERRUPT_INTERVAL)):
                    if manager.interrupted:
                        return
                    time.sleep(POLL_FOR_INTERRUPT_INTERVAL)
