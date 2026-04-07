import time
import plasma
import json
from machine import Pin
from aye_arr.nec.remotes import PimoroniRemote
from aye_arr.nec import NECRemoteReceiver


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


class State:
    OFF = 0
    ON = 1


state = State.ON

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

# Constants
NUM_LEDS = 68        # How many LEDs are on the connected Strip
UPDATES = 50        # How many times the LEDs and effects updated per second
INV_UPDATES = 1 / UPDATES
SPEED_MULT = 1.1


speed = 0.1        # The speed to cycle the rainbow at, with 1.0 being 1 second


# Colour Values
rgb = [100, 100, 100]
increment = 10


# Variables
boot = Pin.board.BUTTON_A
boot.init(Pin.IN, Pin.PULL_UP)

# WS2812 / NeoPixel™ LEDs
strip = plasma.WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
                      color_order=plasma.COLOR_ORDER_BGR)

changed = True
offset = 0.0


def save():
    with open('last_colour.json', 'w') as file:
        json.dump((rgb, speed), file)


def load():
    global rgb
    try:
        with open('last_colour.json', 'r') as file:
            rgb, speed = json.load(file)
    except OSError:
        pass


def toggle_state(ms, v):
    global state, changed
    state = not state
    changed = True


def set_preset(color, ms, v):
    global rgb, changed, state
    rgb = [c for c in color]
    state = State.ON
    changed = True


def update_red(value, ms, v):
    global rgb, changed
    rgb[0] = max(min(rgb[0] + value, 255), 0)
    changed = True


def update_green(value, ms, v):
    global rgb, changed
    rgb[1] = max(min(rgb[1] + value, 255), 0)
    changed = True


def update_blue(value, ms, v):
    global rgb, changed
    rgb[2] = max(min(rgb[2] + value, 255), 0)
    changed = True


def update_speed(value, ms, v):
    global speed, changed
    speed = max(min(speed * value, 10), 0.01)
    changed = True


def rainbow(ms, v):
    global rgb, changed, state
    rgb = [-1, -1, -1]
    state = State.ON
    changed = True


def update():
    global offset
    if state == State.ON:
        if -1 in rgb:
            for led in range(NUM_LEDS):
                hue = float(led) / NUM_LEDS
                strip.set_hsv(led, hue + offset, 1.0, 1.0)

            offset = (offset + (speed * INV_UPDATES)) % 1.0
        else:
            for led in range(NUM_LEDS):
                strip.set_rgb(led, *rgb)
    else:
        for led in range(NUM_LEDS):
            strip.set_rgb(led, *BLACK)


# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
remote.bind("LEFT", (update_speed, 1 / SPEED_MULT))
remote.bind("RIGHT", (update_speed, SPEED_MULT))
remote.bind("1/RED", on_press=None, on_short=(set_preset, RED), on_repeat=(update_red, increment))
remote.bind("4/CYAN", on_press=None, on_short=(set_preset, CYAN), on_repeat=(update_red, -increment))
remote.bind("2/GREEN", on_press=None, on_short=(set_preset, GREEN), on_repeat=(update_green, increment))
remote.bind("5/MAGENTA", on_press=None, on_short=(set_preset, MAGENTA), on_repeat=(update_green, -increment))
remote.bind("3/BLUE", on_press=None, on_short=(set_preset, BLUE), on_repeat=(update_blue, increment))
remote.bind("6/YELLOW", on_press=None, on_short=(set_preset, YELLOW), on_repeat=(update_blue, -increment))
remote.bind("7/WARM", (set_preset, WARM_WHITE))
remote.bind("8/WHITE", (set_preset, WHITE))
remote.bind("9/COOL", (set_preset, COOL_WHITE))
remote.bind("OK/STOP", on_press=None, on_short=toggle_state)
remote.bind("0/RAINBOW", rainbow)

receiver = NECRemoteReceiver(20, 1, 0)
receiver.bind(remote)

# Attempt to load the last colour used
load()

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start(UPDATES)    # Start updating the LED strip
    receiver.start()

    # Loop until the effect stops or the "Boot" button is pressed
    while boot.value():
        receiver.decode()   # Add exception if this is called but start hasn't been called, or is in a stopped state

        if changed:
            save()
            changed = False

        update()   # Always update, for animations
        time.sleep(INV_UPDATES)

# Stop any running effects and turn off the LED strip
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)
