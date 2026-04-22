from pimoroni import RGBLED

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Set the colour of Tiny 2350's onboard RGB LED using the
number buttons on the Pimoroni Aye Arr Remote.

Actions:
- (1)-(9) Buttons [Press + Hold] = Set Colour
- OK Button [Press + Hold] = Set Black

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of Tiny's Qw/ST port.

Press CTRL+C to exit the program.
"""

# Constant
IR_RX_PIN = 12          # The pin to listen for IR pulses on
LED_PINS = 18, 19, 20   # The pins for controlling a RGB LED

# Color constants
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

# Setup the RGB LED
led = RGBLED(*LED_PINS)


# Function called when a colour button is pressed
def set_led(colour):
    led.set_rgb(*colour)
    print(f"Colour = #{colour[0]:02x}{colour[1]:02x}{colour[2]:02x}")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", (set_led, RED))
remote.bind("2_GREEN", (set_led, GREEN))
remote.bind("3_BLUE", (set_led, BLUE))
remote.bind("4_CYAN", (set_led, CYAN))
remote.bind("5_MAGENTA", (set_led, MAGENTA))
remote.bind("6_YELLOW", (set_led, YELLOW))
remote.bind("7_WARM", (set_led, WARM))
remote.bind("8_WHITE", (set_led, WHITE))
remote.bind("9_COOL", (set_led, COOL))
remote.bind("OK_STOP", (set_led, BLACK))

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
