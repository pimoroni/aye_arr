import time
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote
from aye_arr.logging import LOG_NONE


IR_PIN = 12


def press():
    print("Press!")


def short():
    print("Short Press!")


def release():
    print("Button Released!")


def repeat(ms, last_ms):
    # calculate how long the current button has been held
    held = time.ticks_diff(ms, last_ms) / 1000

    print(f"Repeating/Held button for {held} seconds")


# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()

remote.bind("5/MAGENTA", on_press=press, on_short=None, on_release=release, on_repeat=repeat)

receiver = NECRemoteReceiver(IR_PIN, 1, 0, logging_level=LOG_NONE)
receiver.bind(remote)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    print("Press (5) on the keypad to test button press types!")
    receiver.start()

    # Loop until the effect stops or the "Boot" button is pressed
    while True:
        receiver.decode()   # Add exception if this is called but start hasn't been called, or is in a stopped state

# Stop any running effects and turn off the LED strip
finally:
    receiver.stop()
    time.sleep(0.1)
