import time
import RPi.GPIO as GPIO

LED_PIN_1 = 12
LED_PIN_2 = 11
LED_PIN_3 = 13

ALL_LEDS = [LED_PIN_1, LED_PIN_2, LED_PIN_3]
LED_COUNT = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ALL_LEDS , GPIO.OUT)

p1 = GPIO.PWM(LED_PIN_1, 100)  # channel=12 frequency=50Hz
p2 = GPIO.PWM(LED_PIN_2, 100)  # channel=12 frequency=50Hz
p3 = GPIO.PWM(LED_PIN_3, 100)  # channel=12 frequency=50Hz

ALL_LED_PWDS = [p1, p2, p3]

for x in ALL_LED_PWDS:
    x.start(100)

MAX_DC = 100
MIN_DC = 99 

def calc_dc(x):
    val = x
    if x > MAX_DC:
        val = MAX_DC - (x - MAX_DC)
        if val < 0:
            val = abs(val)
    return val

START_DC_1 = 80
START_DC_2 = 30 
START_DC_3 = 0 

try:
    while True:
        for dc in range(MAX_DC * 2):
            p1.ChangeDutyCycle(calc_dc(START_DC_1 + dc))
            p2.ChangeDutyCycle(calc_dc(START_DC_2 + dc))
            print(calc_dc(START_DC_3 + dc))
            p3.ChangeDutyCycle(calc_dc(START_DC_3 + dc))
            time.sleep(0.05)
except KeyboardInterrupt:
    pass

for x in ALL_LED_PWDS:
    x.stop()
GPIO.cleanup()

