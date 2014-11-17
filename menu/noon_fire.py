#!/usr/bin/env python
'''

Text File format

hh:mm:ss                              (warning time)
hh:mm:ss							  (firing time)
ss									  (firing pulse duration)
'''
import time, datetime, RPi.GPIO as GPIO
loop=True
warn_gun=24
fire_gun=25
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(warn_gun, GPIO.OUT)
GPIO.setup(fire_gun, GPIO.OUT)

while loop:
	current_time_read = datetime.datetime.now().time()
	current_time = current_time_read.strftime("%H:%M:%S")
	f = open("/home/time_for_pi/menu/gun_time", "r")
	warning_time = f.readline().rstrip('\n')
	noon = f.readline().rstrip('\n')
	fire_duration = f.readline().rstrip('\n')
	float_fire_duration = float(fire_duration)
	#print fire_duration
	print current_time	
	print warning_time	
	print noon
	print fire_duration
	if current_time == warning_time and current_time < noon:
		print "warning"
		GPIO.output(warn_gun, True)
		time.sleep(float_fire_duration)
		GPIO.output(warn_gun, False)
	elif current_time == noon:
		GPIO.output(fire_gun, True)
		print "BOOOOOM!!!"
		time.sleep(float_fire_duration)
		GPIO.output(fire_gun, False)
		loop=False
			
