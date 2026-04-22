# Pimoroni Tiny FX - Library Reference <!-- omit in toc -->

This is the library reference for the [Pimoroni Tiny FX](https://shop.pimoroni.com/products/tinyfx), a LED effects controller, powered by the Raspberry Pi RP2040.


## Table of Content <!-- omit in toc -->



## `PulseSender` Reference

### Functions

```python
# Initialisation
NECSender(pin_num: int,
          pio: int,
          sm: int,
          debug_burst_pin: int=None,
          debug_send_pin: int=None,
          debug_wait_pin: int=None,
          logging_level: int=logging.LOG_WARN)

# Interaction
start() -> None
stop() -> None

# Sending
send_remote(remote_type: type[RemoteDescriptor], name: str) -> None
send_addr_cmd(addr: int, cmd: int) -> None
send_code(code: int) -> None
send_repeat() -> None
wait_for_send() -> None
```

## `NECReceiver` Reference

### Functions

```python
# Initialisation
NECReceiver(pin_num: int,
            pio: int,
            sm: int,
            debug_pin_base: int=None,
            debug_blip_pin: int=None,
            debug_error_pin: int=None,
            logging_level: int=logging.LOG_WARN)

# Binding
bind(on_press: callable,
     on_repeat: callable=True,
     on_release: callable=None) -> None

# Interaction
start() -> None
stop() -> None
reset() -> None

# Receiving
decode(filter_threshold: int=DEFAULT_FILTER_THRESHOLD_US) -> None
decode_no_filter() -> None
```


## `NECRemoteReceiver` Reference

### Constants

`SHORT_RELEASE_MS` = `250`

### Functions

```python
# Initialisation
NECRemoteReceiver(pin_num: int,
                  pio: int,
                  sm: int,
                  extended_addresses: int=False,
                  debug_pin_base: int=None,
                  debug_blip_pin: int=None,
                  debug_error_pin: int=None,
                  logging_level: int=logging.LOG_WARN)

# Binding
bind(remote_descriptor: RemoteDescriptor, force: bool=False) -> None

# Interaction
start() -> None
stop() -> None
reset() -> None

# Receiving
decode(filter_threshold: int=DEFAULT_FILTER_THRESHOLD_US) -> None
decode_no_filter() -> None
```
