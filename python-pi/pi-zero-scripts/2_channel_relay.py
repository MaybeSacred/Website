#!/usr/bin/env python
'''
**********************************************************************
* Filename 		: 2_channel_relay.py
* Description 	: a sample script for 2-Channel High trigger Relay 
* Author 		: Cavon
* E-mail 		: service@sunfounder.com
* Website 		: www.sunfounder.com
* Update 		: Cavon    2016-08-04
* Detail		: New file
**********************************************************************
'''
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import PWMLED, DistanceSensor

#Relay_channel = [17, 18]
led = PWMLED(18)
sensor = DistanceSensor(echo=5, trigger=17)
#LINE = 17
def setup():

	pass
	# with gpiod.request_lines(
	# 	"/dev/gpiochip0",
	# 	consumer="blink-example",
	# 	config={
	# 		LINE: gpiod.LineSettings(
	# 			direction=Direction.OUTPUT, output_value=Value.ACTIVE
	# 		)
	# 	},
	# ) as request:
	# 	while True:
	# 		request.set_value(LINE, Value.ACTIVE)
	# 		sleep(1)
	# 		request.set_value(LINE, Value.INACTIVE)
	# 		sleep(1)
	# GPIO.setmode(GPIO.BCM)
	# GPIO.setup(Relay_channel, GPIO.OUT, initial=GPIO.LOW)
	# print("|=====================================================|")
	# print("|         2-Channel High trigger Relay Sample         |")
	# print("|-----------------------------------------------------|")
	# print("|                                                     |")
	# print("|          Turn 2 channels on off in orders           |")
	# print("|                                                     |")
	# print("|                    17 ===> IN2                      |")
	# print("|                    18 ===> IN1                      |")
	# print("|                                                     |")
	# print("|                                           SunFounder|")
	# print("|=====================================================|")

def main():
	# with gpiod.request_lines(
	# 	"/dev/gpiochip0",
	# 	consumer="blink-example",
	# 	config={
	# 		LINE: gpiod.LineSettings(
	# 			direction=Direction.OUTPUT, output_value=Value.ACTIVE
	# 		)
	# 	},
	# ) as request:
		while True:
			print("Distance: %.1f cm" % (sensor.distance * 100))
			led.value = sensor.distance
			sleep(0.1)
	# while True:
	# 	for i in range(0, len(Relay_channel)):
	# 		print('...Relay channel %d on' % (i+1))
	# 		GPIO.output(Relay_channel[i], GPIO.HIGH)
	# 		sleep(0.5)
	# 		print('...Relay channel %d off' % (i+1))
	# 		GPIO.output(Relay_channel[i], GPIO.LOW)
	# 		sleep(0.5)

# def destroy():
# 	GPIO.output(Relay_channel, GPIO.LOW)
# 	GPIO.cleanup()

if __name__ == '__main__':
	print("hello world")
	# with gpiod.Chip("/dev/gpiochip0") as chip:
	# 	info = chip.get_info()
	# 	print(f"{info.name} [{info.label}] ({info.num_lines} lines)")
	setup()
	try:
		main()
	except KeyboardInterrupt:
		#destroy()
		pass

