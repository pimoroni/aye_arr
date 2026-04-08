import math
import random
import time

import plasma
from machine import Pin

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

UPDATES = 50
NUM_LEDS = 66
INV_UPDATES = 1 / UPDATES

hue = 1.0
saturation = 1.0
brightness = 1.0

# WS2812 / NeoPixel™ LEDs
strip = plasma.WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
                      color_order=plasma.COLOR_ORDER_BGR)


def pulse():
    p = abs(math.cos(time.ticks_ms() / 500))
    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, saturation, p)


def twinkle():
    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, saturation, random.uniform(brightness - 0.4, brightness))

    time.sleep(0.1)


blink_on = False


def blink():
    global blink_on
    for led in range(NUM_LEDS):
        if blink_on:
            strip.set_hsv(led, hue, saturation, brightness)
        else:
            strip.clear()

    time.sleep(0.5)
    blink_on = not blink_on


def rainbow():

    offset = abs(math.sin(time.ticks_ms() / 2000))

    for led in range(NUM_LEDS):
        hue = float(led) / NUM_LEDS
        strip.set_hsv(led, hue + offset, saturation, brightness)


position = 0


def set_effect(e, ms, v):
    global effect
    strip.clear()
    effect = e


def update_hue(h, ms, v):
    global hue
    hue += h
    hue %= 1.0


def update_saturation(s, ms, v):
    global saturation
    saturation += s
    saturation = min(max(saturation, 0.0), 1.0)


def update_brightness(b, ms, v):
    global brightness
    brightness += b
    brightness = min(max(brightness, 0.0), 1.0)


remote = PimoroniRemote()
remote.bind("1/RED", on_press=None, on_short=(set_effect, twinkle))
remote.bind("2/GREEN", on_press=None, on_short=(set_effect, pulse))
remote.bind("3/BLUE", on_press=None, on_short=(set_effect, blink))

remote.bind("0/RAINBOW", on_press=None, on_short=(set_effect, rainbow))
remote.bind("OK/STOP", on_press=None, on_short=(set_effect, None))

remote.bind("CLOCKWISE", on_press=(update_hue, 0.01))
remote.bind("ANTICLOCK", on_press=(update_hue, -0.01))
remote.bind("UP", on_press=(update_brightness, 0.05))
remote.bind("DOWN", on_press=(update_brightness, -0.05))
remote.bind("RIGHT", on_press=(update_saturation, 0.01))
remote.bind("LEFT", on_press=(update_saturation, -0.01))

receiver = NECRemoteReceiver(20, 1, 0)
receiver.bind(remote)

effect = blink

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start(UPDATES)    # Start updating the LED strip
    receiver.start()

    # Loop until the effect stops or the "Boot" button is pressed
    while True:
        receiver.decode()   # Add exception if this is called but start hasn't been called, or is in a stopped state

        if effect:
            effect()   # Always update, for animations
        time.sleep(INV_UPDATES)

# Stop any running effects and turn off the LED strip
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)
