import json
import time

from machine import Pin
from plasma import COLOR_ORDER_BGR, WS2812

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
An example for the Plasma2350 and IR Stick (Connected to the QW/sT).
Buttons:

Long Press/Hold:
1-4 = Increase/Decrease the Red channel
2-5 = Increase/Decrease the Green channel
3-6 = Increase/Decrease the Blue channel

Short Press (numpad):
Sets the LEDs to the colour shown on the remote.

OK/Stop:
Reduce all channels to zero

"""

# Constants
IR_RX_PIN = 20          # The pin to listen for IR pulses on
NUM_LEDS = 66           # The number of LEDs on the strip
UPDATES = 50            # How many times to update the strip and effects per second
TIMESTEP = 1 / UPDATES  # The time in seconds between each update
STARTING_SPEED = 0.1    # The speed the effects will animate at initially
SPEED_MULT = 1.1        # The amount to multiply or divide the effects speed by each button press
COLOUR_STEP = 10        # The amount that a colour component will change by with each press / repeat

# Color constants
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0
WARM_WHITE = 255, 192, 96
WHITE = 255, 255, 255
COOL_WHITE = 96, 192, 255
BLACK = 0, 0, 0


# Variables
state = True
speed = STARTING_SPEED
rgb = [100, 100, 100]
changed = True
offset = 0.0

# Setup Plasma 2350's "A" button
boot = Pin.board.BUTTON_A
boot.init(Pin.IN, Pin.PULL_UP)

# Setup the RGB LED strip
strip = WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
               color_order=COLOR_ORDER_BGR)


# Save the latest colour and speed to file
def save():
    with open('last_colour.json', 'w') as file:
        json.dump((rgb, speed), file)


# Load the last colour and speed from file
def load():
    global rgb, speed
    try:
        with open('last_colour.json', 'r') as file:
            rgb, speed = json.load(file)
    except OSError:
        pass


# Toggle the LED strip on or off
def toggle_state():
    global state, changed
    state = not state
    changed = True


# Set the LED strip colour, and turn it on
def set_preset(colour):
    global rgb, changed, state
    rgb = [c for c in colour]
    print(f"Colour = #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
    state = True
    changed = True


# Increase or decrease
def update_component(value, index):
    global rgb, changed
    rgb[index] = max(min(rgb[index] + value, 255), 0)
    print(f"Colour = #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
    changed = True


def update_speed(value):
    global speed, changed
    speed = max(min(speed * value, 10), 0.01)
    print(f"Speed = {speed:.3}")
    changed = True


def rainbow():
    global rgb, changed, state
    rgb = [-1, -1, -1]
    print("Rainbow Effect")
    state = True
    changed = True


def update():
    global offset
    if state:
        if -1 in rgb:
            for led in range(NUM_LEDS):
                hue = float(led) / NUM_LEDS
                strip.set_hsv(led, hue + offset, 1.0, 1.0)

            offset = (offset + (speed * TIMESTEP)) % 1.0
        else:
            for led in range(NUM_LEDS):
                strip.set_rgb(led, *rgb)
    else:
        for led in range(NUM_LEDS):
            strip.set_rgb(led, *BLACK)


# Create the remote and setup up what each of our buttons will do
remote = PimoroniRemote()
remote.bind("LEFT", (update_speed, 1 / SPEED_MULT))
remote.bind("RIGHT", (update_speed, SPEED_MULT))
remote.bind("1_RED", on_press=None, on_short=(set_preset, RED), on_repeat=(update_component, COLOUR_STEP, 0))
remote.bind("4_CYAN", on_press=None, on_short=(set_preset, CYAN), on_repeat=(update_component, -COLOUR_STEP, 0))
remote.bind("2_GREEN", on_press=None, on_short=(set_preset, GREEN), on_repeat=(update_component, COLOUR_STEP, 1))
remote.bind("5_MAGENTA", on_press=None, on_short=(set_preset, MAGENTA), on_repeat=(update_component, -COLOUR_STEP, 1))
remote.bind("3_BLUE", on_press=None, on_short=(set_preset, BLUE), on_repeat=(update_component, COLOUR_STEP, 2))
remote.bind("6_YELLOW", on_press=None, on_short=(set_preset, YELLOW), on_repeat=(update_component, -COLOUR_STEP, 2))
remote.bind("7_WARM", (set_preset, WARM_WHITE), on_repeat=None)
remote.bind("8_WHITE", (set_preset, WHITE), on_repeat=None)
remote.bind("9_COOL", (set_preset, COOL_WHITE), on_repeat=None)
remote.bind("OK_STOP", toggle_state, on_repeat=None)
remote.bind("0_RAINBOW", rainbow, on_repeat=None)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Attempt to load the last colour and speed used
load()

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start(UPDATES)    # Start updating the LED strip
    receiver.start()

    # Loop until the "A" button is pressed
    while boot.value():
        # Decode any IR pulses received since the last time this was called.
        receiver.decode()

        # Save the latest colour and speed if there has been a change
        if changed:
            save()
            changed = False

        update()   # Always update, for animations
        time.sleep(TIMESTEP)

# End the program by stopping any active systems
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)     # Short delay for the clear to take effect
