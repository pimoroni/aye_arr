"""
Tests for the pulse layer's GPIO base handling and its pulse assembly.

`__analyse` is the documented override point, and MicroPython reaches it by its
plain name across the hierarchy. CPython mangles, so these tests record through
`_PulseReceiver__analyse`.
"""

import pytest
from conftest import FakeDMA, FakePIO

from aye_arr.pulse import receive
from aye_arr.pulse.pio.rx import BURST_COUNT_TIMEOUT, IDLE_COUNT_TIMEOUT, TIMEOUT_REACHED
from aye_arr.pulse.receive import DEFAULT_FILTER_THRESHOLD_US, RING_COUNTS, PulseReceiver
from aye_arr.pulse.send import PulseSender

# A pin at or above this number needs the PIO's window moved up
HIGH_PIN = 40
LOW_PIN = 5


def count_pair(burst_us, idle_us):
    """The word the PIO program emits for a pulse of these durations."""
    burst = BURST_COUNT_TIMEOUT + 5 - burst_us
    idle = IDLE_COUNT_TIMEOUT + 5 - idle_us
    return (burst << 16) | idle


@pytest.fixture
def analysed(monkeypatch):
    """Sequences handed to the receiver's analysis step, in order."""
    sequences = []
    monkeypatch.setattr(PulseReceiver, "_PulseReceiver__analyse",
                        lambda self, pulses: sequences.append(list(pulses)))
    return sequences


def receiver_with(*count_pairs, pin_num=3, pio=1, sm=0):
    """A started receiver holding these count pairs, ready to decode."""
    receiver = PulseReceiver(pin_num=pin_num, pio=pio, sm=sm)
    state_machine = receiver._PulseReceiver__sm
    receiver.start()
    state_machine.feed(*count_pairs)
    state_machine.trigger_irq()
    return receiver


class TestGpioBase:
    """The window only moves when the pin sits outside it."""

    def test_a_low_pin_leaves_the_base_alone(self):
        PulseReceiver(pin_num=LOW_PIN, pio=0, sm=0)

        assert FakePIO(0).base_sets == []

    def test_a_high_pin_moves_the_base(self):
        PulseReceiver(pin_num=HIGH_PIN, pio=0, sm=0)

        assert FakePIO(0).base_sets == [16]

    def test_a_second_receiver_does_not_move_it_again(self):
        # Setting the base is refused once a program is loaded on that PIO
        PulseReceiver(pin_num=HIGH_PIN, pio=0, sm=0)
        PulseReceiver(pin_num=HIGH_PIN, pio=0, sm=1)

        assert FakePIO(0).base_sets == [16]

    def test_a_second_sender_does_not_move_it_again(self):
        PulseSender(pin_num=HIGH_PIN, pio=0, sm=0, carrier_freq=38000)
        PulseSender(pin_num=HIGH_PIN, pio=0, sm=1, carrier_freq=38000)

        assert FakePIO(0).base_sets == [16]

    def test_a_sender_and_a_receiver_share_a_moved_base(self):
        PulseSender(pin_num=HIGH_PIN, pio=0, sm=0, carrier_freq=38000)
        PulseReceiver(pin_num=HIGH_PIN, pio=0, sm=1)

        assert FakePIO(0).base_sets == [16]

    def test_each_pio_tracks_its_own_base(self):
        PulseReceiver(pin_num=HIGH_PIN, pio=0, sm=0)
        PulseReceiver(pin_num=LOW_PIN, pio=1, sm=0)

        assert FakePIO(0).base_sets == [16]
        assert FakePIO(1).base_sets == []


class TestConstruction:
    @pytest.mark.parametrize("pio", [-1, 3])
    def test_an_out_of_range_pio_raises(self, pio):
        with pytest.raises(ValueError):
            PulseReceiver(pin_num=3, pio=pio, sm=0)

    @pytest.mark.parametrize("sm", [-1, 4])
    def test_an_out_of_range_state_machine_raises(self, sm):
        with pytest.raises(ValueError):
            PulseReceiver(pin_num=3, pio=0, sm=sm)

    def test_decoding_before_starting_raises(self):
        receiver = PulseReceiver(pin_num=3, pio=0, sm=0)

        with pytest.raises(RuntimeError):
            receiver.decode()

    def test_decoding_after_stopping_raises(self):
        receiver = PulseReceiver(pin_num=3, pio=0, sm=0)
        receiver.start()
        receiver.stop()

        with pytest.raises(RuntimeError):
            receiver.decode_no_filter()


class TestPulseAssembly:
    """Counts become pulses, and a timeout ends the sequence."""

    def test_a_timeout_delivers_the_sequence(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500),
                                 count_pair(560, 560),
                                 TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert len(analysed) == 1
        assert analysed[0] == [(9000, 4500), (560, 560)]

    def test_counts_without_a_timeout_are_held_back(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500), count_pair(560, 560))
        receiver.decode_no_filter()

        assert analysed == []

    def test_two_timeouts_deliver_two_sequences(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500),
                                 TIMEOUT_REACHED,
                                 count_pair(9000, 2250),
                                 TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert analysed == [[(9000, 4500)], [(9000, 2250)]]

    def test_a_reset_discards_held_counts(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500), count_pair(560, 560))
        receiver.reset()
        receiver.decode_no_filter()

        assert analysed == []


class TestFilter:
    """A blip shorter than the threshold is merged into its neighbour."""

    def test_a_clean_sequence_passes_through(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500),
                                 count_pair(560, 560),
                                 count_pair(560, 1680),
                                 TIMEOUT_REACHED)
        receiver.decode()

        assert analysed[0] == [(9000, 4500), (560, 560), (560, 1680)]

    def test_a_short_idle_merges_the_pulses(self, analysed):
        blip = DEFAULT_FILTER_THRESHOLD_US - 50
        receiver = receiver_with(count_pair(560, blip),
                                 count_pair(400, 1680),
                                 TIMEOUT_REACHED)
        receiver.decode()

        # The burst either side of the blip is joined into one
        assert analysed[0] == [(400 + 560 + blip, 1680)]

    def test_a_short_burst_merges_the_pulses(self, analysed):
        blip = DEFAULT_FILTER_THRESHOLD_US - 50
        receiver = receiver_with(count_pair(560, 560),
                                 count_pair(blip, 1680),
                                 TIMEOUT_REACHED)
        receiver.decode()

        # The idle either side of the blip is joined into one
        assert analysed[0] == [(560, 560 + blip + 1680)]

    def test_a_pulse_on_the_threshold_is_kept(self, analysed):
        receiver = receiver_with(count_pair(560, DEFAULT_FILTER_THRESHOLD_US),
                                 count_pair(560, 1680),
                                 TIMEOUT_REACHED)
        receiver.decode()

        assert analysed[0] == [(560, DEFAULT_FILTER_THRESHOLD_US), (560, 1680)]

    def test_a_raised_threshold_merges_a_longer_blip(self, analysed):
        receiver = receiver_with(count_pair(560, 300),
                                 count_pair(400, 1680),
                                 TIMEOUT_REACHED)
        receiver.decode(filter_threshold=400)

        assert analysed[0] == [(400 + 560 + 300, 1680)]

    def test_the_filter_does_not_drop_a_full_code_start(self, analysed):
        receiver = receiver_with(count_pair(9000, 4500),
                                 count_pair(560, 560),
                                 TIMEOUT_REACHED)
        receiver.decode()

        assert analysed[0][0] == (9000, 4500)


class TestDma:
    """A DMA channel takes counts off the state machine, which decode reads from its ring."""

    def channel(self):
        assert len(FakeDMA.channels) == 1
        return FakeDMA.channels[0]

    def test_starting_claims_a_channel_paced_by_the_rx_fifo(self):
        receiver = PulseReceiver(pin_num=3, pio=1, sm=3)
        receiver.start()
        channel = self.channel()

        assert channel.read == 0x50300020 + 3 * 4
        assert channel.ctrl["treq_sel"] == 12 + 3
        assert channel.ctrl["inc_read"] is False and channel.ctrl["inc_write"] is True
        assert channel.ctrl["size"] == 2 and channel.ctrl["ring_sel"] is True
        assert channel.running

    def test_the_ring_is_aligned_to_its_size(self):
        receiver = PulseReceiver(pin_num=3, pio=0, sm=0)
        receiver.start()
        channel = self.channel()

        ring_bytes = 1 << channel.ctrl["ring_size"]
        assert channel.write % ring_bytes == 0
        assert ring_bytes == RING_COUNTS * 4

    def test_counts_are_read_in_order_round_the_ring(self, analysed):
        receiver = receiver_with()
        # More than the ring holds, decoded a little at a time so none is overwritten
        sequences = [[(9000 - index, 4500)] for index in range(RING_COUNTS)]
        state_machine = receiver._PulseReceiver__sm
        for sequence in sequences:
            state_machine.feed(count_pair(*sequence[0]), TIMEOUT_REACHED)
            receiver.decode_no_filter()

        assert analysed == sequences

    def test_a_ring_gone_round_unread_drops_what_it_lost(self, analysed):
        receiver = receiver_with()
        state_machine = receiver._PulseReceiver__sm
        state_machine.feed(*([count_pair(560, 560)] * (RING_COUNTS + 10)))
        receiver.decode_no_filter()
        state_machine.feed(count_pair(9000, 4500), TIMEOUT_REACHED)
        receiver.decode_no_filter()

        # The overrun sequence is dropped, and the next one arrives whole
        assert analysed == [[(9000, 4500)]]

    def test_a_spent_channel_is_armed_again(self, analysed, monkeypatch):
        # A run of two counts, which the first sequence uses up
        monkeypatch.setattr(receive, "DMA_COUNT", 2)
        receiver = receiver_with()
        channel = self.channel()
        state_machine = receiver._PulseReceiver__sm
        state_machine.feed(count_pair(9000, 4500), TIMEOUT_REACHED)
        assert not channel.running

        receiver.decode_no_filter()
        state_machine.feed(count_pair(9000, 2250), TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert analysed == [[(9000, 4500)], [(9000, 2250)]]
        assert channel.running

    def test_a_reset_skips_counts_still_in_the_ring(self, analysed):
        receiver = receiver_with()
        state_machine = receiver._PulseReceiver__sm
        state_machine.feed(count_pair(9000, 4500), TIMEOUT_REACHED)
        receiver.reset()
        receiver.decode_no_filter()

        assert analysed == []

    def test_stopping_frees_the_channel(self):
        receiver = PulseReceiver(pin_num=3, pio=0, sm=0)
        receiver.start()
        channel = self.channel()
        receiver.stop()

        assert channel.closed and FakeDMA.channels == []

    def test_starting_again_takes_a_fresh_channel(self, analysed):
        receiver = PulseReceiver(pin_num=3, pio=0, sm=0)
        receiver.start()
        receiver.stop()
        receiver.start()
        receiver._PulseReceiver__sm.feed(count_pair(9000, 4500), TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert analysed == [[(9000, 4500)]]

    def test_with_every_channel_taken_the_interrupt_stands_in(self, analysed):
        FakeDMA.refuse = True
        receiver = receiver_with(count_pair(9000, 4500), TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert FakeDMA.channels == []
        assert analysed == [[(9000, 4500)]]

    def test_without_dma_the_interrupt_stands_in(self, analysed, monkeypatch):
        monkeypatch.setattr(receive, "DMA", None)
        receiver = receiver_with(count_pair(9000, 4500), TIMEOUT_REACHED)
        receiver.decode_no_filter()

        assert FakeDMA.channels == []
        assert analysed == [[(9000, 4500)]]
