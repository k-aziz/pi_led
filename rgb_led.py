import time
import RPi.GPIO as GPIO

from enum import Enum

LED_PIN_1 = 12
LED_PIN_2 = 11
LED_PIN_3 = 13

LED_PIN_4 = 15
LED_PIN_5 = 16
LED_PIN_6 = 18

LED_PIN_7 = 29
LED_PIN_8 = 31
LED_PIN_9 = 32

ALL_LED_PINS = (LED_PIN_1, LED_PIN_2, LED_PIN_3, LED_PIN_4, LED_PIN_5,
                LED_PIN_6, LED_PIN_7, LED_PIN_8, LED_PIN_9)
LED_COUNT = 9


class Colour(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    WHITE = (255, 255, 255)
    PURPLE = (106, 0, 255)
    ORANGE = (255, 45, 0)


class LED:
    def __init__(self, pin, colour_value):
        self.pin = pin
        self.pwm = GPIO.PWM(pin, 100)
        self.colour_value = colour_value
        self.set_brightness(self.colour_value)

    def set_brightness(self, colour_value):
        if colour_value < 0 or colour_value > 255:
            raise ValueError("colour value must be a value from 0 to 255") 

        brightness = round((100 / 255) * colour_value)
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
    def colour_value(self):
        return (
            self.red.colour_value,
            self.green.colour_value,
            self.blue.colour_value
        )

    def start(self):
        for led in self.all:
            led.pwm.start(100)
        
        self.red.set_brightness(255)
        self.green.set_brightness(255)
        self.blue.set_brightness(255)

    def stop(self):
        for led in self.all:
            led.pwm.stop()

    def phase_colour_change(self, new_colour: Colour):
        red_done = False
        green_done = False
        blue_done = False

        while not all([red_done, green_done, blue_done]):
            red_done = self.red.increment_brightness(new_colour.value[0])
            green_done = self.green.increment_brightness(new_colour.value[1])
            blue_done = self.blue.increment_brightness(new_colour.value[2])

            print(self.colour_value)
            time.sleep(0.01)

    def set_colour(self, new_colour: Colour):
        self.red.set_brightness(new_colour.value[0])
        self.green.set_brightness(new_colour.value[1])
        self.blue.set_brightness(new_colour.value[2])


def run():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ALL_LED_PINS, GPIO.OUT, initial=GPIO.HIGH)

    rgb_led_1 = setup_rgb_led(LED_PIN_1, LED_PIN_2, LED_PIN_3)
    rgb_led_2 = setup_rgb_led(LED_PIN_4, LED_PIN_5, LED_PIN_6)
    rgb_led_3 = setup_rgb_led(LED_PIN_7, LED_PIN_8, LED_PIN_9)

    try:
        rgb_led_1.start()
        rgb_led_2.start()
        rgb_led_3.start()

        while True:
            colour_cycle = (
                Colour.GREEN,
                Colour.RED,
                Colour.BLUE,
            )
            for colour in colour_cycle:
                print(f'turning {colour}')
                rgb_led_1.set_colour(colour)
                rgb_led_2.set_colour(colour)
                rgb_led_3.set_colour(colour)
                print('complete')
                time.sleep(2)

    except KeyboardInterrupt:
        rgb_led_1.stop()
        rgb_led_2.stop()
        rgb_led_3.stop()

    GPIO.cleanup()


def setup_rgb_led(red_led_pin, green_led_pin, blue_led_pin):
    red = LED(red_led_pin, 255)
    green = LED(green_led_pin, 255)
    blue = LED(blue_led_pin, 255)

    return RgbLED(red=red, green=green, blue=blue)


if __name__ == "__main__":
    run()
