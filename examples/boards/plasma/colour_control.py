import time

from machine import Pin
from plasma import COLOR_ORDER_BGR, WS2812

import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Constants
IR_RX_PIN = 20          # The pin to listen for IR pulses on
NUM_LEDS = 66           # The number of LEDs on the strip

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

# Setup the RGB LED strip
strip = WS2812(NUM_LEDS, 0, 0, Pin.board.PLASMA_DAT,
               color_order=COLOR_ORDER_BGR)


# Function called when a colour button is pressed
def set_strip(colour):
    for led in range(NUM_LEDS):
        strip.set_rgb(led, *colour)
    print(f"Colour = #{colour[0]:02x}{colour[1]:02x}{colour[2]:02x}")


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("1_RED", (set_strip, RED))
remote.bind("2_GREEN", (set_strip, GREEN))
remote.bind("3_BLUE", (set_strip, BLUE))
remote.bind("4_CYAN", (set_strip, CYAN))
remote.bind("5_MAGENTA", (set_strip, MAGENTA))
remote.bind("6_YELLOW", (set_strip, YELLOW))
remote.bind("7_WARM", (set_strip, WARM))
remote.bind("8_WHITE", (set_strip, WHITE))
remote.bind("9_COOL", (set_strip, COOL))
remote.bind("OK_STOP", (set_strip, BLACK))

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
# The logging level can be increased to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECRemoteReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    strip.start()
    receiver.start()

    # Loop forever
    while True:
        # Decode any IR pulses received since the last time this was called.
        # This should be done as frequently as possible to avoid inputs feeling sluggish
        receiver.decode()

# End the program by stopping any active systems
finally:
    receiver.stop()
    strip.clear()
    time.sleep(0.1)     # Short delay for the clear to take effect
