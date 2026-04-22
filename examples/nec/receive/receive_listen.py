import aye_arr.logging as logging
from aye_arr.nec import NECReceiver

"""
An example of how to listen for any NEC infrared signals.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on

# Set up a receiver on the RX pin, using PIO 1 and SM 0.
# The logging_level is increased from LOG_WARN (the default) to show any codes received
receiver = NECReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_INFO)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
