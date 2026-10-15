from aye_arr.pulse.receive import PulseReceiver

"""
An example of how to read raw infrared pulses.

PulseReceiver gathers pulses until the receiver goes quiet, then hands the whole
sequence to its `__analyse` function. Subclass it and define your own to act on
them, as the NEC layer does.

Each pulse gives the burst and idle durations in microseconds.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
SHOW_PULSES = 4         # The number of pulses to print from each sequence


class PulsePrinter(PulseReceiver):

    # Called with each sequence of pulses received, once the receiver goes quiet
    def __analyse(self, pulses):
        print(f"Received {len(pulses)} pulses")
        for pulse in pulses[:SHOW_PULSES]:
            print(f"  burst {pulse.burst}us, idle {pulse.idle}us")
        if len(pulses) > SHOW_PULSES:
            print(f"  ... and {len(pulses) - SHOW_PULSES} more")


# Set up the receiver on the RX pin, using PIO 1 and SM 0
receiver = PulsePrinter(IR_RX_PIN, 1, 0)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid pulses queuing up
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
