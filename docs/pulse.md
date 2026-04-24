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
DEFAULT_FILTER_THRESHOLD_US = 200
```


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
