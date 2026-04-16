import time

from aye_arr.nec import NECSender
from aye_arr.nec.remotes import RemoteDescriptor

"""
An example of how to send infrared commands as if the board was a remote control, with repeats.

Repeats are used by remotes to signal that a button is being held down.
These should be sent every 108ms to match the NEC protocol spec.

To use this code, connect an IR LED (with a suitable resistor) to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 0           # The pin to send the IR pulses on
REPEATS = 5             # The number of times to send the repeat
REPEAT_DELAY = 0.108    # the time (in seconds) between each repeat.
SILENCE_DELAY = 1       # The time (in seconds) between each code send


# Create a description of the remote we are copying
class Remote(RemoteDescriptor):
    NAME = "Remote"

    ADDRESS = 0x00

    BUTTON_CODES = {
        "UP": 0x46,
        "LEFT": 0x44,
        "RIGHT": 0x43,
        "DOWN": 0x15,
        }


# Set up an NECSender on the TX pin, using PIO 0 and SM 0.
sender = NECSender(IR_TX_PIN, 0, 0)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    sender.start()

    # Loop forever
    while True:
        # Send the intended address and command once per loop
        print(f"Sending Addr 0x{Remote.ADDRESS:02x}, Cmd 0x{Remote.BUTTON_CODES['UP']:02x}")
        sender.send_remote(Remote, "UP")

        # Send repeats rather than resending the code
        for i in range(REPEATS):
            print("Sending Repeat")
            time.sleep(REPEAT_DELAY)
            sender.send_repeat()

        # Have a period of silence between each send
        time.sleep(SILENCE_DELAY)

# End the program by stopping any active systems
finally:
    sender.stop()
