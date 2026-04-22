# Aye Arr - NEC Receive - MicroPython Examples <!-- omit in toc -->

These are micropython examples for using Aye Arr with the NEC protocol to receive infrared signals.

- [Examples](#examples)
  - [Listen](#listen)
  - [Receive Code](#receive-code)
  - [Receive Code with Repeat](#receive-code-with-repeat)
  - [Receive Address \& Command](#receive-address--command)
  - [Receive Known Address \& Command](#receive-known-address--command)
- [Remote Examples](#remote-examples)
  - [Individual Callbacks](#individual-callbacks)
  - [Shared Callbacks](#shared-callbacks)
  - [Variable Adjustment](#variable-adjustment)
  - [Number Entering](#number-entering)
  - [Binding Options](#binding-options)
  - [Binding Timings](#binding-timings)


## Examples

### Listen
[receive_listen.py](receive_listen.py)

An example of how to listen for any NEC infrared signals.


### Receive Code
[receive_code.py](receive_code.py)

Listen for NEC infrared codes, and act on them. Any code that is received gets printed out.


### Receive Code with Repeat
[receive_code_with_repeat.py](receive_code_with_repeat.py)

Listen for NEC infrared codes and their repeats, and act on them. Any code that is received gets printed out.


### Receive Address & Command
[receive_addr_cmd.py](receive_addr_cmd.py)

Listen for NEC infrared commands sent to an address, and act on them. Any command that is received gets printed out.


### Receive Known Address & Command
[receive_addr_cmd_known.py](receive_addr_cmd_known.py)

Listen for NEC infrared commands sent to an address, and act on only ones we are interested in. The four bound commands that are received get printed out.


## Remote Examples

### Individual Callbacks
[remote/individual_callbacks.py](remote/individual_callbacks.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and perform individual actions for the ones we are interested in, via separate functions.


### Shared Callbacks
[remote/shared_callbacks.py](remote/shared_callbacks.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and perform actions for the ones we are interested in, via a shared function with separate data.


### Variable Adjustment
[remote/variable_adjust.py](remote/variable_adjust.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and use them to change the values of local "volume" and "brightness" variables.


### Number Entering
[remote/number_entering.py](remote/number_entering.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and use them to enter a "channel" number into the system. Each number button on the remote adds a digit to the current number.


### Binding Options
[remote/binding_options.py](remote/binding_options.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and show how
different actions can be used to each button behave differently.


### Binding Timings
[remote/binding_timings.py](remote/binding_timings.py)

Listen for NEC infrared commands sent from a Pimoroni remote, and have a single
button perform different actions, including timing information.
