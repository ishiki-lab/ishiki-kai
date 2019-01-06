# lrpi_display

THis LushRoom Pi module displays diagnostic information on the display.

It displays the following information:

* host name,
* time zone,
* MAC address and IP address of the physical network adapters,
* current time.

If it finds images in the `/media/usb/Images` folder, it puts them randomly as background.
If it finds a logo.png image in the `/media/usb/Images` folder, it displays it at the top of the screen.

As it is intended to display on a Raspberry Pi 3.5" touch screen "hat", it is recommended to format the images with 480x320 pixels dimensions 
and the logo with 480x80 pixels dimensions.

## Reference documentation for Raspberry Pi touchscreens

[Generic reference documentation for screen drivers and calibration](http://www.circuitbasics.com/raspberry-pi-touchscreen-calibration-screen-rotation/)

[Touchscreen pygame tips from Adafruit](https://learn.adafruit.com/adafruit-2-4-pitft-hat-with-resistive-touchscreen-mini-kit/pitft-pygame-tips)

[KeDei Touchscreen kernel modules recompilation](https://johan.ehnberg.net/raspberry-pi-tft-kedei-3-5-touchscreen-v2/)

[KeDei Touchscreen kernel patch](https://github.com/zefj/kedei2-patchfiles)

[Alternative kernel module for ILI9341 based displays](https://github.com/juj/fbcp-ili9341)
