import plasma

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Color constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WARM_WHITE = (255, 192, 96)
WHITE = (255, 255, 255)
COOL_WHITE = (96, 192, 255)
BLACK = (0, 0, 0)

# setup for the led strip
NM_LEDS = 50
led_strip = plasma.WS2812(NM_LEDS, color_order=plasma.COLOR_ORDER_BGR)
led_strip.start()


def change_all_rgb(color):

    for led in range(NM_LEDS):
        led_strip.set_rgb(led, *color)


# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
remote.bind("1_RED", (change_all_rgb, RED))
remote.bind("2_GREEN", (change_all_rgb, GREEN))
remote.bind("3_BLUE", (change_all_rgb, BLUE))
remote.bind("4_CYAN", (change_all_rgb, CYAN))
remote.bind("5_MAGENTA", (change_all_rgb, MAGENTA))
remote.bind("6_YELLOW", (change_all_rgb, YELLOW))
remote.bind("7_WARM", (change_all_rgb, WARM_WHITE))
remote.bind("8_WHITE", (change_all_rgb, WHITE))
remote.bind("9_COOL", (change_all_rgb, COOL_WHITE))
remote.bind("OK_STOP", (change_all_rgb, BLACK))

receiver = NECRemoteReceiver(20, 1, 0)
receiver.bind(remote)

try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
