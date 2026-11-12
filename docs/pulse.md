# Aye Arr - Pulse - Library Reference <!-- omit in toc -->

This is the library reference for the `Pulse` component of the Aye Arr MicroPython library.


## Table of Content <!-- omit in toc -->

- [`PulseSender` Reference](#pulsesender-reference)
  - [Functions](#functions)
- [`pulse.receive` Reference](#pulsereceive-reference)
  - [Constants](#constants)
- [`PulseReceiver` Reference](#pulsereceiver-reference)
  - [Functions](#functions-1)


## `PulseSender` Reference

### Functions

```python
# Initialisation
PulseSender(pin_num: int,
            pio: int,
            sm: int,
            carrier_freq: int | float,
            debug_burst_pin: int=None,
            debug_send_pin: int=None,
            debug_wait_pin: int=None,
            stalled_wait: bool=True)

# Interaction
start() -> None
stop() -> None

# Sending
send(burst_us: int, idle_us: int) -> None
wait_for_send() -> None
```

## `pulse.receive` Reference

### Constants

```python
MAX_BUFFER = 1024
RING_COUNTS = 256
DEFAULT_FILTER_THRESHOLD_US = 200
```

`start()` claims a DMA channel, which copies each pulse count off the state
machine as it arrives, and `stop()` frees it. No code has to run for a count to
be kept, so a press is received whole even while the program is busy, such as
sending a frame to a screen. `RING_COUNTS` is how many counts can wait between
calls to `decode`, several presses' worth. Calling it too infrequently loses
the sequence the oldest counts belonged to.

Where every DMA channel is taken, or the port has no `rp2.DMA`, the receiver
takes the counts from an interrupt instead. `MAX_BUFFER` is then how many can
wait between calls to `decode`, and calling it too infrequently discards the
oldest. An interrupt waits for other code to finish, so a long-running call can
leave the state machine's FIFO full and the press it was receiving incomplete.


## `PulseReceiver` Reference

### Functions

```python
# Initialisation
PulseReceiver(pin_num: int,
              pio: int,
              sm: int,
              debug_pin_base: int=None,
              debug_blip_pin: int=None)

# Interaction
start() -> None
stop() -> None
reset() -> None

# Receiving
decode(filter_threshold: int=DEFAULT_FILTER_THRESHOLD_US) -> None
decode_no_filter() -> None
```
