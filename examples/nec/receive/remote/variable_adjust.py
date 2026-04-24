from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and use
them to change the values of local "volume" and "brightness" variables.

Actions:
- UP Button [Press + Hold] = Increase Volume
- DOWN Button [Press + Hold] = Decrease Volume
- LEFT Button [Press + Hold] = Decrease Brightness
- RIGHT Button [Press + Hold] = Increase Brightness

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on

VOLUME_STEP = 1         # The amount that volume will change by with each press / repeat
BRIGHTNESS_STEP = 5     # The amount that brightness will change by with each press / repeat

# Variables
volume = 0              # An example variable for a system's volume
brightness = 0          # An example variable for a system's brightness


# Function called to change the volume
def adjust_volume(amount):
    global volume
    volume = max(min(volume + amount, 11), 0)
    print(f"Volume = {volume}")


# Function called to change the brightness
def adjust_brightness(amount):
    global brightness
    brightness = max(min(brightness + amount, 100), 0)
    print(f"Brightness = {brightness}%")


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# Bind the same two functions to pairs of buttons, with positive and negative values
remote.bind("UP", (adjust_volume, VOLUME_STEP))
remote.bind("DOWN", (adjust_volume, -VOLUME_STEP))
remote.bind("RIGHT", (adjust_brightness, BRIGHTNESS_STEP))
remote.bind("LEFT", (adjust_brightness, -BRIGHTNESS_STEP))

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Print out the initial values (by calling the adjust functions with no change)
    adjust_volume(0)
    adjust_brightness(0)

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
