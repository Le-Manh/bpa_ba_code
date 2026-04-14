import time
from arduino.app_utils import App
from arduino.app_utils import Bridge
from arduino.app_utils import Leds # let the LED blink so we know something is happening
import csv

def envlope_read(envlope: int):
    print(envlope)
    with open('test.txt',mode='w', encoding='UTF8') as file:
        file.write(str(envlope))

def loop():
    # Blink LED 1 in red
    # Turn on the LED red segment(1, 0, 0)
    Leds.set_led1_color(1,0,0)
    time.sleep(1)

    # Turn off the LED (0, 0, 0)
    Leds.set_led1_color(0,0,0)
    time.sleep(1)
    Bridge.provide("envlope_read", envlope_read)

App.run(user_loop=loop)