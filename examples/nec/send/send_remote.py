import time

from aye_arr.nec import NECSender
from aye_arr.nec.remotes import RemoteDescriptor

"""
An example of how to send infrared commands as if the board was a remote control.

The chosen command is sent to the address multiple times in bursts,
followed by a period of silence. The number of commands per burst,
as well as the burst and silence timings can be adjusted.

To use this code, connect an IR LED (with a suitable resistor) to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 0           # The pin to send the IR pulses on
BURSTS = 5              # The number of times to send the code in quick succession
BURST_DELAY = 0.01      # The time (in seconds) between each code send
SILENCE_DELAY = 1       # The time (in seconds) between each burst


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
        # Send the intended address and command several times to help it be detected
        print(f"Sending Addr 0x{Remote.ADDRESS:02x}, Cmd 0x{Remote.BUTTON_CODES['UP']:02x} {BURSTS}x times")
        for i in range(BURSTS):
            sender.send_remote(Remote, "UP")
            time.sleep(BURST_DELAY)

        # Have a period of silence between each burst
        time.sleep(SILENCE_DELAY)

# End the program by stopping any active systems
finally:
    sender.stop()
