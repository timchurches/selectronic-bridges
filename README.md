# selectronic-home-automation-bridges
Efforts to expose Selectronic SP PRO hybrid inverter data in HomeKit and other home automation frameworks .

## Selectronic SP PRO 2i to Apple HomeKit bridge

1. Use a 64-bit capable Rasperry Pi (RPi): an RPi 3, RPi 4 or an RPi Zero 2 (not an RPi Zero W which is only 32-bit)
2. Download and install the Raspberry Pi Imager app on your computer
3. Select the Raspberry Pi OS Lite (64-bit) operating system (under the Raspberry Pi OS (other) submenu). Select your micro SD card target media. In settings, specify a host name (something like selectronic-homekit-bridge.local), a default account name and password for access over shh (or use ssh keypair auth if you prefer), and provide your local wi-fi details and password. Write the image to the microSD card.
4. Place the microSD card in yoyr RPi and power it up. Confirm that it connects to your wi-fi and that you can log in to it using ssh.
5. Update the system with `sudo apt update` then `sudo apt full-upgrade`
6. 
