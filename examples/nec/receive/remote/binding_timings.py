import time

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and have a single
button perform different actions, including timing information.

Actions:
- (5) Button [Press] = `Button Pressed!`
- (5) Button [Short Press] = `Short Press!`
- (5) Button [Hold] = `Button Held for...`
- (5) Button [Release] = `Button Released!`

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
BUTTON = "5_MAGENTA"    # The button to bind the actions to


# Functions called for each of the remote's buttons. They all include two additional
# parameters `now` and `last` that, when provided, give timing information
def press(now, last):
    # Calculate how long it was since the last button was pressed
    diff = time.ticks_diff(now, last) / 1000
    print(f"Button Pressed! Last press was {diff} seconds ago")


def short(now, last):
    # Calculate how long the current button was pressed
    diff = time.ticks_diff(now, last) / 1000
    print(f"Short Press! Was pressed for {diff} seconds")


def release(now, last):
    # Calculate how long the current button was pressed
    diff = time.ticks_diff(now, last) / 1000
    print(f"Button Released! Was pressed for {diff} seconds")


def repeat(now, last):
    # Calculate how long the current button has been held
    diff = time.ticks_diff(now, last) / 1000
    print(f"Button Held for {diff} seconds and counting")


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# Bind a separate function to each of the button's four actions
# No parameters are provided with these callbacks in this case, but adding
# `now` and `last` to any of the functions will allow them to receive timing information.
# e.g. `(func, "a")` can go to the function as `def func(a, now, last):`
remote.bind(BUTTON,
            on_press=press,
            on_short=short,
            on_release=release,
            on_repeat=repeat)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    print(f"Press ({BUTTON}) on the keypad to test button press types!")
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
    time.sleep(0.1)
