# pi-clock - A simple e-paper clock

The idea here is to run a simple wall clock. :-)

The display panel we're using is a [Waveshare 13.3" e-paper display](https://www.waveshare.com/13.3inch-e-Paper-HAT-K.htm). There's an [online hardware manual](https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)), as well as a checked-in [PDF manual](./13.3-inch-e-Paper-(K)-user-manual.pdf). The display driver is vendored from [the Waveshare repository](https://github.com/waveshareteam/e-Paper).

## System Settings

* Install the Japanese locale: `sudo dpkg-reconfigure locales`
  The clock displays the date in Japanese, using the `ja_JP.UTF8` locale.

* Enable SPI: `sudo raspi-config`, under Interfaces.
  This is needed for communication with the E-Paper display.

