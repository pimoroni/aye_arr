import math
import random
import time

from machine import Pin
from plasma import COLOR_ORDER_BGR, WS2812

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Constants
IR_RX_PIN = 20          # The pin to listen for IR pulses on
NUM_LEDS = 66           # The number of LEDs on the strip
UPDATES = 50            # How many times to update the strip and effects per second
TIMESTEP = 1 / UPDATES  # The time in seconds between each update

HUE_STEP = 0.01         # The amount that hue will change by with each press / repeat
SAT_STEP = 0.01         # The amount that saturation will change by with each press / repeat
VAL_STEP = 0.05         # The amount that value will change by with each press / repeat

# Variables
hue = 1.0
sat = 1.0
val = 1.0
blink_on = False

# Setup the RGB LED strip
strip = WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
               color_order=COLOR_ORDER_BGR)


def pulse():
    p = abs(math.cos(time.ticks_ms() / 500))
    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, p)


def twinkle():
    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, random.uniform(val - 0.4, val))

    time.sleep(0.1)


def blink():
    global blink_on
    if blink_on:
        for led in range(NUM_LEDS):
            strip.set_hsv(led, hue, sat, val)
    else:
        strip.clear()

    time.sleep(0.5)
    blink_on = not blink_on


def rainbow():
    offset = abs(math.sin(time.ticks_ms() / 2000))

    for led in range(NUM_LEDS):
        hue = float(led) / NUM_LEDS
        strip.set_hsv(led, hue + offset, sat, val)


def set_effect(e):
    global effect
    strip.clear()
    effect = e


def update_hue(h):
    global hue
    hue += h
    hue %= 1.0


def update_sat(s):
    global sat
    sat += s
    sat = min(max(sat, 0.0), 1.0)


def update_val(b):
    global val
    val += b
    val = min(max(val, 0.0), 1.0)


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", on_press=None, on_short=(set_effect, twinkle))
remote.bind("2_GREEN", on_press=None, on_short=(set_effect, pulse))
remote.bind("3_BLUE", on_press=None, on_short=(set_effect, blink))

remote.bind("0_RAINBOW", on_press=None, on_short=(set_effect, rainbow))
remote.bind("OK_STOP", on_press=None, on_short=(set_effect, None))

remote.bind("CLOCKWISE", on_press=(update_hue, HUE_STEP))
remote.bind("ANTICLOCK", on_press=(update_hue, -HUE_STEP))
remote.bind("RIGHT", on_press=(update_sat, SAT_STEP))
remote.bind("LEFT", on_press=(update_sat, -SAT_STEP))
remote.bind("UP", on_press=(update_val, VAL_STEP))
remote.bind("DOWN", on_press=(update_val, -VAL_STEP))


# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
receiver.bind(remote)

# Set the first effect that will start playing
effect = blink

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start(UPDATES)
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        receiver.decode()

        if effect:
            effect()   # Always update, for animations
        time.sleep(TIMESTEP)

# End the program by stopping any active systems
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)     # Short delay for the clear to take effect
