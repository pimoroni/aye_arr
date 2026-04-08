from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

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

# Colour constants
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0
WARM = 255, 192, 96
WHITE = 255, 255, 255
COOL = 96, 192, 255
BLACK = 0, 0, 0

# Variables
red = 0
green = 0
blue = 0


# Callback functions to adjust volume and brightness
def set_colour(colour, ms, l_ms):
    global red, green, blue
    red = colour[0]
    green = colour[1]
    blue = colour[2]
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Create an instance of the remote, and bind the callback functions to each of its buttons
remote = PimoroniRemote()
remote.bind("1_RED", (set_colour, RED))
remote.bind("2_GREEN", (set_colour, GREEN))
remote.bind("3_BLUE", (set_colour, BLUE))
remote.bind("4_CYAN", (set_colour, CYAN))
remote.bind("5_MAGENTA", (set_colour, MAGENTA))
remote.bind("6_YELLOW", (set_colour, YELLOW))
remote.bind("7_WARM", (set_colour, WARM))
remote.bind("8_WHITE", (set_colour, WHITE))
remote.bind("9_COOL", (set_colour, COOL))
remote.bind("OK_STOP", (set_colour, BLACK))

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
