from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Examples of how remote buttons can be bound in different ways.

An IR receiver should be connected to the IR_RX_PIN.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Callback functions for different button functions
def pressed():
    print("pressed")


def held():
    print("held")


def released():
    print("released\n")


def short():
    print("short release\n")


# Create an instance of the remote for binding callbacks to buttons
remote = PimoroniRemote()


# --------------------------
# ----- Press and Hold -----
# --------------------------
remote.bind("UP", pressed)

# OR
# remote.bind("UP",
#             on_press=pressed)
#             on_repeat=pressed)


# --------------------------------
# ----- Press, Hold, Release -----
# --------------------------------
remote.bind("LEFT", pressed, held, released)

# OR
# remote.bind("LEFT",
#             on_press=pressed,
#             on_repeat=held,
#             on_release=released)


# -----------------------------------------
# ----- Press only (good for toggles) -----
# -----------------------------------------
remote.bind("RIGHT", pressed, None)

# OR
# remote.bind("RIGHT",
#             on_press=pressed,
#             on_repeat=None)


# ------------------------------------------------
# ----- Release only (also good for toggles) -----
# ------------------------------------------------
remote.bind("DOWN",
            on_press=None,
            on_release=released)


# --------------------------------
# ----- Short press and Hold -----
# --------------------------------
remote.bind("ANTICLOCK",
            on_press=None,
            on_repeat=held,
            on_short=short)


# --------------------------------
# ----- Short and Long press -----
# --------------------------------
remote.bind("CLOCKWISE",
            on_press=None,
            on_release=released,
            on_short=short)


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
