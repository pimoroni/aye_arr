# Aye Arr - Pulse Receive - MicroPython Examples <!-- omit in toc -->

These are MicroPython examples for using the `Pulse` layer of Aye Arr to read raw infrared pulses, without a protocol on top. Use these to decode a remote the NEC layer does not cover, or to see what a receiver is picking up.

`PulseReceiver` gathers pulses until the receiver goes quiet, then hands the sequence to its `__analyse` function. Both examples subclass it and define their own, as the NEC layer does.

- [Examples](#examples)
  - [Receive Pulses](#receive-pulses)
  - [Receive Unfiltered](#receive-unfiltered)


## Examples

### Receive Pulses
[receive_pulses.py](receive_pulses.py)

An example of how to read raw infrared pulses.

Each sequence received is printed with its length, along with the burst and idle durations of its first few pulses.


### Receive Unfiltered
[receive_unfiltered.py](receive_unfiltered.py)

How the pulse filter changes what a sequence looks like.

`decode` merges any burst or idle shorter than its threshold into the pulse beside it, recovering data a stray blip would otherwise spoil, while `decode_no_filter` reports the pulses as they arrived. Switching between the two against the same remote shows how many pulses the filter accounts for.
