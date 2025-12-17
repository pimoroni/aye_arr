import time
from aye_arr.nec import NECSender

"""
A barebones example of how to send an infrared code.

In it the chosen code is sent multiple times in bursts, followed
by a period of silence. The number of codes per burst, as well as
the burst and silence timings can be adjusted.

An IR LED (with a suitable resistor) should be connected to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 20          # The pin to send the IR pulses on
CODE = 0x0046           # The 16-bit code to send
BURSTS = 5              # The number of times to send the code in quick succession
BURST_DELAY = 0.01      # The time (in seconds) between each code send
SILENCE_DELAY = 1       # The time (in seconds) between each burst

# Set up an NECSender on the TX pin, using PIO 0 and SM 0.
sender = NECSender(IR_TX_PIN, 0, 0)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    sender.start()

    # Loop forever
    while True:
        # Send the intended code several times to help it be detected
        print(f"Sending Code 0x{CODE:04x}")
        for i in range(BURSTS):
            sender.send_code(CODE)
            time.sleep(BURST_DELAY)

        # Have a period of silence between each burst
        time.sleep(SILENCE_DELAY)

# End the program by stopping any active systems
finally:
    sender.stop()
