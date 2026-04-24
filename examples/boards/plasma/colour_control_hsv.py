import time

from machine import Pin
from plasma import COLOR_ORDER_BGR, WS2812

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Set the colour of a RGB LED strip connected to Plasma 2350 using the
number buttons on the Pimoroni Aye Arr Remote, and change its hue,
saturation, and value using the directional buttons.

Actions:
- (1)-(9) Button [Press + Hold] = Set Colour
- OK_STOP Button [Press + Hold] = Set Black
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

# Colour constants (in HSV)
RED = 0 / 6, 1, 1
GREEN = 2 / 6, 1, 1
BLUE = 4 / 6, 1, 1
CYAN = 3 / 6, 1, 1
MAGENTA = 5 / 6, 1, 1
YELLOW = 1 / 6, 1, 1
WARM = 0.1, 0.624, 1
WHITE = 0, 0, 1
COOL = 0.56, 0.624, 1
BLACK = 0, 0, 0

# Variables
hue = 0
sat = 0
val = 0

# Setup the RGB LED strip, using PIO 0 and SM 0
strip = WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
               color_order=COLOR_ORDER_BGR)


# Function called when a colour button is pressed
def set_hsv(colour):
    global hue, sat, val
    hue, sat, val = colour

    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, val)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Function called to change the hue of the colour
def cycle_hue(amount):
    global hue
    hue = (hue + amount) % 1.0

    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, val)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Function called to change the saturation of the colour
def adjust_sat(amount):
    global sat
    sat = max(min(sat + amount, 1.0), 0.0)

    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, val)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Function called to change the value (brightness) of the colour
def adjust_val(amount):
    global val
    val = max(min(val + amount, 1.0), 0.0)

    for led in range(NUM_LEDS):
        strip.set_hsv(led, hue, sat, val)
    print(f"H = {hue:.2}, S = {sat:.2}, V = {val:.2}")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", (set_hsv, RED))
remote.bind("2_GREEN", (set_hsv, GREEN))
remote.bind("3_BLUE", (set_hsv, BLUE))
remote.bind("4_CYAN", (set_hsv, CYAN))
remote.bind("5_MAGENTA", (set_hsv, MAGENTA))
remote.bind("6_YELLOW", (set_hsv, YELLOW))
remote.bind("7_WARM", (set_hsv, WARM))
remote.bind("8_WHITE", (set_hsv, WHITE))
remote.bind("9_COOL", (set_hsv, COOL))
remote.bind("OK_STOP", (set_hsv, BLACK))
remote.bind("CLOCKWISE", (cycle_hue, HUE_STEP))
remote.bind("ANTICLOCK", (cycle_hue, -HUE_STEP))
remote.bind("RIGHT", (adjust_sat, SAT_STEP))
remote.bind("LEFT", (adjust_sat, -SAT_STEP))
remote.bind("UP", (adjust_val, VAL_STEP))
remote.bind("DOWN", (adjust_val, -VAL_STEP))

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start()
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)     # Short delay for the clear to take effect
