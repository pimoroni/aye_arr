# SPDX-FileCopyrightText: 2026 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from collections import deque

from machine import Pin
from rp2 import PIO, StateMachine

from .common import DebugPin, Pulse
from .pio.rx import FREQUENCY, TIMEOUT_REACHED, count_to_burst_us, count_to_idle_us, pulsereader, pulsereader_debug

# A port built without DMA takes the received counts by interrupt instead
try:
    from rp2 import DMA
    from uctypes import addressof
except ImportError:
    DMA = None

# Constants
MAX_BUFFER = const(1024)
DEFAULT_FILTER_THRESHOLD_US = const(200)

# The ring the DMA copies received counts into, which must be a power of two in size and
# aligned to it for the DMA to wrap its writes there. 256 counts is several remote presses
RING_COUNTS = const(256)
RING_BYTES = const(RING_COUNTS * 4)
RING_SIZE_BITS = const(10)              # RING_BYTES as a power of two

# How many counts the DMA takes before it is armed again. The top four bits stay clear, as
# the RP2350 reads them as the transfer's mode
DMA_COUNT = const(0x0fffffff)

# The RX FIFO register of PIO 0's state machine 0, and how far apart the PIOs' registers sit.
# Each state machine's register is the next word along
PIO0_RXF0 = const(0x50200020)
PIO_REGISTER_STEP = const(0x100000)

# The DMA request that PIO 0's state machine 0 raises when its RX FIFO holds a count, and
# how far apart the PIOs' requests are. Each state machine's request is the next along
DREQ_PIO0_RX0 = const(4)
DREQ_PIO_STEP = const(8)


class PulseReceiver:
    def __init__(self, pin_num, pio, sm,
                 debug_pin_base=None, debug_blip_pin=None):
        self.__counts = deque((), MAX_BUFFER)
        self.__sequence = []
        self.__last_pulse = None

        # The DMA channel copying counts off the state machine, its ring, and how many counts
        # have been taken from the ring since the channel was armed. None until started
        self.__dma = None
        self.__ring = None
        self.__ring_start = 0
        self.__taken = 0

        # Check the PIO is valid
        try:
            _ = PIO(pio)
        except ValueError:
            raise ValueError("pio out of range. Expected 0 or 1 (or 2 if on RP2350)") from None

        # Check the State Machine is valid
        if sm < 0 or sm > 3:
            raise ValueError("sm out of range. Expected 0 to 3")

        # Set up the pin used to receive pulse signals
        pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)

        # For the RP2350, shift the gpio_base of this PIO if the pin is above 32.
        # Setting it is refused once a program is loaded on that PIO, which a second
        # receiver on the same PIO meets, so only move it where it is not already there
        base = 16 if pin_num >= 32 else 0
        try:
            if PIO(pio).gpio_base() != Pin(base):
                PIO(pio).gpio_base(base)
        except AttributeError:
            # Handle RP2040 not having the gpio_base function
            pass

        # Load either the regular or debug program into the chosen StateMachine
        if debug_pin_base is None:
            self.__sm = StateMachine(sm + (pio * 4), pulsereader,
                                         freq=FREQUENCY, in_base=pin,
                                         jmp_pin=pin)
        else:
            if debug_pin_base < base or debug_pin_base > base + 30:    # 30 because the debug PIO uses two sideset pins
                raise ValueError(f"'debug_pin_base' is outside the GPIO base of 'pin_num'.\
                                 Choose a 'debug_pin_base' between {base} and {base + 30}") from None
            self.__sm = StateMachine(sm + (pio * 4), pulsereader_debug,
                                         freq=FREQUENCY, in_base=pin,
                                         sideset_base=Pin(debug_pin_base),
                                         jmp_pin=pin)

        # Set up debug pin for scoping
        self.__debug_blip_pin = DebugPin(debug_blip_pin, Pin.OUT)

        # Where the DMA reads this state machine's counts from, and the request it waits on
        self.__rx_fifo = PIO0_RXF0 + (pio * PIO_REGISTER_STEP) + (sm * 4)
        self.__dreq = DREQ_PIO0_RX0 + (pio * DREQ_PIO_STEP) + sm

    def start(self):
        # The DMA takes each count off the state machine as it arrives, with no code waiting to
        # run. An interrupt handler waits on the scheduler, which other work, such as a screen
        # being sent a frame, can hold up for longer than the RX FIFO lasts
        if DMA is not None:
            try:
                self.__dma = DMA()
            except OSError:
                self.__dma = None    # Every channel is taken, so the interrupt handler stands in
        if self.__dma is not None:
            self.__arm()
        else:
            self.__sm.irq(self.__handler)
        self.__sm.active(1)

    def stop(self):
        self.__sm.active(0)
        if self.__dma is not None:
            self.__dma.close()
            self.__dma = None
        else:
            self.__sm.irq(None)

    def reset(self):
        self.__counts = deque((), MAX_BUFFER)
        self.__sequence = []
        if self.__dma is not None:
            self.__taken = DMA_COUNT - self.__dma.count

    def __arm(self):
        # Point the DMA at a ring aligned to its own size, inside a buffer twice that size, so
        # it writes counts round the ring while the state machine has them
        if self.__ring is None:
            self.__ring = bytearray(RING_BYTES * 2)
            address = addressof(self.__ring)
            self.__ring_start = ((address + RING_BYTES - 1) & ~(RING_BYTES - 1)) - address

        ctrl = self.__dma.pack_ctrl(size=2, inc_read=False, inc_write=True,
                                    ring_size=RING_SIZE_BITS, ring_sel=True, treq_sel=self.__dreq)
        self.__dma.config(read=self.__rx_fifo, write=addressof(self.__ring) + self.__ring_start,
                          count=DMA_COUNT, ctrl=ctrl, trigger=True)
        self.__taken = 0

    def __collect(self):
        # Move the counts the DMA has written since the last decode onto the deque
        if self.__dma is None:
            return

        written = DMA_COUNT - self.__dma.count

        # Check if the ring went round before these were read, losing the oldest of them and
        # with them the sequence they were part of
        if written - self.__taken > RING_COUNTS:
            self.__taken = written
            self.__sequence.clear()
            self.__last_pulse = None
            return

        while self.__taken < written:
            at = self.__ring_start + (self.__taken % RING_COUNTS) * 4
            self.__counts.append(int.from_bytes(self.__ring[at:at + 4], "little"))
            self.__taken += 1

        # A channel that has taken all its counts is armed again, its ring read to the end
        if written == DMA_COUNT:
            self.__arm()

    @micropython.native
    def __handler(self, sm):
        # Copy received counts from the SM to the deque for later processing.
        while sm.rx_fifo() > 0:
            self.__counts.append(sm.get())

    def __analyse(self, pulses):
        # Override this to analyse a received sequence of pulses
        pass

    def decode_no_filter(self):
        """
        Checks for any newly received pulses since the last time `decode` was
        called. Once a sufficient number of pulses has been received, as
        indicated by the PIO program's timeout being reached, the pulses are
        passed to an overridable `__analyse` function to act on any data.

        This should be called frequently from user code to avoid pulses
        queuing up and making remote button presses feel sluggish.

        This function lacks any filtering meaning any "blips" in
        received pulses could cause data to be discarded.
        """

        if not self.__sm.active():
            raise RuntimeError("Cannot decode IR signals. Check that you have called `.start()` on the receiver first.")

        self.__collect()

        # Go through all counts currently stored
        while len(self.__counts) > 0:
            count_pair = self.__counts.popleft()   # Extract the oldest count pair

            # Did the count timeout get reached?
            if count_pair == TIMEOUT_REACHED:
                # Analyse, and clear the pulse sequence
                self.__analyse(self.__sequence)
                self.__sequence.clear()
                continue        # Skip to the next pulse

            # Otherwise, convert the count pair into a pulse and add it to the sequence
            pulse = Pulse(count_to_burst_us((count_pair >> 16) & 0xffff),
                          count_to_idle_us(count_pair & 0xffff))
            self.__sequence.append(pulse)

    def decode(self, filter_threshold=DEFAULT_FILTER_THRESHOLD_US):   # with filter
        """
        Checks for any newly received pulses since the last time `decode` was
        called. Once a sufficient number of pulses has been received, as
        indicated by the PIO program's timeout being reached, the pulses are
        passed to an overridable `__analyse` function to act on any data.

        This should be called frequently from user code to avoid pulses
        queuing up and making remote button presses feel sluggish.

        This function includes a low-pass filter to removes any "blips" in
        received pulses to recover data that may otherwise be discarded.
        """

        if not self.__sm.active():
            raise RuntimeError("Cannot decode IR signals. Check that you have called `.start()` on the receiver first.")

        self.__collect()

        # Go through all counts currently stored
        while len(self.__counts) > 0:
            count_pair = self.__counts.popleft()   # Extract the oldest count pair

            # Did the count timeout get reached?
            if count_pair == TIMEOUT_REACHED:
                # If there is one, add the last pulse to the pulse sequence to finish it off
                if self.__last_pulse is not None:
                    self.__sequence.append(self.__last_pulse)
                    self.__last_pulse = None

                # Analyse, and clear the pulse sequence
                self.__analyse(self.__sequence)
                self.__sequence.clear()
                continue        # Skip to the next pulse

            # Otherwise, convert the count pair into a pulse
            current_pulse = Pulse(count_to_burst_us((count_pair >> 16) & 0xffff),
                                  count_to_idle_us(count_pair & 0xffff))

            # Is this the first pulse we've received in this sequence?
            if self.__last_pulse is None:
                self.__last_pulse = current_pulse   # Save it for later
                continue        # Skip to the next pulse

            last_burst, last_idle = self.__last_pulse   # For convenience

            # Was the idle of the last pulse below the filter threshold?
            if last_idle < filter_threshold:
                self.__debug_blip_pin.on()      # Show that a blip was detected

                # Filter out the blip by merging the last pulse into the burst of the current pulse, updating the last pulse
                self.__last_pulse = Pulse(
                    current_pulse.burst + last_burst + last_idle,
                    current_pulse.idle      # Idle is unchanged
                )

                self.__debug_blip_pin.off()     # Show that a blip was handled
                continue        # Skip to the next pulse

            # Was the burst of the current pulse below the filter threshold?
            if current_pulse.burst < filter_threshold:
                self.__debug_blip_pin.on()      # Show that a blip was detected

                # Filter out the blip by merging the current pulse into the idle of the last pulse, updating the last pulse
                self.__last_pulse = Pulse(
                    last_burst,     # Burst is unchanged
                    last_idle + current_pulse.burst + current_pulse.idle
                )

                self.__debug_blip_pin.off()     # Show that a blip was handled
                continue        # Skip to the next pulse

            # The last pulse is now valid, so add it to the pulse sequence, and update the last pulse
            self.__sequence.append(self.__last_pulse)
            self.__last_pulse = current_pulse
