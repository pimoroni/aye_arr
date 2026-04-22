import aye_arr.logging as logging
from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Listen for NEC infrared commands sent from a Pimoroni remote, and have
each button perform a different set of actions.

Actions:
- UP Button [Press + Hold]
- DOWN Button [Press]
- LEFT Button [Press + Hold + Release]
- RIGHT Button [Release Only]
- ANTICLOCK Button [Short Press + Hold]
- CLOCKWISE Button [Short Press + Release (aka Long Press)]

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Functions called for each of the remote's buttons
def pressed(name):
    print(f"{name}: pressed")


def held(name):
    print(f"{name}: held")


def released(name):
    print(f"{name}: released")


def short(name):
    print(f"{name}: short release")


# Create an instance of the ready-made Pimoroni remote descriptor
remote = PimoroniRemote()

# --------------------------
# ----- Press and Hold -----
# --------------------------
remote.bind("UP", (pressed, "up"))

# OR
# remote.bind("UP",
#             on_press=(pressed, "up"))
#             on_repeat=(pressed, "up"))

# -----------------------------------------
# ----- Press only (good for toggles) -----
# -----------------------------------------
remote.bind("DOWN",
            on_press=(pressed, "down"),
            on_repeat=None)

# --------------------------------
# ----- Press, Hold, Release -----
# --------------------------------
remote.bind("LEFT",
            on_press=(pressed, "left"),
            on_repeat=(held, "left"),
            on_release=(released, "left"))

# ------------------------------------------------
# ----- Release only (also good for toggles) -----
# ------------------------------------------------
remote.bind("RIGHT",
            on_press=None,
            on_release=(released, "right"))

# --------------------------------
# ----- Short press and Hold -----
# --------------------------------
remote.bind("ANTICLOCK",
            on_press=None,
            on_short=(short, "anticlock"),
            on_repeat=(held, "anticlock"))

# --------------------------------
# ----- Short and Long press -----
# --------------------------------
remote.bind("CLOCKWISE",
            on_press=None,
            on_short=(short, "clockwise"),
            on_release=(released, "clockwise"))

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
