from aye_arr.nec.receive import NECRemoteReceiver
from aye_arr.nec.remotes import RemoteDescriptor

"""
A barebones example of how to send an infrared code.

In it the chosen code is sent multiple times in bursts, followed
by a period of silence. The number of codes per burst, as well as
the burst and silence timings can be adjusted.

An IR LED (with a suitable resistor) should be connected to the IR_TX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Create a description of the remote we are listening for
class Remote(RemoteDescriptor):
    NAME = "Remote"

    ADDRESS = 0x00

    BUTTON_CODES = {
        "UP": 0x46,
        "LEFT": 0x44,
        "RIGHT": 0x43,
        "DOWN": 0x15,
    }


# Callback function for 
def received_any(command):
    print(f"Received 0x{command:02x}")
    return True


def received_known(button):
    print(f"Received `{button}`")
    return False


# Create an instance of the remote, and bind the callback functions to each of its buttons
remote = Remote()
remote.on_any = received_any
remote.on_known = received_known

# Set up an NECRemoteReceiver on the RX pin, using PIO 1 and SM 0.
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
