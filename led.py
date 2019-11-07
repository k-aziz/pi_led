import time
import typing as t
from collections import namedtuple
from enum import Enum

import RPi.GPIO as GPIO

RGB = namedtuple('RGB', 'red green blue')


class Colour(Enum):
    RED = RGB(255, 0, 0)
    GREEN = RGB(0, 255, 0)
    BLUE = RGB(0, 0, 255)

    YELLOW = RGB(255, 255, 0)
    CYAN = RGB(0, 255, 255)
    MAGENTA = RGB(255, 0, 255)

    WHITE = RGB(255, 255, 255)
    PURPLE = RGB(106, 0, 255)
    ORANGE = RGB(255, 45, 0)


class LED:
    def __init__(self, pin, colour_value):
        self.pin = pin
        self.pwm = GPIO.PWM(pin, 100)
        self.colour_value = colour_value
        self.set_brightness(self.colour_value)

    def set_brightness(self, colour_value):
        if colour_value < 0 or colour_value > 255:
            raise ValueError("Colour value must be a value from 0 to 255")

        brightness = round((100 / 255) * colour_value)
        self.colour_value = colour_value
        # for common anode rgb the brightness must be inverted
        self.pwm.ChangeDutyCycle(100 - brightness)

    def increment_brightness(self, new_brightness):
        done = False
        if self.colour_value < new_brightness:
            self.colour_value += 1
            self.set_brightness(self.colour_value)
        elif self.colour_value > new_brightness:
            self.colour_value -= 1
            self.set_brightness(self.colour_value)
        else:
            done = True

        return done


class RgbLED:
    def __init__(self, *, red: LED, green: LED, blue: LED):
        self.red = red
        self.green = green
        self.blue = blue
        self.all = (self.red, self.green, self.blue)

    @property
    def colour_value(self) -> t.Tuple:
        return (
            self.red.colour_value,
            self.green.colour_value,
            self.blue.colour_value
        )

    @staticmethod
    def setup(red_led_pin: int, green_led_pin: int, blue_led_pin: int) -> 'RgbLED':
        red = LED(red_led_pin, 255)
        green = LED(green_led_pin, 255)
        blue = LED(blue_led_pin, 255)

        return RgbLED(red=red, green=green, blue=blue)

    def start(self):
        for led in self.all:
            led.pwm.start(100)

        self.red.set_brightness(255)
        self.green.set_brightness(255)
        self.blue.set_brightness(255)

    def stop(self):
        for led in self.all:
            led.pwm.stop()

    def single_led_phase_colour_change(self, new_colour: Colour) -> None:
        red_done = False
        green_done = False
        blue_done = False

        while not all([red_done, green_done, blue_done]):
            red_done = self.red.increment_brightness(new_colour.value.red)
            green_done = self.green.increment_brightness(new_colour.value.green)
            blue_done = self.blue.increment_brightness(new_colour.value.blue)

            print(self.colour_value)
            time.sleep(0.01)

    @staticmethod
    def multi_led_phase_colour_change(all_rgb_leds: t.List['RgbLED'], new_colour: Colour, manager) -> None:
        all_red_done = False
        all_green_done = False
        all_blue_done = False

        led_done_statuses = {}
        for led in all_rgb_leds:
            led_done_statuses[id(led)] = {
                'red_done': False,
                'blue_done': False,
                'green_done': False
            }

        while not all([all_red_done, all_green_done, all_blue_done]):
            for led in all_rgb_leds:
                if manager.interrupted:
                    return
                led_done_statuses[id(led)]['red_done'] = led.red.increment_brightness(new_colour.value.red)
                led_done_statuses[id(led)]['green_done'] = led.green.increment_brightness(new_colour.value.green)
                led_done_statuses[id(led)]['blue_done'] = led.blue.increment_brightness(new_colour.value.blue)

                all_red_done = all([led_done_statuses[led_id]['red_done'] for led_id in led_done_statuses])
                all_green_done = all([led_done_statuses[led_id]['green_done'] for led_id in led_done_statuses])
                all_blue_done = all([led_done_statuses[led_id]['blue_done'] for led_id in led_done_statuses])

            time.sleep(0.05)

    def set_colour(self, new_colour: Colour) -> None:
        self.red.set_brightness(new_colour.value.red)
        self.green.set_brightness(new_colour.value.green)
        self.blue.set_brightness(new_colour.value.blue)
