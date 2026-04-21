# Aye Arr - NEC Sending - Micropython Examples <!-- omit in toc -->

These are micropython examples for using Aye Arr with the NEC protocol to send infrared signals.

- [Examples](#examples)
  - [Send Code](#send-code)
  - [Send Code With Repeat](#send-code-with-repeat)
  - [Send Addr Cmd](#send-addr-cmd)
  - [Send Addr Cmd With Repeat](#send-addr-cmd-with-repeat)
  - [Send Remote](#send-remote)
  - [Send Remote With Repeat](#send-remote-with-repeat)


## Examples

### Send Code
[send_code.py](send_code.py)

A barebones example of how to send an infrared code.

The chosen code is sent multiple times in bursts, followed by a period of silence. The number of codes per burst, as well as the burst and silence timings can be adjusted.


### Send Code With Repeat
[send_code_with_repeat.py](send_code_with_repeat.py)

How to send an infrared code, with repeats.

Repeats are used by remotes to signal that a button is being held down. These should be sent every 108ms to match the NEC protocol spec.


### Send Addr Cmd
[send_addr_cmd.py](send_addr_cmd.py)

Send an infrared command to an address.

The chosen command is sent to the address multiple times in bursts, followed by a period of silence. The number of codes per burst, as well as the burst and silence timings can be adjusted.


### Send Addr Cmd With Repeat
[send_addr_cmd_with_repeat.py](send_addr_cmd_with_repeat.py)

Send an infrared command to an address, with repeats.

Repeats are used by remotes to signal that a button is being held down. These should be sent every 108ms to match the NEC protocol spec.


### Send Remote
[send_remote.py](send_remote.py)

Send infrared commands as if the board was a remote control.

The chosen command is sent to the address multiple times in bursts, followed by a period of silence. The number of commands per burst, as well as the burst and silence timings can be adjusted.


### Send Remote With Repeat
[send_remote_with_repeat.py](send_remote_with_repeat.py)

Send infrared commands as if the board was a remote control, with repeats.

Repeats are used by remotes to signal that a button is being held down. These should be sent every 108ms to match the NEC protocol spec.

