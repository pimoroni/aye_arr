import time

from aye_arr.pulse.send import PulseSender

"""
A barebones example of how to send an infrared pulse.

A pulse is a burst of the carrier frequency followed by a period of idle. Both
durations are given in microseconds. The pulse is sent repeatedly, with a period
of silence between each one.

To use this code, connect an IR LED (with a suitable resistor) to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 0           # The pin to send the IR pulses on
CARRIER_FREQ = 38000    # The carrier frequency (in hertz) the receiver expects
BURST_US = 9000         # The time (in microseconds) to emit the carrier for
IDLE_US = 4500          # The time (in microseconds) to stay silent for
SILENCE_DELAY = 1       # The time (in seconds) between each pulse

# Set up a PulseSender on the TX pin, using PIO 0 and SM 0
sender = PulseSender(IR_TX_PIN, 0, 0, CARRIER_FREQ)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    sender.start()

    # Loop forever
    while True:
        print(f"Sending a {BURST_US}us burst, then {IDLE_US}us of idle")
        sender.send(BURST_US, IDLE_US)

        # Wait for the pulse to leave the PIO before timing the next one
        sender.wait_for_send()

        # Have a period of silence between each pulse
        time.sleep(SILENCE_DELAY)

# End the program by stopping any active systems
finally:
    sender.stop()
