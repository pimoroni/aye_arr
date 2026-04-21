from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
"""

# Constants
IR_RX_PIN = 4           # The pin to listen for IR pulses on
SPEED = 0.5             # The speed the motors will drive at

# Set up the left and right motors
left = Motor(pico_motor_shim.MOTOR_1)
right = Motor(pico_motor_shim.MOTOR_2)

# Reverse the driving direction of the left motor
# to make the movement code more understandable
left.direction(REVERSED_DIR)


# Function for driving forward or backward
def forward(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(SPEED)
    else:
        left.speed(-SPEED)
        right.speed(-SPEED)


# Function for turning on the spot
def turn(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(-SPEED)
    else:
        left.speed(-SPEED)
        right.speed(SPEED)


# Function for turning in an arc
def arc(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(SPEED / 2)
    else:
        left.speed(SPEED / 2)
        right.speed(SPEED)


# Function to stop moving
def stop():
    left.stop()
    right.stop()


# Create the remote and setup up what each of the buttons will do
remote = PimoroniRemote()
remote.bind("UP", on_press=(forward, 1), on_release=stop)
remote.bind("DOWN", on_press=(forward, -1), on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
remote.bind("ANTICLOCK", on_press=(arc, -1), on_release=stop)
remote.bind("CLOCKWISE", on_press=(arc, 1), on_release=stop)

# Set up a receiver on the RX pin, using PIO 1 and SM 0, and bind the remote to it.
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
    left.disable()
    right.disable()
