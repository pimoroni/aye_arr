from aye_arr.nec import NECReceiver

"""
Listen for infrared codes and their repeats, and act on them.
Any code that is received gets printed out.

An IR receiver should be connected to the IR_RX_PIN of your board.

Press CTRL+C to exit the program.
"""

# Constants
IR_RX_PIN = 26          # The pin to listen for IR pulses on


# Function called when a code is received
def received(code):
    print("Received Code 0x{CODE:04x}")


# Function called when a repeat code is received
def repeated(code):
    print("Repeat Received 0x{CODE:04x}")


# Set up a receiver on the RX pin, using PIO 1 and SM 0.
# Optionally set the logging_level to get more information about what is received.
# Accepted values are LOG_NONE, LOG_WARN (the default), LOG_INFO, and LOG_DEBUG
receiver = NECReceiver(IR_RX_PIN, 1, 0)

# Bind the receive function to the receiver, and turn off listening for repeats
receive.bind(on_press=received, on_repeat=repeated)

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
