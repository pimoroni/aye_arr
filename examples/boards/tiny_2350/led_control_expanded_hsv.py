from pimoroni import RGBLED

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Set the colour of Tiny 2350's onboard RGB LED using the number buttons
on the Pimoroni Aye Arr Remote, and change it using the directional buttons.
This version makes use of HSV to allow for changing of colours.

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of Tiny's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 12          # The pin to listen for IR pulses on
LED_PINS = 18, 19, 20   # The pins for controlling a RGB LED

HUE_STEP = 0.1          # The amount that hue will change by with each press / repeat
SAT_STEP = 0.1          # The amount that saturation will change by with each press / repeat
VAL_STEP = 0.1          # The amount that value will change by with each press / repeat

# Colour constants (in HSV)
RED = 0 / 6, 1, 1
GREEN = 2 / 6, 1, 1
BLUE = 4 / 6, 1, 1
CYAN = 3 / 6, 1, 1
MAGENTA = 5 / 6, 1, 1
YELLOW = 1 / 6, 1, 1
WHITE = 0, 0, 1
BLACK = 0, 0, 0

# Variables
hue = 0
sat = 0
val = 0

# Setup the RGB LED
led = RGBLED(*LED_PINS)


# Function for converting HSV to RGB
def rgb_from_hsv(h, s, v):
    if s == 0.0:
        return v, v, v
    else:
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p, q, t = v * (1.0 - s), v * (1.0 - s * f), v * (1.0 - s * (1.0 - f))

        i = i % 6
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        elif i == 5:
            return v, p, q


# Function called when a colour button is pressed
def set_hsv(colour):
    global hue, sat, val
    hue, sat, val = colour

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    led.set_rgb(red, green, blue)
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Function called to change the hue of the colour
def cycle_hue(amount):
    global hue
    hue += amount % 1.0

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    led.set_rgb(red, green, blue)
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Function called to change the saturation of the colour
def adjust_sat(amount):
    global sat
    sat = max(min(sat + amount, 1.0), 0.0)

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    led.set_rgb(red, green, blue)
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Function called to change the value (brightness) of the colour
def adjust_val(amount):
    global val
    val = max(min(val + amount, 1.0), 0.0)

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    led.set_rgb(red, green, blue)
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", (set_hsv, RED))
remote.bind("2_GREEN", (set_hsv, GREEN))
remote.bind("3_BLUE", (set_hsv, BLUE))
remote.bind("4_CYAN", (set_hsv, CYAN))
remote.bind("5_MAGENTA", (set_hsv, MAGENTA))
remote.bind("6_YELLOW", (set_hsv, YELLOW))
remote.bind("8_WHITE", (set_hsv, WHITE))
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
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
