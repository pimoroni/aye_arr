from motor import Motor

from aye_arr.nec import NECRemoteReceiver
from aye_arr.nec.remotes import PimoroniRemote

# Create the remote and setup up what each of our buttons will do.
remote = PimoroniRemote()
receiver = NECRemoteReceiver(4, 1, 0)

# Create a list of motors
MOTOR_PINS = [(6, 7), (26, 27)]
motors = [Motor(pins) for pins in MOTOR_PINS]


def reverse():
    for m in motors:
        m.full_positive()


def forward():
    for m in motors:
        m.full_negative()


def turn(d):
    if d > 0:
        motors[1].full_positive()
        motors[0].full_negative()
    else:
        motors[0].full_positive()
        motors[1].full_negative()


def stop():
    for m in motors:
        m.stop()


remote.bind("UP", on_press=forward, on_release=stop)
remote.bind("DOWN", on_press=reverse, on_release=stop)
remote.bind("LEFT", on_press=(turn, -1), on_release=stop)
remote.bind("RIGHT", on_press=(turn, 1), on_release=stop)
receiver.bind(remote)

try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
    for m in motors:
        m.disable()
