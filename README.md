<p align="center" >
<img src="http://bluz.io/static/img/logo.png" alt="Bluz" title="Bluz">
</p>

Bluz Command Line Interface
==========
Bluz is a Development Kit (DK) that implements the Wiring language and talks to the [Particle](https://www.particle.io/) cloud through Bluetooth Low Energy. It can be accessed through a REST API and programmed from a Web IDE.

The bluz Command Line Interface (CLI) provides a tool to talk to and provision bluz DK enabled hardware.

## Installation

You must first make sure you have python 2.7 and pip installed. Once you do, you can install the CLI with pip:

```sh
pip install git+https://github.com/bluzDK/bluz-cli.git
```

## Commands

### Provision

**NOTE:** This command is currently in Beta

Provisions a PCB that uses the nrf51822 for the Particle cloud. This command will flash the necessary ID and keys to the device, and will add the device ID of the board to the Particle cloud. It will then flash the latest bluz DK production firmware to the board.

The provision command should only be used on hardware that is custom built from the bluz designs. It is NOT needed for standard boards that are purchased and shipped from bluz.

Further, the provision command requires an API key that can only be obtained from bluz. If you wish to build a board from the bluz designs and provion it for the Particle cloud, please contact the bluz team at hello@bluz.io.

The provision command requires a few external pieces and libraries, namely:
- Adalink, a third party python library for programming nrf51822 hardware. Detailed instructions for installation can be found [here](https://github.com/adafruit/Adafruit_Adalink)
- A programmer, a JLink programmer or an STLInk v2 are recomended.
- If using STLink, you must install OpenOCD, this is explained in the Adalink documentation.

Once all the pieces are installed, you need to hook up your programmer to the [SWD pins](http://docs.bluz.io/hardware/dk/#pinout) on your PCB. You also need to hook up a USB Serial adapter to the TX/RX pins.

To test that your dependencies are met, you can use the following command:

```
adalink nrf51822 --programmer <either jlink or stlink> --info
```

This will output the information on your board if you have succesfully installed the dependencies, or an error otherwise.

Once your dependencies are installed, you can provision a board as so:

```
bluz provision -p <either jlink or stlink> -s <COM port of the Serial Interfact to bluz> -a <API Key> -i <Product ID>
```

For example, if the programmer were STLink, and COM port was COM3, the API Key was 123, and the product ID were 103 (bluz DK), the command would be:

```
bluz provision -p stlink -s COM3 -a 123 -i 103
```

Once you start the command, the programmer will obtain the device ID from the board and send to to a bluz REST API for processing. The command will then flash down the device ID, keys, and other items to the bluz board for processing. Once all items on the bluz board have been processed, the latest production firmware will be flashed.

The command can take 30-40 seconds to complete. The device, if equipped with an RGB LED, will flash multiple times during the process.


