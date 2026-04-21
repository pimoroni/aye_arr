# Aye Arr - NEC Receiving - Micropython Examples <!-- omit in toc -->

These are micropython examples for using Aye Arr with the NEC protocol to receive infrared signals.

- [Examples](#examples)
  - [Send Code](#send-code)
  - [Send Code With Repeat](#send-code-with-repeat)
  - [Send Addr Cmd](#send-addr-cmd)
  - [Send Addr Cmd With Repeat](#send-addr-cmd-with-repeat)
  - [Send Remote](#send-remote)
  - [Send Remote With Repeat](#send-remote-with-repeat)


## Examples

### Receive Listen
[receive_listen.py](receive_listen.py)

An example of how to listen for infrared codes.


### Receive Code
[receive_code.py](receive_code.py)

Listen for infrared codes, and act on them. Any code that is received gets printed out.


### Receive Code with Repeat
[receive_code_with_repeat.py](receive_code_with_repeat.py)

Listen for infrared codes and their repeats, and act on them. Any code that is received gets printed out.


### Receive Addr Cmd
[receive_add_cmd.py](receive_addr_cmd.py)

Listen for infrared commands sent to an address, and act on them. Any command that is received gets printed out.


### Receive Addr Cmd Known
[receive_addr_cmd_known.py](receive_addr_cmd_known.py)

Listen for infrared commands sent to an address, and act on only ones we are interested in. The four known commands that are received get printed out.


### Receive Remote
[receive_remote.py](receive_remote.py)

Listen for infrared commands sent to an address, and act uniquely on only the ones we are interested in. The four known commands that are received get a separate print-out.


### Receive Remote Shared
[receive_remote_shared.py](receive_remote_shared.py)

Listen for infrared commands sent to an address, and act uniquely on only the ones we are interested in. The four known commands that are received get passed to a shared function with separate data to change their final print-out.
