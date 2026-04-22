import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and perform
individual actions for the ones we are interested in, via separate functions.

Actions:
- UP Button [Press + Hold] = `up received`
- DOWN Button [Press + Hold] = `down received`
- LEFT Button [Press + Hold] = `left received`
- RIGHT Button [Press + Hold] = `right received`

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Functions called for each of the remote's buttons
def up():
    print("up received")


def left():
    print("left received")


def right():
    print("right received")


def down():
    print("down received")


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# Bind a unique function to each of the directional buttons
remote.bind("UP", up)
remote.bind("LEFT", left)
remote.bind("RIGHT", right)
remote.bind("DOWN", down)

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

# End the program by stopping any active systems
finally:
    receiver.stop()
