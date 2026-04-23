import json
import time

from pimoroni import RGBLED

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Set the colour of Tiny 2350's onboard RGB LED using the number buttons
on the Pimoroni Aye Arr Remote, and change it using the Red-Cyan,
Green-Magenta, and Blue-Yellow button pairs. This also plays a rainbow
effect, and includes saving and loading of settings.

Actions:
- LEFT Button [Press + Hold] = Decrease Speed
- RIGHT Button [Press + Hold] = Increase Speed
- (1)-(6) Buttons [Short Press] = Set Colour
- (7) Button [Press] = Set Warm White
- (8) Button [Press] = Set White
- (9) Button [Press] = Set Cool White
- (0) Button [Press] = Set Rainbow
- (1) Button [Hold] = Increase Red
- (4) Button [Hold] = Decrease Red
- (2) Button [Hold] = Increase Green
- (5) Button [Hold] = Decrease Green
- (3) Button [Hold] = Increase Blue
- (6) Button [Hold] = Decrease Blue
- OK_STOP Button [Press] = Toggle On/Off

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of Tiny's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 12          # The pin to listen for IR pulses on
LED_PINS = 18, 19, 20   # The pins for controlling a RGB LED
UPDATES = 50            # How many times to update the LED and effects per second
TIMESTEP = 1 / UPDATES  # The time in seconds between each update
STARTING_SPEED = 0.1    # The speed the effects will animate at initially
SPEED_MULT = 1.1        # The amount to multiply or divide the effects speed by each button press
COLOUR_STEP = 10        # The amount that a colour component will change by with each press / repeat
FILE_NAME = "last_rgb_and_speed.json"   # The file to load from and save the last settings to
R, G, B = 0, 1, 2       # Constants for indexing into the rgb list

# Color constants
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0
WARM = 255, 192, 96
WHITE = 255, 255, 255
COOL = 96, 192, 255
BLACK = 0, 0, 0


# Variables
state = True
speed = STARTING_SPEED
rgb = [100, 100, 100]
changed = True
offset = 0.0

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


# Save the latest colour and speed to file
def save():
    with open(FILE_NAME, "w") as file:
        json.dump((rgb, speed), file)


# Load the last colour and speed from file
def load():
    global rgb, speed
    try:
        with open(FILE_NAME, "r") as file:
            rgb, speed = json.load(file)
    except OSError:
        pass


# Toggle the LED on or off
def toggle_state():
    global state, changed
    state = not state
    changed = True


# Set the LED colour, and turn it on
def set_preset(colour):
    global rgb, changed, state
    rgb = [c for c in colour]
    print(f"Colour = #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
    state = True
    changed = True


# Change a colour component by an amount
def update_component(index, amount):
    global rgb, changed
    rgb[index] = max(min(rgb[index] + amount, 255), 0)
    print(f"Colour = #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
    changed = True


# Change the speed by an amount
def update_speed(amount):
    global speed, changed
    speed = max(min(speed * amount, 10), 0.01)
    print(f"Speed = {speed:.3}")
    changed = True


# Switch to playing a rainbow effect
def rainbow():
    global rgb, changed, state
    rgb = [-1, -1, -1]
    print("Rainbow Effect")
    state = True
    changed = True


# Update the LED state
def update():
    global offset
    if state:
        if -1 in rgb:
            red, green, blue = [int(x * 255) for x in rgb_from_hsv(offset, 1.0, 1.0)]
            led.set_rgb(red, green, blue)
            offset = (offset + (speed * TIMESTEP)) % 1.0
        else:
            led.set_rgb(*rgb)
    else:
        led.set_rgb(*BLACK)


# Create the remote and setup up what each of our buttons will do
remote = PimoroniRemote()
remote.bind("LEFT", (update_speed, 1 / SPEED_MULT))
remote.bind("RIGHT", (update_speed, SPEED_MULT))
remote.bind("1_RED", on_press=None, on_short=(set_preset, RED), on_repeat=(update_component, R, COLOUR_STEP))
remote.bind("4_CYAN", on_press=None, on_short=(set_preset, CYAN), on_repeat=(update_component, R, -COLOUR_STEP))
remote.bind("2_GREEN", on_press=None, on_short=(set_preset, GREEN), on_repeat=(update_component, G, COLOUR_STEP))
remote.bind("5_MAGENTA", on_press=None, on_short=(set_preset, MAGENTA), on_repeat=(update_component, G, -COLOUR_STEP))
remote.bind("3_BLUE", on_press=None, on_short=(set_preset, BLUE), on_repeat=(update_component, B, COLOUR_STEP))
remote.bind("6_YELLOW", on_press=None, on_short=(set_preset, YELLOW), on_repeat=(update_component, B, -COLOUR_STEP))
remote.bind("7_WARM", (set_preset, WARM), on_repeat=None)
remote.bind("8_WHITE", (set_preset, WHITE), on_repeat=None)
remote.bind("9_COOL", (set_preset, COOL), on_repeat=None)
remote.bind("0_RAINBOW", rainbow, on_repeat=None)
remote.bind("OK_STOP", toggle_state, on_repeat=None)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Attempt to load the last colour and speed used
load()

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
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
    led.set_rgb(*BLACK)
