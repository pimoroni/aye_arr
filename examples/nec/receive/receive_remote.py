import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import RemoteDescriptor

"""
Listen for infrared commands sent to an address, and act uniquely
on only the ones we are interested in. The four known commands that
are received get a separate print-out.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
ADDRESS = 0x00          # The 8-bit address to listen for commands on


# Functions called for each of the remote's buttons
def up():
    print("up received")


def left():
    print("left received")


def right():
    print("right received")


def down():
    print("down received")


# Create a remote descriptor with a name, our address, and some button codes
remote = RemoteDescriptor()
remote.NAME = "Remote"
remote.ADDRESS = 0x00
remote.BUTTON_CODES = {
    "UP": 0x46,
    "LEFT": 0x44,
    "RIGHT": 0x43,
    "DOWN": 0x15,
}

# Bind functions to each of the buttons
remote.bind("UP", up)
remote.bind("LEFT", left)
remote.bind("RIGHT", right)
remote.bind("DOWN", down)

# Set up an NECRemoteReceiver on the RX pin, using PIO 1 and SM 0.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)

# Bind the remote descriptor to the receiver
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
