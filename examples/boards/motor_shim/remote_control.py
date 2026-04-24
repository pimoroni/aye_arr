from motor import Motor, pico_motor_shim
from pimoroni import REVERSED_DIR

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

"""
Control a 2-wheeled robot built using a Raspberry Pi Pico and
Pimoroni Motor Shim for Pico using the Pimoroni Aye Arr Remote.

Actions:
- UP Button [Press + Hold] = Drive Forward
- DOWN Button [Press + Hold] = Drive Backward
- LEFT Button [Press + Hold] = Turn Left
- RIGHT Button [Press + Hold] = Turn Right
- ANTICLOCK Button [Press + Hold] = Arc Forward-Left
- CLOCKWISE Button [Press + Hold] = Arc Forward-Right
- Directional Buttons [Release] = Stop Driving

An IR receiver should be connected to the IR_RX_PIN of your board.
E.g. an IR Stick connected to the 3V, GND, and SDA of the Motor Shim's Qw/ST port.

Press CTRL+C to exit the program.
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


# Drive forward or backward
def forward(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(SPEED)
        print("Driving Forward")
    else:
        left.speed(-SPEED)
        right.speed(-SPEED)
        print("Driving Backward")


# Turn on the spot
def turn(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(-SPEED)
        print("Turning Right")
    else:
        left.speed(-SPEED)
        right.speed(SPEED)
        print("Turning Left")


# Turn in a forward arc
def arc(d):
    if d > 0:
        left.speed(SPEED)
        right.speed(SPEED / 2)
        print("Arcing Forward-Right")
    else:
        left.speed(SPEED / 2)
        right.speed(SPEED)
        print("Arcing Forward-Left")


# Stop moving
def stop():
    left.stop()
    right.stop()
    print("Stopping")


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
