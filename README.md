# Aye Arr<!-- omit in toc -->

## An infrared TX/RX Micropython library for Raspberry Pi Pico/RP boards<!-- omit in toc -->

This repository is home to the Aye Arr library.

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/aye_arr/build.yml?branch=main&label=Build)](https://github.com/pimoroni/aye_arr/actions/workflows/build.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pimoroni/aye_arr)](https://github.com/pimoroni/aye_arr/releases/latest/)

## Introduction

Aye Arr is a Micropython library for sending and receiving infrared remote signals on Raspberry Pi Pico/RP boards. It uses the RP's PIO to handle the timing of IR pulses.

The library consists of two layers:
* `Pulse` - the underlying creation and decoding of infrared pulses.
* `NEC` - a protocol layer for acting as or listening for consumer remote controls.

## Hardware

To use Aye Arr in a project, for transmission you need an infrared LED (with suitable current limiting resistor), and for receiving you need an infrared photodiode connected to a demodulator IC, such as our IR Stick ().


## Examples

There are examples provided for a number of Pimoroni boards, though most will be usable on other RP products too with a few pin changes:

* [Examples: NEC](/examples/nec/README.md)

* [Examples: Motor Shim](/examples/motor_shim/README.md)
* [Examples: Tiny 2350](/examples/tiny_2350/README.md)
* [Examples: Plasma](/examples/plasma/README.md)

## Documentation

To take Aye Arr further, the full API documentation can be found at:

* [Library Reference](/docs/reference.md)
