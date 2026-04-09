from pimoroni import RGBLED

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Color constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Setup the RGB Led
led = RGBLED(18, 19, 20)


def set_led(color):

    led.set_rgb(*color)


# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
remote.bind("1_RED", (set_led, RED))
remote.bind("2_GREEN", (set_led, GREEN))
remote.bind("3_BLUE", (set_led, BLUE))
remote.bind("4_CYAN", (set_led, CYAN))
remote.bind("5_MAGENTA", (set_led, MAGENTA))
remote.bind("6_YELLOW", (set_led, YELLOW))
remote.bind("OK_STOP", (set_led, BLACK))

receiver = NECRemoteReceiver(12, 1, 0)
receiver.bind(remote)

try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
