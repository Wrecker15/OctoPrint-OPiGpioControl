# OctoPrint OPi GPIO Control

GPIO Control adds a sidebar with on/off buttons. You can add as many buttons as you want that will control each device connected to your Orange Pi.

Very useful if you want to add some electronic/improvements to your printer.

![OPiGpioControl](assets/sidebar.png)
![OPiGpioControl](assets/settings.png)

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/TTLC198/OctoPrint-OPiGpioControl/archive/master.zip

## Configuration

Just add correct GPIO configuration:

- select icon using icon picker (or typing manually) for better identification
- type name for your device connected to GPIO
- type pin number according to BCM numeration - for more details please [visit this page](https://pinout.xyz/)
- select if device is driven for low or high state of GPIO
    - _active high_ means that device is **on for high state** of GPIO and **off for low state**
    - _active low_ means that device is **on for low state** of GPIO and **off for high state**
- select if device should be on or off by default eg. after startup

## Authors

The main version of the plugin for Raspberry Pi was written by catgiggle, modified to work with Orange Pi boards by TTLC198.
