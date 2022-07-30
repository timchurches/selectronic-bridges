# selectronic_hk_bridge.py
# written by Tim Churches
# copyright Tim Churches
# licensed under the GNU Public License V3

from pyhap.accessory import Accessory, Bridge
import pyhap.loader as loader
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR

import requests
import json
import time
import logging
import signal
import random

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")

# Constants for now
SELECT_LIVE_IP = 'x.x.x.x'
SYSTEM_ID = 'xxxxx'

class BatterySOC(Accessory):
	"""Implementation of a Selectronic SP PRO 2i battery state-of-charge sensor accessory."""

	category = CATEGORY_SENSOR  # This is for the icon in the iOS Home app.

	def __init__(self, *args, house_load_instance=None, solar_prod_instance=None, generator_status_instance=None, **kwargs):
	# def __init__(self, *args, generator_status_instance=None, **kwargs):
		"""Here, we just store a reference to the current state-of-charge characteristic and
		   add a method that will be executed every time its value changes.
		"""
		# If overriding this method, be sure to call the super's implementation first.
		super().__init__(*args, **kwargs)

		self.select_data_url = f'http://{SELECT_LIVE_IP}/cgi-bin/solarmonweb/devices/{SYSTEM_ID}/point'
		# add the house load class instance
		self.house_load_instance = house_load_instance
		# add the solar production class instance
		self.solar_prod_instance = solar_prod_instance
		# add the generator status class instance
		self.generator_status_instance = generator_status_instance
		# Add the services that this Accessory will support with add_preload_service here
		battery_soc = self.add_preload_service('HumiditySensor')
		battery_service = self.add_preload_service('BatteryService')
		self.battery_soc_char = battery_soc.configure_char('CurrentRelativeHumidity')
		self.battery_soc_active_char = battery_soc.configure_char('StatusActive')
		self.battery_soc_fault_char = battery_soc.configure_char('StatusFault')
		self.battery_service_battery_level_char = battery_service.configure_char('BatteryLevel')
		self.battery_service_charging_state_char = battery_service.configure_char('ChargingState', value = int(0))
		self.battery_service_status_low_battery_char = battery_service.configure_char('StatusLowBattery', value = int(0))
		# Having a callback is optional, but you can use it to add functionality.
		# self.battery_soc_char.setter_callback = self.battery_soc_changed


	def battery_soc_changed(self, value):
		"""This will be called every time the value of the CurrentRelativeHumidity
		   is changed. Use setter_callbacks to react to user actions, e.g. setting the
		   lights On could fire some GPIO code to turn on a LED (see pyhap/accessories/LightBulb.py).
		"""
		print('Battery level changed to: ', value)

	@Accessory.run_at_interval(60)  # Run this method every 60 seconds
	# The `run` method can be `async` as well
	def run(self):
		"""We override this method to implement what the accessory will do when it isstarted.
		   We retrieve the battery SOC from select.live every minute.
		"""
		try:
			sess = requests.Session()
			hfdata = sess.get(self.select_data_url)
			if hfdata.status_code == 200:
				hfdict = json.loads(hfdata.text)
				# print(hfdict)
				bat_soc = float(hfdict["items"]["battery_soc"])
				bat_w = float(hfdict["items"]["battery_w"])
				grid_w = float(hfdict["items"]["grid_w"])
				load_w = float(hfdict["items"]["load_w"])
				solarprod_w = float(hfdict["items"]["solarinverter_w"])
				# set battery SOC values
				self.battery_soc_char.set_value(bat_soc)
				self.battery_service_battery_level_char.set_value(int(bat_soc))
				if bat_soc < 40.0:
					bat_low = int(1)
				else:
					bat_low = int(0)
				if bat_w < 0:
					charging_state = int(1)
				else:
					charging_state = int(0)
				self.battery_service_charging_state_char.set_value(charging_state)
				self.battery_service_status_low_battery_char.set_value(bat_low)
				# set house load value
				self.house_load_instance.current_house_load = load_w
				# set solar production value
				self.solar_prod_instance.current_solar_prod = solarprod_w
				# set generator status
				if grid_w < -10.0:
					self.generator_status_instance.current_generator_status = True
				else:
					self.generator_status_instance.current_generator_status = False
				self.battery_soc_active_char.set_value(True)
				self.battery_soc_fault_char.set_value(int(0))
				self.generator_status_instance.current_generator_status_active = True
				self.generator_status_instance.current_generator_status_fault = int(0)
				self.house_load_instance.house_load_sensor_active = True
				self.house_load_instance.house_load_sensor_fault = int(0)
				self.solar_prod_instance.solar_prod_sensor_active = True
				self.solar_prod_instance.solar_prod_sensor_fault = int(0)
			else:
				print(hfdata.status_code)
				self.battery_service_charging_state_char.set_value(int(2))
				self.battery_soc_active_char.set_value(False)
				self.battery_soc_fault_char.set_value(int(1))
				self.house_load_instance.current_house_load = 0
				self.generator_status_instance.current_generator_status_active = False
				self.generator_status_instance.current_generator_status_fault = int(1)
				self.house_load_instance.house_load_sensor_active = False
				self.house_load_instance.house_load_sensor_fault = int(1)
				self.solar_prod_instance.solar_prod_sensor_active = False
				self.solar_prod_instance.solar_prod_sensor_fault = int(1)
		except BaseException as err:
			print(f"Unexpected {err=}, {type(err)=}")
			self.battery_service_charging_state_char.set_value(int(2))
			self.battery_soc_active_char.set_value(False)
			self.battery_soc_fault_char.set_value(int(1))
			self.generator_status_instance.current_generator_status_active = False
			self.generator_status_instance.current_generator_status_fault = int(1)
			self.house_load_instance.house_load_sensor_active = False
			self.house_load_instance.house_load_sensor_fault = int(1)
			self.solar_prod_instance.solar_prod_sensor_active = False
			self.solar_prod_instance.solar_prod_sensor_fault = int(1)
			pass

	# The `stop` method can be `async` as well
	def stop(self):
		"""We override this method to clean up any resources or perform final actions, as
		this is called by the AccessoryDriver when the Accessory is being stopped.
		"""
		print('Stopping accessory.')

class GeneratorStatus(Accessory):
	"""Generator status sensor."""

	category = CATEGORY_SENSOR

	def __init__(self,  *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_generator_status = False # stores current state
		self.current_generator_status_active = False 
		self.current_generator_status_fault = int(0)
		generator_status_sensor = self.add_preload_service('MotionSensor')
		self.generator_status_sensor_char = generator_status_sensor.configure_char('MotionDetected', setter_callback=self.set_gen_status)
		self.generator_status_sensor_active_char = generator_status_sensor.configure_char('StatusActive')
		self.generator_status_sensor_fault_char = generator_status_sensor.configure_char('StatusFault')

	def set_gen_status(self, value):
		logging.info("Generator status sensor: %s", value)

	@Accessory.run_at_interval(40)
	async def run(self):
		# print(self.current_generator_status)
		self.generator_status_sensor_char.set_value(self.current_generator_status)
		self.generator_status_sensor_active_char.set_value(self.current_generator_status_active)
		self.generator_status_sensor_fault_char.set_value(self.current_generator_status_fault)

class HouseLoad(Accessory):
	"""House load in watts"""

	category = CATEGORY_SENSOR

	def __init__(self,  *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_house_load = 0 # stores current state
		self.house_load_sensor_active = False
		self.house_load_sensor_fault = int(0)
		house_load_sensor = self.add_preload_service('LightSensor')
		self.house_load_sensor_char = house_load_sensor.configure_char('CurrentAmbientLightLevel', value = 0.0001)
		self.house_load_sensor_active_char = house_load_sensor.configure_char('StatusActive')
		self.house_load_sensor_fault_char = house_load_sensor.configure_char('StatusFault')

	@Accessory.run_at_interval(30)
	async def run(self):
		if self.current_house_load < 0.0001:
			self.house_load_sensor_char.set_value(0.0001)
		else:
			self.house_load_sensor_char.set_value(self.current_house_load)
		self.house_load_sensor_active_char.set_value(self.house_load_sensor_active)
		self.house_load_sensor_fault_char.set_value(self.house_load_sensor_fault)

class SolarProd(Accessory):
	"""Solar production in watts"""

	category = CATEGORY_SENSOR

	def __init__(self,  *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_solar_prod = 0 # stores current state
		self.solar_prod_sensor_active = False
		self.solar_prod_sensor_fault = int(0)
		solar_prod_sensor = self.add_preload_service('LightSensor')
		self.solar_prod_sensor_char = solar_prod_sensor.configure_char('CurrentAmbientLightLevel', value = 0.0001)
		self.solar_prod_sensor_active_char = solar_prod_sensor.configure_char('StatusActive')
		self.solar_prod_sensor_fault_char = solar_prod_sensor.configure_char('StatusFault')

	@Accessory.run_at_interval(35)
	async def run(self):
		if self.current_solar_prod < 0.0001:
			self.solar_prod_sensor_char.set_value(0.0001)
		else:
			self.solar_prod_sensor_char.set_value(self.current_solar_prod)
		self.solar_prod_sensor_active_char.set_value(self.solar_prod_sensor_active)
		self.solar_prod_sensor_fault_char.set_value(self.solar_prod_sensor_fault)

def get_accessory(driver):
	"""Call this method to get a standalone Accessory."""
	return BatterySOC(driver, 'BatterySOC')

def get_bridge(driver):
	bridge = Bridge(driver, 'SelectronicBridge')
	house_load_instance = HouseLoad(driver, 'Load in watts')
	solar_prod_instance = SolarProd(driver, 'Solar production in watts')
	generator_status_instance = GeneratorStatus(driver, 'Generator status')
	bridge.add_accessory(BatterySOC(driver, 'House', house_load_instance=house_load_instance, solar_prod_instance=solar_prod_instance, generator_status_instance=generator_status_instance))
	bridge.add_accessory(house_load_instance)
	bridge.add_accessory(solar_prod_instance)
	bridge.add_accessory(generator_status_instance)
	return bridge



# Start the bridge on port 51826
driver = AccessoryDriver(port=51826, persist_file='selectronic_hk_bridge.state')
driver.add_accessory(accessory=get_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()

'''
If you're on the lan and you know the select.live device's IP,
 you can navigate to http://$ip/cgi-bin/solarmonweb/devices to get
 the SP Pro's internal device ID and 
then http://$ip/cgi-bin/solarmonweb/devices/$sp_pro_id/point to get some
'''

"""

   "Switch": {
      "OptionalCharacteristics": [
         "Name"
      ],
      "RequiredCharacteristics": [
         "On"
      ],
      "UUID": "00000049-0000-1000-8000-0026BB765291"
   },

   "HumiditySensor": {
      "OptionalCharacteristics": [
         "StatusActive",
         "StatusFault",
         "StatusTampered",
         "StatusLowBattery",
         "Name"
      ],
      "RequiredCharacteristics": [
         "CurrentRelativeHumidity"
      ],
      "UUID": "00000082-0000-1000-8000-0026BB765291"
   },
   "CurrentRelativeHumidity": {
      "Format": "float",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "00000010-0000-1000-8000-0026BB765291",
      "maxValue": 100,
      "minStep": 1,
      "minValue": 0,
      "unit": "percentage"
   },
   "BatteryService": {
      "OptionalCharacteristics": [
         "Name"
      ],
      "RequiredCharacteristics": [
         "BatteryLevel",
         "ChargingState",
         "StatusLowBattery"
      ],
      "UUID": "00000096-0000-1000-8000-0026BB765291"
   },

   "BatteryLevel": {
      "Format": "uint8",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "00000068-0000-1000-8000-0026BB765291",
      "maxValue": 100,
      "minStep": 1,
      "minValue": 0,
      "unit": "percentage"
   },
 "ChargingState": {
      "Format": "uint8",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "0000008F-0000-1000-8000-0026BB765291",
      "ValidValues": {
         "Charging": 1,
         "NotChargeable": 2,
         "NotCharging": 0
      }
   },

   "StatusLowBattery": {
      "Format": "uint8",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "00000079-0000-1000-8000-0026BB765291",
      "ValidValues": {
         "BatteryLevelLow": 1,
         "BatteryLevelNormal": 0
      }
   },

   "TemperatureSensor": {
      "OptionalCharacteristics": [
         "StatusActive",
         "StatusFault",
         "StatusLowBattery",
         "StatusTampered",
         "Name"
      ],
      "RequiredCharacteristics": [
         "CurrentTemperature"
      ],
      "UUID": "0000008A-0000-1000-8000-0026BB765291"
   },

   "CurrentTemperature": {
      "Format": "float",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "00000011-0000-1000-8000-0026BB765291",
      "maxValue": 1000,
      "minStep": 0.1,
      "minValue": -273.1,
      "unit": "celsius"
   },

"""
