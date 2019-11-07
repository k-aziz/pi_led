import subprocess
import time

import RPi.GPIO as GPIO

from led import Colour, RgbLED
from mode import ModeManager, ModeA, ModeB
from timer import MyTimer

BUTTON_PIN = 5

LED_PIN_1 = 12
LED_PIN_2 = 11
LED_PIN_3 = 13

LED_PIN_4 = 15
LED_PIN_5 = 16
LED_PIN_6 = 18

LED_PIN_7 = 29
LED_PIN_8 = 31
LED_PIN_9 = 32

ALL_LED_PINS = (LED_PIN_1, LED_PIN_2, LED_PIN_3,
                LED_PIN_4, LED_PIN_5, LED_PIN_6,
                LED_PIN_7, LED_PIN_8, LED_PIN_9)


def start():
    try:
        for led in all_rgb_leds:
            led.start()
        mode_manager.run()
    except KeyboardInterrupt:
        for led in all_rgb_leds:
            led.stop()

    print("\n\nExiting...")
    GPIO.cleanup()


def shutdown():
    print("Shutting down...")
    subprocess.run(['sudo', 'shutdown', '-h', 'now'])


def edge_detected(pin):
    if not GPIO.input(pin):
        shutdown_timer.start()
        print("Button down")
    else:
        shutdown_timer.cancel()
        print("Button up")
        mode_manager.interrupted = True

    time.sleep(0.2)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ALL_LED_PINS, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(BUTTON_PIN, GPIO.IN)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=edge_detected, bouncetime=100)

    rgb_led_1 = RgbLED.setup(LED_PIN_1, LED_PIN_2, LED_PIN_3)
    rgb_led_2 = RgbLED.setup(LED_PIN_4, LED_PIN_5, LED_PIN_6)
    rgb_led_3 = RgbLED.setup(LED_PIN_7, LED_PIN_8, LED_PIN_9)

    all_rgb_leds = [rgb_led_1, rgb_led_2, rgb_led_3]

    mode_a = ModeA(all_rgb_leds, colour_cycle=[Colour.RED, Colour.GREEN, Colour.BLUE])
    mode_b = ModeB(all_rgb_leds, colour_cycle=[Colour.PURPLE, Colour.CYAN, Colour.MAGENTA])

    shutdown_timer = MyTimer(3, shutdown)
    mode_manager = ModeManager([mode_a, mode_b])
    start()
