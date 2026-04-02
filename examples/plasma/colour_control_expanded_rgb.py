import plasma

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
An example for the Plasma2350 and IR Stick (Connected to the QW/sT).
Buttons:

Long Press/Hold:
1-4 = Increase/Decrease the Red channel
2-5 = Increase/Decrease the Green channel
3-6 = Increase/Decrease the Blue channel

Short Press (numpad):
Sets the LEDs to the colour shown on the remote.

OK/Stop:
Reduce all channels to zero

"""

# Color constants
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
CYAN = [0, 255, 255]
MAGENTA = [255, 0, 255]
YELLOW = [255, 255, 0]
WARM_WHITE = [255, 192, 96]
WHITE = [255, 255, 255]
COOL_WHITE = [96, 192, 255]
BLACK = [0, 0, 0]

# Colour Values
rgb = [100, 100, 100]
increment = 10

# setup for the led strip
NM_LEDS = 30
led_strip = plasma.WS2812(NM_LEDS, color_order=plasma.COLOR_ORDER_BGR)
led_strip.start()


def set_preset(color, ms, v):
    global rgb
    rgb = color


def update_red(value, ms, v):
    global rgb
    rgb[0] = max(min(rgb[0] + value, 255), 0)


def update_green(value, ms, v):
    global rgb
    rgb[1] = max(min(rgb[1] + value, 255), 0)


def update_blue(value, ms, v):
    global rgb
    rgb[2] = max(min(rgb[2] + value, 255), 0)


def update():

    for led in range(NM_LEDS):
        led_strip.set_rgb(led, *rgb)


# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()

remote.bind("1/RED", on_press=None, on_short=(set_preset, RED), on_repeat=(update_red, increment))
remote.bind("4/CYAN", on_press=None, on_short=(set_preset, CYAN), on_repeat=(update_red, -increment))

remote.bind("2/GREEN", on_press=None, on_short=(set_preset, GREEN), on_repeat=(update_green, increment))
remote.bind("5/MAGENTA", on_press=None, on_short=(set_preset, MAGENTA), on_repeat=(update_green, -increment))

remote.bind("3/BLUE", on_press=None, on_short=(set_preset, BLUE), on_repeat=(update_blue, increment))
remote.bind("6/YELLOW", on_press=None, on_short=(set_preset, YELLOW), on_repeat=(update_blue, -increment))

remote.bind("7/WARM", (set_preset, WARM_WHITE))
remote.bind("8/WHITE", (set_preset, WHITE))
remote.bind("9/COOL", (set_preset, COOL_WHITE))
remote.bind("OK/STOP", (set_preset, BLACK))

receiver = NECRemoteReceiver(20, 1, 0)
receiver.bind(remote)

try:
    receiver.start()

    while True:
        receiver.decode()
        update()

finally:
    receiver.stop()
