#!/usr/bin/env python

import time, datetime, RPi.GPIO as GPIO
import sqlite3
loop=True
warn_gun=24
fire_gun=25
count_gun = 9 # change this to 4 for the noon gun module, also change the gps_stat to 9 in time_service.py
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(warn_gun, GPIO.OUT)
GPIO.setup(fire_gun, GPIO.OUT)
GPIO.setup(count_gun, GPIO.OUT)
GPIO.output(count_gun, False)
current_time_read = datetime.datetime.now().time()
countdown_flag = False
tm = 1
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

def warning_calc(nt, wt):
	h, m, s = nt.split(":")
        seconds = int(h)*3600+int(m)*60+int(s)
        warns = seconds - int(wt)
        if warns<0:
                warns=86400+warns
        wh = int((warns/3600))
        if wh<10:
                whs="0"+str(wh)
	else:
		whs=str(wh)
        wm = int(((warns-(wh*3600))/60))
        if wm<10:
                wms="0"+str(wm)
	else:
		wms=str(wm)
        ws = int(warns-wh*3600-wm*60)
        if ws<10:
                wss="0"+str(ws)
	else:
		wss=str(ws)
	
        warnt = whs + ":" + wms +":" + wss
	return warnt
	
def get_seconds(var):
	temp_s = var.split(":")
	return int(temp_s[2])



while loop:
	current_time_read = datetime.datetime.now().time()
	current_time = current_time_read.strftime("%H:%M:%S")
	
	noon, warning_time, fire_duration = time_firing()
	

	warn_time=warning_calc(noon, warning_time)		
	
	'''print "warning time: " + warn_time
	print "Firing time: " + noon
	print "current time: " + current_time'''

	float_fire_duration = float(fire_duration)
	if current_time == warn_time and current_time < noon:
		countdown_flag = True
		print "warning"
		GPIO.output(warn_gun, True)
		time.sleep(float_fire_duration)
		GPIO.output(warn_gun, False)
	elif current_time == noon:
		GPIO.output(fire_gun, True)
		print "BOOOOOM!!!"
		time.sleep(float_fire_duration)
		GPIO.output(fire_gun, False)
		countdown_flag = False
		loop=False
	elif countdown_flag:
		current_s = get_seconds(current_time)
		if current_s-tm >= 1:
			GPIO.output(count_gun, True)
			time.sleep(0.7)
			GPIO.output(count_gun, False)
			print "second!!"
			tm = current_s
