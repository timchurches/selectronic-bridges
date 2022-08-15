# selectronic-bridges
Efforts to expose Selectronic SP PRO hybrid inverter data in HomeKit and other home automation frameworks, and collect it in InfluxDB for visualisation via Grafana dashboards.

## Selectronic SP PRO 2i to Apple HomeKit bridge

1. Use a 64-bit capable Rasperry Pi (RPi): an RPi 3, RPi 4 or an RPi Zero 2 (not an RPi Zero W which is only 32-bit)
2. Download and install the Raspberry Pi Imager app on your computer
3. Insert the micro SD card you will be using for the RPi (32GB or larger recommended) into the SD card reader slot or adapter on your computer (you will probably need to use a microSD-to-SD carrier card).
4. Open the Raspberry Pi Imager app and select the Raspberry Pi OS Lite (64-bit) operating system (under the Raspberry Pi OS (other) submenu). Select your micro SD card target media. In settings (click on cog wheel icon), specify a host name (something like selectronic-bridge.local), a default account name and password for access over ssh - the account name pi is traditional and is used in these instructions (or use ssh keypair auth instead of a password if you prefer, but these instructions assume password authentication), and provide your local wi-fi details and password. Make sure you get the wi-fi details correct otherwise you won't be able to access the RPi (unless you plug in a screen and keybaord. Write the image to the microSD card.
5. Place the microSD card in yoyr RPi and power it up. Confirm that it connects to your wi-fi and that you can log in to it using ssh.
6. Update the system with `sudo apt update` then `sudo apt full-upgrade`
7. Install `git`: `sudo apt-get install git`
8. Clone the forked version of the `HAP-python` package (into the pi user home directory, so `cd ~` first if necessary): `gh repo clone timchurches/HAP-python`
9. Install `HAP-python` official version to get dependencies, then the forked version: 
  > `sudo apt-get install python3-pip`
  > `sudo apt-get install libavahi-compat-libdnssd-dev`
  > `pip3 install HAP-python[QRCode]`
  > `cd HAP-python`
  > `sudo python3 setup.py install`
10. To be continued....

## Telefraf and InfluxDB and Grafana

Detailed instructions will appear here, but basically following the instructions for installing  InfluxDb and Telegraf detailed [here](https://pimylifeup.com/raspberry-pi-influxdb/_ and [here](https://nwmichl.net/2020/07/14/telegraf-influxdb-grafana-on-raspberrypi-from-scratch/)

## TP-Link

Leverage https://github.com/softScheck/tplink-smartplug/blob/master/tplink_smartplug.py
