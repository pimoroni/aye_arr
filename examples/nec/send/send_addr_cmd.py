import time
from aye_arr.nec import NECSender

"""
An example of how to send an infrared command to an address.

In it the chosen command is sent to the address multiple times in
bursts, followed by a period of silence. The number of codes per
burst, as well as the burst and silence timings can be adjusted.

An IR LED (with a suitable resistor) should be connected to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 20          # The pin to send the IR pulses on
ADDRESS = 0x00          # The 8-bit address to send the command to
COMMAND = 0x46          # The 8-bit command to send to the address
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
        # Send the intended address and command several times to help it be detected
        print(f"Sending Addr 0x{ADDRESS:02x}, Cmd 0x{COMMAND:02x}")
        for i in range(BURSTS):
            sender.send_addr_cmd(ADDRESS, COMMAND)
            time.sleep(BURST_DELAY)

        # Have a period of silence between each burst
        time.sleep(SILENCE_DELAY)

finally:
    sender.stop()
