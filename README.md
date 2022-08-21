# selectronic-bridges
Efforts to expose Selectronic SP PRO hybrid inverter data in HomeKit and other home automation frameworks, and collect it in InfluxDB for visualisation via Grafana dashboards.

## Selectronic SP PRO 2i to Apple HomeKit bridge

### Initial set-up of your Raspberry Pi (RPi) server

1. Use a 64-bit capable Rasperry Pi (RPi): an RPi 3 model B, RPi 4 model B or an RPi Zero 2 (**not** an RPi Zero W which is only 32-bit)
1. Download and install the [Raspberry Pi Imager app](https://www.raspberrypi.com/software/) on your computer
1. Insert the micro SD card you will be using for the RPi (32GB or larger recommended) into the SD card reader slot or adapter on your computer (you will probably need to use a microSD-to-SD carrier card).
1. Open the Raspberry Pi Imager app and select the Raspberry Pi OS Lite (64-bit) operating system (under the Raspberry Pi OS (other) submenu). Select your micro SD card target media. In settings (click on cog wheel icon), specify a host name (something like selectronic-bridge.local), a default account name and password for access over ssh - the account name `pi` is traditional and is used in these instructions (or use ssh keypair auth instead of a password if you prefer, but these instructions assume password authentication), and provide your local wi-fi details and password. Make sure you get the wi-fi details correct otherwise you won't be able to access the RPi (unless you plug in a screen and keybaord to allow you to correct them later. Write the image to the microSD card.
1. Place the microSD card in yoyr RPi and power it up. Wait a few minutes while the first-time boot process completes, then confirm that your RPi has connected to your wi-fi and that you can log in to it using ssh (from your command line or terminal prompt on your local computer, issue somehting like `ssh pi@selectronic-bridge.local` or on Windows, use the [PuTTY ssh client](https://www.putty.org))
    1. If that doesn't work, then your local network router (which is probably your internet/wi-fi router) may not support _multicast DNS_ (mDNS), in which case you will need to find the IP address which your RPi server has been issued via DCHP by your router. Use the configuration interface for your router to find the IP address allocated to your RPi, or use `nmap` or other network scanning utilities to determine its IP address).
    1. While you are using the router configuration interface, also carry out the next step immediately below.
1. Using the configurartion or administration interface for your router (exact details vary from router to router):
    1. configure DCHP to permnanently assign a fixed IP address to your RPi server. You may find these settings under _Advanced setting_ or similar.
    1. determine the IP address of your local Select.live interface (the IP address it uses is also shown on the LCD screen on the Select.live device) and note it down, and similarly configure DCHP to permnanently assign a fixed IP address to your local Select.live interface device.
1. Download a zip file of this repository by clicking on the Code button at the upper right and choosing Zip file. Save the zip file locally on your computer and unzip it.

1. Henceforth all commands should be issued at the RPi terminal prompt in your ssh client unless otherwise stated.
1. Update the RPi system with:

```
sudo apt update
sudo apt full-upgrade
```

1. Start the RPi configuration utility with `sudo raspi-config`. 
    1. Then under _System Option_ make sure _Network at Boot_ is set to **Yes** (this ensure the wi-fi and/or ethernet network connections are up before trying to start the InfluxDB and telegraf daemons)
    1. Under _Localisation Options_ make sure the **en_AU.UTF-8** locale is selected and is the default, that the _Timezone_ is correct and that the _WLAN Country_ is set to **AU**.
    1. Choose reboot when exiting the config utility, wait for the RPi o reboot, then reconnect to it via ssh as described above.
1. Install `git` with `sudo apt-get install git` then configure it, replacing First_name, Last_name and the email address with your actual names and email address (in quotes as shown) (the email address you used to register with GitHub is the best one to use):

```
git config --global user.name "First_name Last_name"
git config --global user.email "my_name@example.com"
```

## Telefraf and InfluxDB and Grafana

Detailed instructions will appear here, but basically following the instructions for installing  InfluxDb and Telegraf detailed [here](https://pimylifeup.com/raspberry-pi-influxdb/) and [here](https://nwmichl.net/2020/07/14/telegraf-influxdb-grafana-on-raspberrypi-from-scratch/)

1. Install the influxdb and grafana repository keys (ignore the warning about `apt-key add` being deprecated):

```
curl https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdb-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
curl -sL https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
```

1. Install influxdb, telegraf and grafana

```
sudo apt-get install -y grafana influxdb telegraf
sudo systemctl unmask influxdb
sudo systemctl enable influxdb
sudo systemctl unmask telegraf
sudo systemctl enable telegraf
sudo systemctl enable grafana-server
```


1. Start InfluxDB

```
sudo systemctl start influxdb 
# check if running
sudo systemctl status influxdb
```


1. Configure InfluxDB

    1. Invoke the influxdb command shell with the command : `influx`
    1. Issue the following commands, line-by-line, at the influx coammnd prompt, substituting a password of your choice for XXXXX below

```
create database selectronic
use selectronic
create user telegrafuser with password 'XXXXX' with all privileges
grant all privileges on selectronic to telegrafuser
create retention policy "forever" on "selectronic" duration INF replication 1 default
exit
```

1. Configure telegraf to collect data from your local Select.live interface device:
    1. Make sure you know the permanently assigned IP addess for you Select.live interface box (as detailed in the section on DCHP configuration above).
    1. Using a web browser, go to http://x.x.x.x/cgi-bin/solarmonweb/devices where x.x.x.x is the IP address of your local Select.live interface device
    1. You should see a page of data in JSON format. Keep that page open in a browser tab (you will need to copy-and-paste the **id** hash value shortly).
    1. Open the [telegraf.conf](https://github.com/timchurches/selectronic-bridges/blob/main/telegraf.conf) template file in another browser tab. Click on the **Raw** button to see it in raw form. Keep that tab open, you will shortly need to copy-and-paste it.
    1. In the RPi terminal client, issue the command `sudo mv /etc/telegraf/telegraf.conf /etc/telegraf/telegraf.conf_bak`
    1. Create a new, empty telegraf.conf file with  `sudo nano /etc/telegraf/telegraf.conf` 
    1. Copy-and-paste the entire contents of the telegraf.conf template file you opened in your web browser above into the empty telegraf.conf file on your RPi.
    1. Scroll to the section _## HTTP Basic Auth_ and replace the XXXXXXX with the password you specified for _telegrafuser_ in the InfluxDB  configuration steps above.
    1. Scroll down to the _[[inputs.http]]_ section and, in the line starting with _urls =_, replace the X.X.X.X with the IP address of your local Select.live interface device, and replace the XXXXXXXXXXXXXXX with the alphanumeric **id* hash string from the local Select.live device information page you opened in a browser tab a few steps above.
    1. Write the file to disc by pressing Ctrl-O (oh, not zero) then Enter, followed by Ctrl-X (note, that's the control key, not the command key on a Mac).
    
1. Start the telegraf data collection daemon:
    1. At the RPi terminal prompt, issue `sudo systemctl start telegraf`
    1. Check the status of teh daemon with `sudo systemctl status telegraf` - there should be no errors reported.
    
1. At this stage the telegraf daemon shoud be collecting data from your local Select.live device over your local network. Check this by starting the InfluxDB shell with `influx` and then issuing these commands:

```
use selectronic
select * from selectronic
```

You should see data. Try repeatedly issuing the command `select count(battery_soc) from selectronic` to show the number of rows in the database. Repeat the command (use up-arrow to recall it) every 15 seconds or so and you should see the count incrementing. When satisfied exit the InfluxDB shell with the command `exit`.

### Configure grafana

1. Start the _grafana-server_ daemon with `sudo systemctl start grafana-server`. Check that there are no errors with `sudo systemctl status grafana-server`.
1. In your web browser, open the _grafana_ page at [http://selectronic-bridge.local:3000/](http://selectronic-bridge.local:3000/). Note that if mDNS is not working on your LAN then you will need to substitute the IP address of your Rpi server for "selectronic-bridge.local" in the URL above.
1. Log in as _admin_, password _admin_. You will be asked to chnage the _admin_ password. You will then be at the _grafana_ home page.
1. Hover your mouse pointer over the config icon (cog wheel) on the left-hand side and choose _Data sources_. Click on _Add data source_ and then click on _InfluxDB_. 
1. In the _HTTP_ section, set _URL_ to http://localhost:8086/
1. Scroll down to _InfluxDB Details_ and set the parameters as follows:
    1. Database: selectronic
    1. User: telegrafuser
    1. Password: <substitute the password for the telegrafuser account which you created above>
    1. http method: GET
1. Click _Save & test_. You should see a confirmation that the datasource is accessible and working.
1. Return to the _grafana_ home page by clicking on the Grafana icon at the top on the left.

### Set-up the prototype Selectronic dashboard

1. In the Grafana page which you have open in your web browser, hover you mouse over the Dashboards icon (four small squares on the left) and choose _Import_. Click on _Upload JSON file_ and select the file _Selectronic_prototype_dashboard.json_ from the directory where you downloaded and unzipped the zip file for this repository. Click _Upload_.
1. You should be at the Options page for the dashboard definition to be imported. Change the InfluxDB field to _InfluxDB (default)_ and click import.
1. Voilà! You should see a dashboard displaying your local Selectronic parameters.
1. Set the refresh rate by clicking on the two-arrow-in-a-circle icon at the upper right and choose 15s. You can also put the display in kiosk mode using the upper right-most icon. You can copy the URL for that view and bookmark it or share it to go to exactly that view. However, you may wish to create a read-only user account for sharing purposes first. This will be documented below shortly.

## HomeKit bridge set-up

The following steps are only needed if you have Apple HomeKit home automation. The steps below are not yet fully documented so don't undertke them yet.

1. Clone the forked version of the `HAP-python` package (into the pi user home directory, so `cd ~` first if necessary): `gh repo clone timchurches/HAP-python`
1. Install `HAP-python` official version to get dependencies, then the forked version: 
```
sudo apt-get install python3-pip
sudo apt-get install libavahi-compat-libdnssd-dev
pip3 install HAP-python[QRCode]
cd HAP-python
sudo python3 setup.py install
```
## TP-Link

For future use, leverage https://github.com/softScheck/tplink-smartplug/blob/master/tplink_smartplug.py to provide direct load switching automation via the cheap TP-Link devices, without the need for Apple HomeKit of other home automation systems.

