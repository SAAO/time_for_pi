#!/usr/bin/env python

import time, datetime, RPi.GPIO as GPIO
import sqlite3
loop=True
warn_gun=24
fire_gun=25
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(warn_gun, GPIO.OUT)
GPIO.setup(fire_gun, GPIO.OUT)

def time_firing():
        conn = sqlite3.connect('/home/time_for_pi/frontpage/timeserver.db', timeout=1)
        curs=conn.cursor()
        firing_db="SELECT* FROM time_firing"
        curs.execute(firing_db)
        ft = [dict(firing_time=row[2], pulse_length=row[3], pre_fire=row[1]) for row in curs.fetchall()] #this returns a single element list of dictionaries containing the data in table time_firing
        pre_fire_pulse=ft[0]['pre_fire']
        pulse_len=ft[0]['pulse_length']
        firing=ft[0]['firing_time']
        return firing, pre_fire_pulse, pulse_len


while loop:
	current_time_read = datetime.datetime.now().time()
	current_time = current_time_read.strftime("%H:%M:%S")
	noon, warning_time, fire_duration = time_firing()
	
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
			
