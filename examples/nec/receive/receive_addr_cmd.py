from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import RemoteDescriptor

"""
Listen for infrared commands sent to an address, and act on them.
Any command that is received gets printed out.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on
ADDRESS = 0x00          # The 8-bit address to listen for commands on


# Function called when a command to our address is received
def received(command):
    print(f"Received 0x{command:02x}")
    return True     # Let the receiver know we handled this command


# Create a remote descriptor with a name and our address, and bind the receive function to it
remote = RemoteDescriptor()
remote.NAME = "Remote"
remote.ADDRESS = ADDRESS
remote.on_any = received

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
