import math
import random
import time

from machine import Pin
from plasma import COLOR_ORDER_BGR, WS2812

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Use the number buttons on the Pimoroni Aye Arr Remote to select between
a effects to play across a RGB LED strip connected to Plasma 2350, and
change its hue, saturation, and value using the directional buttons.

Actions:
- (1) Button [Press] = Twinkle
- (2) Button [Press] = Pulse
- (3) Button [Press] = Blink
- (0) Button [Press] = Rainbow
- OK_STOP Button [Press] = Stop
- UP Button [Press + Hold] = Increase Value
- DOWN Button [Press + Hold] = Decrease Value
- LEFT Button [Press + Hold] = Decrease Saturation
- RIGHT Button [Press + Hold] = Increase Saturation
- ANTICLOCK Button [Press + Hold] = Decrease Hue
- CLOCKWISE Button [Press + Hold] = Increase Hue

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of Plasma's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 20          # The pin to listen for IR pulses on
NUM_LEDS = 66           # The number of LEDs on the strip

HUE_STEP = 0.01         # The amount that hue will change by with each press / repeat
SAT_STEP = 0.01         # The amount that saturation will change by with each press / repeat
VAL_STEP = 0.05         # The amount that value will change by with each press / repeat

PULSE_MS = 2000         # Time in milliseconds for the pulse effect to cycle
TWINKLE_MS = 60         # Time in milliseconds between each twinkle update
BLINK_MS = 750          # Time in milliseconds between each blink update
RAINBOW_MS = 2000       # Time in milliseconds for the rainbow effect to cycle

# Variables
hue = 0
sat = 1.0
val = 1.0
blink_on = False
last_update = time.ticks_ms()
offset = 0.0

# Setup the RGB LED strip, using PIO 0 and SM 0
strip = WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
               color_order=COLOR_ORDER_BGR)


# Pulse the LEDs between off and full brightness
def pulse():
    p = (math.cos(time.ticks_ms() * math.pi / PULSE_MS) + 1) * 0.5 * val
    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, p)


# Twinkle, twinkle, little star.
def twinkle():
    global last_update
    now = time.ticks_ms()
    if time.ticks_diff(now, last_update) > TWINKLE_MS:
        for led in range(NUM_LEDS):
            strip.set_hsv(led, hue, sat, random.uniform(val - 0.4, val))
        last_update = now


# On, Off, On, Off!
def blink():
    global blink_on, last_update
    now = time.ticks_ms()
    if time.ticks_diff(now, last_update) > BLINK_MS:
        blink_on = not blink_on
        if blink_on:
            for led in range(NUM_LEDS):
                strip.set_hsv(led, hue, sat, val)
        else:
            strip.clear()
        last_update = now


# Rainbowz
def rainbow():
    global offset, last_update
    now = time.ticks_ms()
    offset = (offset + (time.ticks_diff(now, last_update) / RAINBOW_MS)) % 1.0
    for led in range(NUM_LEDS):
        led_hue = float(led) / NUM_LEDS
        strip.set_hsv(led, led_hue + offset, sat, val)
    last_update = now


# Changes the current effect.
def set_effect(e):
    global effect, last_update
    last_update = time.ticks_ms()
    strip.clear()
    effect = e
    print(f"Effect set to '{e.__name__}'")


# Function called to change the hue of the colour
def cycle_hue(amount):
    global hue
    hue = (hue + amount) % 1.0
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Function called to change the saturation of the colour
def adjust_sat(amount):
    global sat
    sat = max(min(sat + amount, 1.0), 0.0)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Function called to change the value (brightness) of the colour
def adjust_val(amount):
    global val
    val = max(min(val + amount, 1.0), 0.0)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", on_press=(set_effect, twinkle), on_repeat=None)
remote.bind("2_GREEN", on_press=(set_effect, pulse), on_repeat=None)
remote.bind("3_BLUE", on_press=(set_effect, blink), on_repeat=None)
remote.bind("0_RAINBOW", on_press=(set_effect, rainbow), on_repeat=None)
remote.bind("OK_STOP", on_press=(set_effect, None), on_repeat=None)
remote.bind("CLOCKWISE", on_press=(cycle_hue, HUE_STEP))
remote.bind("ANTICLOCK", on_press=(cycle_hue, -HUE_STEP))
remote.bind("RIGHT", on_press=(adjust_sat, SAT_STEP))
remote.bind("LEFT", on_press=(adjust_sat, -SAT_STEP))
remote.bind("UP", on_press=(adjust_val, VAL_STEP))
remote.bind("DOWN", on_press=(adjust_val, -VAL_STEP))


# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
receiver.bind(remote)

# Set the first effect that will start playing
set_effect(blink)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start()
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        receiver.decode()

        if effect:
            effect()   # Always update, for animations

# End the program by stopping any active systems
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)     # Short delay for the clear to take effect
