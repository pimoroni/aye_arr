import time

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and use them to
enter a "channel" number into the system. Each number button on the
remote adds a digit to the current number.

Actions:
- (0)-(9) Button [Press] = Enter digit

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
TIMEOUT_MS = 800        # The time after a number is pressed before the channel is output

# Variables
number = ""             # The current number being populated, as a string
last_press = time.ticks_ms()


# Functions called for each of the remote's number buttons
# For this use, two additional parameters are passed in;
# the current time and the last time a button was pressed (the latter is not used here)
def append_number(num, now, _):
    global number, last_press
    print(str(num), end="")
    number += str(num)
    last_press = now


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# Bind functions to each of the Pimoroni remote's number buttons in a loop.
for button, num in remote.NUMBERS.items():
    remote.bind(button, (append_number, num), on_repeat=None)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

        # If a number button has not been pressed for a while, output the channel
        if time.ticks_diff(time.ticks_ms(), last_press) >= TIMEOUT_MS and len(number) > 0:
            print("\nChannel:", number)
            number = ""

# End the program by stopping any active systems
finally:
    receiver.stop()
