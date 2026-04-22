# Pimoroni Tiny FX - Library Reference <!-- omit in toc -->

This is the library reference for the [Pimoroni Tiny FX](https://shop.pimoroni.com/products/tinyfx), a LED effects controller, powered by the Raspberry Pi RP2040.


## Table of Content <!-- omit in toc -->



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

## `PulseReceiver` Reference

### Constants

`DEFAULT_FILTER_THRESHOLD_US` = `200`

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
