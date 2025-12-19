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
VOLUME_STEP = 1
BRIGHTNESS_STEP = 5

# Colour constants
RED = 0/6, 1, 1
GREEN = 2/6, 1, 1
BLUE = 4/6, 1, 1
CYAN = 3/6, 1, 1
MAGENTA = 5/6, 1, 1
YELLOW = 1/6, 1, 1
WHITE = 0, 0, 1
BLACK = 0, 0, 0


# Variables
hue = 0
sat = 0
val = 0


def rgb_from_hsv(h, s, v):
    if s == 0.0:
        return v, v, v
    else:
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p, q, t = v * (1.0 - s), v * (1.0 - s * f), v * (1.0 - s * (1.0 - f))

        i = i % 6
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        elif i == 5:
            return v, p, q


# Callback functions to adjust volume and brightness
def set_hsv(colour, _):
    global hue, sat, val
    hue = colour[0]
    sat = colour[1]
    val = colour[2]

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")

def cycle_hue(amount, _):
    global hue
    hue += amount % 1.0

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


def adjust_sat(amount, _):
    global sat
    sat = max(min(sat + amount, 1.0), 0.0)

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


def adjust_val(amount, _):
    global val
    val = max(min(val + amount, 1.0), 0.0)

    red, green, blue = [int(x * 255) for x in rgb_from_hsv(hue, sat, val)]
    print(f"Colour = #{red:02x}{green:02x}{blue:02x}")


# Create an instance of the remote, and bind the callback functions to each of its buttons
remote = PimoroniRemote()
remote.bind("1/RED", (set_hsv, RED))
remote.bind("2/GREEN", (set_hsv, GREEN))
remote.bind("3/BLUE", (set_hsv, BLUE))
remote.bind("4/CYAN", (set_hsv, CYAN))
remote.bind("5/MAGENTA", (set_hsv, MAGENTA))
remote.bind("6/YELLOW", (set_hsv, YELLOW))
remote.bind("8/WHITE", (set_hsv, WHITE))
remote.bind("OK/STOP",  (set_hsv, BLACK))
remote.bind("CLOCKWISE",  (cycle_hue, 0.1))
remote.bind("ANTICLOCK",  (cycle_hue, -0.1))
remote.bind("UP",  (adjust_val, 0.1))
remote.bind("DOWN",  (adjust_val, -0.1))
remote.bind("RIGHT",  (adjust_sat, 0.1))
remote.bind("LEFT",  (adjust_sat, -0.1))

# Set up an NECRemoteReceiver on the RX pin, using PIO 1 and SM 0.
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
