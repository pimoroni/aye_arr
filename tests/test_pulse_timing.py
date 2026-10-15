"""
Tests for the NEC timing tolerance and the receiver's count conversions.

These are the arithmetic the protocol rests on, so they are pinned against the
NEC specification's figures and against the PIO program's counter widths.
"""

from aye_arr.nec.common import (NEC_ALLOWED_DEVIATION_PERCENT, NEC_DATA_BURST_US, NEC_DATA_ONE_US, NEC_DATA_ZERO_US, NEC_NONE, NEC_REPEAT, NEC_START_BURST_US, NEC_START_DATA_US, NEC_START_REPEAT_US,
                                pulse_us_valid)
from aye_arr.pulse.pio.rx import BURST_COUNT_TIMEOUT, IDLE_COUNT_TIMEOUT, count_to_burst_us, count_to_idle_us


class TestNECConstants:
    def test_specification_figures(self):
        assert NEC_START_BURST_US == 9000
        assert NEC_START_DATA_US == 4500
        assert NEC_START_REPEAT_US == 2250
        assert NEC_DATA_BURST_US == 560

    def test_a_one_is_three_times_a_zero(self):
        assert NEC_DATA_ZERO_US == NEC_DATA_BURST_US
        assert NEC_DATA_ONE_US == NEC_DATA_BURST_US * 3

    def test_sentinels_are_distinct_and_negative(self):
        # A code is a 32 bit unsigned value, so both sentinels sit below zero
        assert NEC_REPEAT < 0
        assert NEC_NONE < 0
        assert NEC_REPEAT != NEC_NONE


class TestPulseUsValid:
    def test_an_exact_pulse_is_valid(self):
        assert pulse_us_valid(NEC_START_BURST_US, NEC_START_BURST_US)

    def test_the_band_is_the_allowed_deviation(self):
        expected = 1000
        limit = expected * NEC_ALLOWED_DEVIATION_PERCENT

        assert pulse_us_valid(expected + limit - 1, expected)
        assert pulse_us_valid(expected - limit + 1, expected)

    def test_the_band_excludes_its_own_edge(self):
        expected = 1000
        limit = expected * NEC_ALLOWED_DEVIATION_PERCENT

        assert not pulse_us_valid(expected + limit, expected)
        assert not pulse_us_valid(expected - limit, expected)

    def test_a_zero_is_not_mistaken_for_a_one(self):
        zero = NEC_DATA_BURST_US + NEC_DATA_ZERO_US
        one = NEC_DATA_BURST_US + NEC_DATA_ONE_US

        assert not pulse_us_valid(zero, one)
        assert not pulse_us_valid(one, zero)

    def test_a_repeat_start_is_not_mistaken_for_a_data_start(self):
        assert not pulse_us_valid(NEC_START_REPEAT_US, NEC_START_DATA_US)
        assert not pulse_us_valid(NEC_START_DATA_US, NEC_START_REPEAT_US)


class TestCountConversions:
    """The counters run down from their timeout, offset by the program's setup delay."""

    def test_a_timeout_count_is_zero_length(self):
        # Five counts of setup delay are added back by the conversion
        assert count_to_burst_us(BURST_COUNT_TIMEOUT + 5) == 0
        assert count_to_idle_us(IDLE_COUNT_TIMEOUT + 5) == 0

    def test_counters_are_sized_from_their_bit_widths(self):
        assert BURST_COUNT_TIMEOUT == (2 ** 14) - 1
        assert IDLE_COUNT_TIMEOUT == (2 ** 13) - 1

    def test_a_count_step_is_one_microsecond(self):
        # The PIO runs at 2MHz and each loop takes two cycles
        assert count_to_burst_us(1000) - count_to_burst_us(1001) == 1
        assert count_to_idle_us(1000) - count_to_idle_us(1001) == 1

    def test_a_burst_count_converts_to_its_microseconds(self):
        count = BURST_COUNT_TIMEOUT + 5 - NEC_START_BURST_US
        assert count_to_burst_us(count) == NEC_START_BURST_US

    def test_an_idle_count_converts_to_its_microseconds(self):
        count = IDLE_COUNT_TIMEOUT + 5 - NEC_START_DATA_US
        assert count_to_idle_us(count) == NEC_START_DATA_US

    def test_the_idle_counter_cannot_reach_the_data_lockout(self):
        # A lockout longer than the counter is what ends a received sequence
        from aye_arr.nec.common import NEC_DATA_LOCKOUT_US
        assert NEC_DATA_LOCKOUT_US > IDLE_COUNT_TIMEOUT + 5
