import time

from aye_arr.pulse.send import PulseSender

"""
How to send a sequence of infrared pulses, as a protocol of your own.

Each entry of SEQUENCE is a burst and idle pair in microseconds. Queueing them
one after another lets the PIO send them back to back, holding the timing to the
pulse durations whatever the speed of this loop.

The sequence here is a start pulse followed by four data bits, where a long idle
is a one and a short idle is a zero.

To use this code, connect an IR LED (with a suitable resistor) to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_TX_PIN = 0           # The pin to send the IR pulses on
CARRIER_FREQ = 38000    # The carrier frequency (in hertz) the receiver expects
BURST_US = 560          # The time (in microseconds) each data burst lasts
ZERO_US = 560           # The idle (in microseconds) that marks a zero
ONE_US = 1680           # The idle (in microseconds) that marks a one
LOCKOUT_US = 9500       # A long idle, to separate one sequence from the next
SILENCE_DELAY = 1       # The time (in seconds) between each sequence

BITS = (1, 0, 1, 1)     # The data bits to send after the start pulse

# The start pulse, then one pulse per data bit, then a final burst to close it
SEQUENCE = [(9000, 4500)]
for bit in BITS:
    SEQUENCE.append((BURST_US, ONE_US if bit else ZERO_US))
SEQUENCE.append((BURST_US, LOCKOUT_US))

# Set up a PulseSender on the TX pin, using PIO 0 and SM 0
sender = PulseSender(IR_TX_PIN, 0, 0, CARRIER_FREQ)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    sender.start()

    # Loop forever
    while True:
        print(f"Sending {len(SEQUENCE)} pulses for bits {BITS}")

        # Queue every pulse, letting the PIO keep the timing between them
        for burst_us, idle_us in SEQUENCE:
            sender.send(burst_us, idle_us)

        # Wait for the whole sequence to leave the PIO
        sender.wait_for_send()

        # Have a period of silence between each sequence
        time.sleep(SILENCE_DELAY)

# End the program by stopping any active systems
finally:
    sender.stop()
