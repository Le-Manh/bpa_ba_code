import time
from arduino.app_utils import App
from arduino.app_utils import Leds

def loop():
    # Blink LED 1 in red
    # Turn on the LED red segment(1, 0, 0)
    Leds.set_led1_color(1,0,0)
    time.sleep(1)

    # Turn off the LED (0, 0, 0)
    Leds.set_led1_color(0,0,0)
    time.sleep(1)

App.run(user_loop=loop)