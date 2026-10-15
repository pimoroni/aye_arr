# Aye Arr - NEC Remote - Library Reference <!-- omit in toc -->

This is the library reference for the `NEC Remote` component of the Aye Arr MicroPython library.


## Table of Content <!-- omit in toc -->

- [`RemoteDescriptor` Reference](#remotedescriptor-reference)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)
  - [Named Tuples](#named-tuples)
- [Supplied Remotes](#supplied-remotes)


## `RemoteDescriptor` Reference

### Constants

* `NAME` = `"Unknown"`
* `ADDRESS` = `0x00`
* `BUTTON_CODES` = `{}`
* `NUMBERS` = `{}`

### Variables

```python
on_known: callable = None
on_any: callable = None
```

### Functions

```python
# Initialisation
RemoteDescriptor()

# Binding
bind(name: str,
     on_press: callable,
     on_short: callable=None,
     on_repeat: callable=True,
     on_release: callable=None) -> None
bind_code(code: int,
          on_press: callable,
          on_short: callable=None,
          on_repeat: callable=True,
          on_release: callable=None) -> None

unbind(name: str) -> None
unbind_code(code: int) -> None

# Accessor
button(code: int) -> ButtonCallbacks
```

Leaving `on_repeat` as `True` repeats the press action for as long as the button
is held. Pass a callable to act differently on a repeat, or `None` to ignore
repeats. `on_short` replaces `on_release` when the button is let go before a
repeat carries it past `NECRemoteReceiver.SHORT_RELEASE_MS`, which is what
separates a short press from a hold.

### Named Tuples

```python
ButtonCallbacks(
     on_press: callable
     on_short: callable
     on_repeat: callable
     on_release: callable
)
```


## Supplied Remotes

Three `RemoteDescriptor` subclasses are supplied, each filling in `NAME`,
`ADDRESS` and `BUTTON_CODES` for a physical remote. Their button names are the
keys of that remote's `BUTTON_CODES`, listed in its module.

| Class | Address | Module | Numbers |
| ----- | ------- | ------ | ------- |
| `PimoroniRemote` | `0x00` | [pimoroni.py](/aye_arr/nec/remotes/pimoroni.py) | Yes |
| `ArgonRemote` | `0x00` | [argon.py](/aye_arr/nec/remotes/argon.py) | No |
| `LGRemote` | `0x04` | [lg.py](/aye_arr/nec/remotes/lg.py) | Yes |

`NUMBERS` maps a remote's digit button names to their values, for entering a
number a digit at a time. It is empty on a remote without digit buttons.

```python
KNOWN_REMOTES = (ArgonRemote, PimoroniRemote, LGRemote)
```

`NECRemoteReceiver` consults `KNOWN_REMOTES` when it receives a code from an
unbound address, so it can suggest which remote the code came from. Two supplied
remotes share address `0x00`, so binding both to one receiver needs
`bind(..., force=True)`.
