# Aye Arr - Library Reference <!-- omit in toc -->

Aye Arr is a Micropython library for sending and receiving infrared remote signals on Raspberry Pi Pico/RP boards. It uses the RP's PIO to handle the timing of IR pulses.

## Table of Content <!-- omit in toc -->

It can be used at a base level to send arbitary IR signals, up to emulating specific remotes.



## Sending Your First Code

```python
import time
from aye_arr.nec import NECSender
```

```python
IR_TX_PIN = 0
sender = NECSender(IR_TX_PIN, 0, 0)
```

```python
try:
    sender.start()

    while True:
        sender.send_code(0xDEADBEEF)
        time.sleep(1)

finally:
    sender.stop()
```
examples/nec/send/send_code.py


## Receiving Your First Code

```python
import aye_arr.logging as logging
from aye_arr.nec import NECReceiver
```

```python
IR_RX_PIN = 26          # The pin to listen for IR pulses on
receiver = NECReceiver(IR_RX_PIN, 1, 0, logging_level=logging.LOG_INFO)

try:
    receiver.start()

    while True:
        receiver.decode()

finally:
    receiver.stop()
```

examples/nec/receive/receive_listen.py

## Emulating a Remote Control

The typical way the library will be used is via the RemoteDescriptor.

A RemoteDescriptor is, as the name implies, a description of a remote. It includes its address, button codes, and user friendly names to aid in debugging. Its purpose is to allow button actions such as press, release, and repeat, to be bound to callback functions within a users code, taking out the complexity of decoding the data from an IR signal itself.