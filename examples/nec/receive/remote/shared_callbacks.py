from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and perform actions
for the ones we are interested in, via a shared function with separate data.

Actions:
- UP Button [Press + Hold] = Print `up received`
- DOWN Button [Press + Hold] = Print `down received`
- LEFT Button [Press + Hold] = Print `left received`
- RIGHT Button [Press + Hold] = Print `right received`

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Function called for all button presses
def received(name):
    print(f"{name} received")


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# Bind the same function to each of the buttons, but with a different parameter.
# Any number of parameters can be provided within the inner brackets, and they
# will be passed to the function separately.
# e.g. `(func, "a", "b", "c")` will go to the function as `def func(a, b, c):`
remote.bind("UP", (received, "up"))
remote.bind("LEFT", (received, "left"))
remote.bind("RIGHT", (received, "right"))
remote.bind("DOWN", (received, "down"))

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
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
