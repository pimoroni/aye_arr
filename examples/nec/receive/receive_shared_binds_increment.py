from aye_arr.nec import NECRemoteReceiver
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
VOLUME_STEP = 1
BRIGHTNESS_STEP = 5

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


# Variables
volume = 0          # An example variable for a system's volume
brightness = 0      # An example variable for a system's brightness


# Callback functions to adjust volume and brightness
def adjust_volume(amount, ms, l_ms):
    global volume
    volume = max(min(volume + amount, 11), 0)
    print(f"Volume = {volume}")


def adjust_brightness(amount, ms, l_ms):
    global brightness
    brightness = max(min(brightness + amount, 100), 0)
    print(f"Brightness = {brightness}%")


# Create an instance of the remote, and bind the callback functions to each of its buttons
remote = Remote()
remote.bind("UP", (adjust_volume, VOLUME_STEP))
remote.bind("DOWN", (adjust_volume, -VOLUME_STEP))
remote.bind("RIGHT", (adjust_brightness, BRIGHTNESS_STEP))
remote.bind("LEFT", (adjust_brightness, -BRIGHTNESS_STEP))


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
