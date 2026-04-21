from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import RemoteDescriptor

"""
Listen for infrared commands sent to an address, and act uniquely
on only the ones we are interested in. The four known commands
that are received get passed to a shared function with separate data
to change their final print-out.

An IR LED (with a suitable resistor) should be connected to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
ADDRESS = 0x00          # The 8-bit address to listen for commands on


# Function called for all button presses
def received(name):
    print(f"{name} received")


# Create an instance of the remote, and bind the callback functions to each of its buttons
remote = RemoteDescriptor()
remote.NAME = "Remote"
remote.ADDRESS = 0x00
remote.BUTTON_CODES = {
    "UP": 0x46,
    "LEFT": 0x44,
    "RIGHT": 0x43,
    "DOWN": 0x15,
}

# Bind the same function to each of the buttons, but with a different parameter.
# Any number of parameters can be provided within the inner brackets, and they
# will be passed to the function separately.
# e.g. `(func, "a", "b", "c")` will go to the function as `def func(a, b, c):`
remote.bind("UP", (received, "up"))
remote.bind("LEFT", (received, "left"))
remote.bind("RIGHT", (received, "right"))
remote.bind("DOWN", (received, "down"))

# Set up an NECRemoteReceiver on the RX pin, using PIO 1 and SM 0.
# Optionally set the logging_level to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)

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
