# selectronic-bridges
Efforts to expose Selectronic SP PRO hybrid inverter data in HomeKit and other home automation frameworks, and collect it in InfluxDB for visualisation via Grafana dashboards.

## Selectronic SP PRO 2i to Apple HomeKit bridge

### Initial set-up of your Raspberry Pi (RPi) server

1. Use a 64-bit capable Rasperry Pi (RPi): an RPi 3 model B, RPi 4 model B or an RPi Zero 2 (**not** an RPi Zero W which is only 32-bit)
1. Download and install the [Raspberry Pi Imager app](https://www.raspberrypi.com/software/) on your computer
1. Insert the micro SD card you will be using for the RPi (32GB or larger recommended) into the SD card reader slot or adapter on your computer (you will probably need to use a microSD-to-SD carrier card).
1. Open the Raspberry Pi Imager app and select the Raspberry Pi OS Lite (64-bit) operating system (under the Raspberry Pi OS (other) submenu). Select your micro SD card target media. In settings (click on cog wheel icon), specify a host name (something like selectronic-bridge.local), a default account name and password for access over ssh - the account name `pi` is traditional and is used in these instructions (or use ssh keypair auth instead of a password if you prefer, but these instructions assume password authentication), and provide your local wi-fi details and password. Make sure you get the wi-fi details correct otherwise you won't be able to access the RPi (unless you plug in a screen and keybaord to allow you to correct them later. Write the image to the microSD card.
1. Place the microSD card in yoyr RPi and power it up. Confirm that it connects to your wi-fi and that you can log in to it using ssh (from your command line or terminal prompt on your local computer, issue somehing like `ssh pi@selectronic-bridge.local` or on Windows, use the [PuTTY ssh client](https://www.putty.org))
    1. If that doesn't work, then your local network router (which is probably your internet/wi-fi router) may not support _multicast DNS_ (mDNS), in which case you will need to find the IP address which your RPi server has been issued via DCHP by your router. Use the configuration interface for your router to find the IP address allocated to your RPi, or use `nmap` or other network scanning utilities to determine its IP adress).
    1. While you are using the router configuration interface, also carry out the next step immediately below.
1. Using the configurartion or administration interface for your router, configure DCHP to permnanently assign the same IP address to your RPi server. You may find these settings under _Advanced setting_ or similar. Exact details vary from router to router. 
1. Henceforth all commands should be issued at the RPi terminal prompt in your ssh client unless otherwise stated.
1. Update the RPi system with `sudo apt update` then `sudo apt full-upgrade`
1. Start the RPi configuration utility with `sudo raspi-config`. 
    1. Then under _System Option_ make sure _Network at Boot_ is set to **Yes** (this ensure the wi-fi and/or ethernet network connections are up before trying to start the InfluxDB and telegraf daemons)
    1. Under _Localisation Options_ make sure the **en_AU.UTF-8** locale is selected, that the _Timezone_ is correct and that the _WLAN Country_ is set to **AU**.
    1. Choose reboot when exiting the config utility, wait for the RPi o reboot, then reconnect to it via ssh as described above.
1. Install `git` with `sudo apt-get install git`
1. 



1. Clone the forked version of the `HAP-python` package (into the pi user home directory, so `cd ~` first if necessary): `gh repo clone timchurches/HAP-python`
1. Install `HAP-python` official version to get dependencies, then the forked version: 
```
sudo apt-get install python3-pip
sudo apt-get install libavahi-compat-libdnssd-dev
pip3 install HAP-python[QRCode]
cd HAP-python
sudo python3 setup.py install
```

1. To be continued....

## Telefraf and InfluxDB and Grafana

Detailed instructions will appear here, but basically following the instructions for installing  InfluxDb and Telegraf detailed [here](https://pimylifeup.com/raspberry-pi-influxdb/) and [here](https://nwmichl.net/2020/07/14/telegraf-influxdb-grafana-on-raspberrypi-from-scratch/)

11. Install the influxdb and grafana repository keys:
```
curl https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdb-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
curl -sL https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
```

12. Install influxdb, telegraf and grafana
```
sudo apt-get install -y grafana influxdb2 telegraf
sudo systemctl unmask influxd
sudo systemctl enable influxd
sudo systemctl unmask telegraf
sudo systemctl enable telegraf
sudo systemctl unmask grafana-server
sudo systemctl enable grafana-server
```

13. Start the influxdb, telegraf and grafana daemons (services) and check their status. Later we will tweak their systemd settings to ensure they restart themselves if they fall over.

```
sudo systemctl start influxdb grafana-server telegraf
sudo systemctl status influxdb
sudo systemctl status telegraf
sudo systemctl status grafana-server
```

That should take you to the influxdb command prompt. Exit by typing `exit`.


## TP-Link

Leverage https://github.com/softScheck/tplink-smartplug/blob/master/tplink_smartplug.py
