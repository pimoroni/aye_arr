# Pimoroni Tiny FX - Library Reference <!-- omit in toc -->

This is the library reference for the [Pimoroni Tiny FX](https://shop.pimoroni.com/products/tinyfx), a LED effects controller, powered by the Raspberry Pi RP2040.


## Table of Content <!-- omit in toc -->


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
          on_short: callable=None
          on_repeat: callable=True,
          on_release: callable=None)

unbind(name: str) -> None
unbind_code(code: int) -> None

# Accessor
button(code: int) -> ButtonCallbacks
```

### Named Tuples

```python
ButtonCallbacks(
     on_press: callable
     on_short: callable
     on_repeat: callable
     on_release: callable
)
```