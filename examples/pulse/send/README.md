# Aye Arr - Pulse Send - MicroPython Examples <!-- omit in toc -->

These are MicroPython examples for using the `Pulse` layer of Aye Arr to send raw infrared pulses, without a protocol on top. Use these to build a protocol of your own, or to reproduce a signal the NEC layer does not cover.

- [Examples](#examples)
  - [Send Pulse](#send-pulse)
  - [Send Sequence](#send-sequence)


## Examples

### Send Pulse
[send_pulse.py](send_pulse.py)

A barebones example of how to send an infrared pulse.

A pulse is a burst of the carrier frequency followed by a period of idle, both given in microseconds. The carrier frequency, the two durations, and the silence between each pulse can be adjusted.


### Send Sequence
[send_sequence.py](send_sequence.py)

Send a sequence of infrared pulses, as a protocol of your own.

The pulses are queued one after another so the PIO holds the timing between them, whatever the speed of the loop. The sequence sent is a start pulse followed by four data bits.
