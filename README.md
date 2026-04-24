# Aye Arr<!-- omit in toc -->

## An infrared TX/RX MicroPython library for Raspberry Pi Pico/RP boards<!-- omit in toc -->

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/aye_arr/build.yml?branch=main&label=Build)](https://github.com/pimoroni/aye_arr/actions/workflows/build.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pimoroni/aye_arr)](https://github.com/pimoroni/aye_arr/releases/latest/)


- [Introduction](#introduction)
- [Hardware](#hardware)
- [Installing](#installing)
  - [mip](#mip)
- [Examples](#examples)
- [Documentation](#documentation)


## Introduction

Aye Arr is a MicroPython library for sending and receiving infrared remote signals on Raspberry Pi Pico/RP boards. It uses the RP's PIO to handle the timing of IR pulses.

The library consists of two layers:
* `NEC` - a protocol layer for acting as or listening for consumer remote controls.
* `Pulse` - the underlying creation and decoding of infrared pulses with a carrier frequency.


## Hardware

For transmission projects using Aye Arr you need an infrared LED (with suitable current limiting resistor) connected up to a GPIO pin of your RP board.
For receiving projects using Aye Arr you need an infrared photodiode with a 38KHz receiver module, such as our [IR Receiver Stick](https://shop.pimoroni.com/products/infrared-receiver-remote), connected to a GPIO pin of your RP board.

<img src="https://cdn.shopify.com/s/files/1/0174/1800/files/ir-receiver-3.jpg" width="500">


## Installing

### mip

If your board is online and has `mip` you should be able to run:

```python
import mip
mip.install("github:org/pimoroni/aye_arr/package.json")
```

Otherwise, using Tools -> Manage Packages in Thonny, locate the
`aye_arr` package and install it as normal.

You can also install this library manually by copying the `aye_arr` directory in this repo to your board. To do this, click on the down arrow next to `<> Code`, click on `Download ZIP`, then unzip the file and copy the `aye_arr` folder within it over to your RP board via Thonny.


## Examples

There are a variety of examples to get you started with Aye Arr, located in the examples folder of this repository:

* [Examples](/examples/README.md)


## Documentation

To take Aye Arr further, function references for the Aye Arr library can be found at:

* [NEC Reference](/docs/nec.md)
* [NEC Remote Reference](/docs/remote.md)
* [Pulse Reference](/docs/pulse.md)
