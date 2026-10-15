from aye_arr.pulse.receive import DEFAULT_FILTER_THRESHOLD_US, PulseReceiver

"""
How the pulse filter changes what a sequence looks like.

`decode` runs a low-pass filter that merges any burst or idle shorter than its
threshold into the pulse beside it, recovering data that a stray blip would
otherwise spoil. `decode_no_filter` reports the pulses as they arrived.

Set USE_FILTER to compare the two against the same remote. An unfiltered
sequence from a noisy receiver holds more pulses than the protocol expects.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
USE_FILTER = True       # Whether to filter blips out of the received pulses

# The shortest burst or idle to keep, in microseconds. Raising it merges longer blips
FILTER_THRESHOLD_US = DEFAULT_FILTER_THRESHOLD_US


class PulseCounter(PulseReceiver):

    # Called with each sequence of pulses received, once the receiver goes quiet
    def __analyse(self, pulses):
        # Gather every burst and idle, to report the shortest received
        durations = []
        for pulse in pulses:
            durations.append(pulse.burst)
            durations.append(pulse.idle)

        shortest = min(durations) if len(durations) > 0 else 0
        print(f"{len(pulses)} pulses, shortest burst or idle {shortest}us")


# Set up the receiver on the RX pin, using PIO 1 and SM 0
receiver = PulseCounter(IR_RX_PIN, 1, 0)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()
    print(f"Filtering {'on' if USE_FILTER else 'off'}")

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called
        if USE_FILTER:
            receiver.decode(FILTER_THRESHOLD_US)
        else:
            receiver.decode_no_filter()

# End the program by stopping any active systems
finally:
    receiver.stop()
