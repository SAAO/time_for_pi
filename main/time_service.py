#!/usr/bin/env python
import sys, traceback
import os
import RPi.GPIO as GPIO
import subprocess
import sidereal as sid
import datetime as dt
import math
from gps import *
from time import *
import time
import threading
import lcd
import socket
import fcntl
import struct
import sqlite3


traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n''' # Skipping the "actual line" item


#==================INITIALIZE REGISTERS===============================================================================
gps_status=4
arm_pulse=17
ng_warning=24
ng_fire=25
LP_D0=27
LP_D1=22
LP_D2=18
LIGHT_PULSE_ON = 23
pid = os.getpid()
pid_file = open("/var/run/python-script.pid", "wb")
pid_file.write(str(pid))
pid_file.close()
kilohertz = 8
fix_flag=True #flag to ensure no gps fix is only printed once
old_sast=0                      # initialize seconds register
diff=0
delay=0
previous_option = '7Hz'


#================================================================GPIO SETUP==========================================
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gps_status, GPIO.OUT)  # setup gps status led
GPIO.setup(arm_pulse, GPIO.OUT) # setup 500ms arm pulse
GPIO.setup(LP_D0, GPIO.OUT) # lightpulse select D0
GPIO.setup(LP_D1, GPIO.OUT) # lightpulse select D1
GPIO.setup(LP_D2, GPIO.OUT) # lightpulse select D2
GPIO.setup(LIGHT_PULSE_ON, GPIO.OUT) # lightpulse select D2
GPIO.setup(ng_warning, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN) # noon gun warning
GPIO.setup(ng_fire, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN) # noon gun fire
GPIO.setup(kilohertz, GPIO.IN) # noon gun fire


GPIO.output(gps_status, False)
GPIO.output(LIGHT_PULSE_ON, False)
GPIO.output(LP_D0, False)
GPIO.output(LP_D1, False)
GPIO.output(LP_D2, False)
GPIO.output(arm_pulse, False)
GPIO.output(ng_warning, False)
GPIO.output(ng_fire, False)
#====================================================================================================================
gpsd = None #seting the global variable
#os.system('clear') #clear the terminal (optional)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def no_gps_fix():
	lcd.clear(fd) #clear display
	lcd.writeString("NO GPS FIX", fd)
	return
#=====================================================================================================
def display_ip(ip_chars):
	lcd.writeString("IP:", fd)
	location=4
	for char in ip_chars:
		lcd.write(ord(char), type, fd)
		location=location+1
	while location<=20:
		lcd.writeString(" ", fd)
		location=location+1
	return
#=====================================================================================================
def dech(time):
	try:
		hours = int(time)
		minutesA=(time-int(time))*60
		minutes = int(minutesA)
		seconds = (minutesA-int(minutesA))*60
		return hours, minutes, seconds
	except:
		return 0, 0, 0
	return 0, 0, 0
#=====================================================================================================
def pulse_read():
	the_id=1
	conn = sqlite3.connect('/home/time_for_pi/frontpage/timeserver.db', timeout=1)
	curs=conn.cursor()
	firing_db="SELECT* FROM time_pulse"
	curs.execute(firing_db)
	pulse=[dict(selection=row[1]) for row in curs.fetchall()]
	return pulse[0]['selection']
def IO(previous_option):
	try:
		os.system('clear')
		option = str(pulse_read())
		print option, previous_option
		if option != previous_option:
			print "ERROR"
			time_pulse(option)
	except Exception, e:				
		exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default
		traceback_details={
							'filename': exc_traceback.tb_frame.f_code.co_filename,
							'lineno'  : exc_traceback.tb_lineno,
							'name'    : exc_traceback.tb_frame.f_code.co_name,
							'type'    : exc_type.__name__,
							'message' : exc_value.message, # or see traceback._some_str()
							}
		
		# This still isn't "completely safe", though!
		# "Best (recommended) practice: replace all exc_type, exc_value, exc_traceback
		# with sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
		print
		print traceback.format_exc()
		print
		print traceback_template % traceback_details
		print
					
		end = open("/home/time_for_pi/end.txt", 'wb')
		end.write("File:\t\t\t")
		end.write(exc_traceback.tb_frame.f_code.co_filename)
		end.write("\nLine:\t\t\t")
		end.write(str(exc_traceback.tb_lineno))
		end.write("\nModule:\t\t\t")
		end.write(exc_traceback.tb_frame.f_code.co_name)
		end.write("\nError Type:\t\t")
		end.write(exc_type.__name__)
		end.write("\nError:\t\t\t")
		end.write(exc_value.message)
		end.write("\n")
		end.close()
		del(exc_type, exc_value, exc_traceback) # So we don't leave our local labels/objects dangling			
	#except:
	#	print "error oFFF"
	#	GPIO.output(LIGHT_PULSE_ON, False)

	return option
	
def time_pulse(option):
	GPIO.output(LIGHT_PULSE_ON, False)
	if option == '1pps':
		os.system("bash /home/time_for_pi/gps_setup/invert_khz")
		delay=0
		GPIO.output(LP_D0, False)
		GPIO.output(LP_D1, False)
		GPIO.output(LP_D2, False)
	elif option == '2hz':
		print option
		os.system("bash /home/time_for_pi/gps_setup/invert_khz")
		delay=0.25
		GPIO.output(LP_D0, True)
		GPIO.output(LP_D1, False)
		GPIO.output(LP_D2, False)		
	elif option == '5hz':
		os.system("bash /home/time_for_pi/gps_setup/invert_khz")
		delay=0.1
		GPIO.output(LP_D0, False)
		GPIO.output(LP_D1, True)
		GPIO.output(LP_D2, False)
	elif option == '10hz':
		os.system("bash /home/time_for_pi/gps_setup/invert_khz")
		delay=0.05
		GPIO.output(LP_D0, True)
		GPIO.output(LP_D1, True)
		GPIO.output(LP_D2, False)
	elif option == '100hz':
		os.system("bash /home/time_for_pi/gps_setup/invert_khz")
		delay=0.005
		GPIO.output(LP_D0, False)
		GPIO.output(LP_D1, False)
		GPIO.output(LP_D2, True)
	elif option == '1khz':
		os.system("bash /home/time_for_pi/gps_setup/noninvert_khz")
		delay=0
		GPIO.output(LP_D0, True)
		GPIO.output(LP_D1, False)
		GPIO.output(LP_D2, True)
	time.sleep(1)		
	timeNow = dt.datetime.now()
	seconds_now = timeNow.second
	S = seconds_now
	while S is seconds_now:
		timeNow = dt.datetime.now()
		S = timeNow.second
	if option != 'off':
		print "ON"
		time.sleep(delay)
		GPIO.output(LIGHT_PULSE_ON, True)
	return 
 #=====================================================================================================
class GpsPoller(threading.Thread):
  def __init__(self):
	result = False
	while not result:
		try:
			threading.Thread.__init__(self)
			global gpsd #bring it in scope
			gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) #starting the stream of info
			self.current_value = None
			self.running = True #setting the thread running to true
			result = True
		except:
			pass
  def run(self):
	global gpsd
	while gpsp.running:
		gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
#=====================================================================================================


 #=====================================================================================================
if __name__ == '__main__':
	fd = lcd.init()
	gpsp = GpsPoller() # create the thread
	no_gps_fix()
	try:
		gpsp.start() # start it up
		while True:
			previous_option=IO(previous_option)
			#It may take a second or two to get good data
			#print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
			if gpsd.fix.mode==MODE_2D:
				fix_flag=True
				GPIO.output(gps_status, True)   # switch on gps status led if it has a 3d fix
				#==========================================================calculate sidereal time from gps time
				gpsNow = gpsd.utc
				gpsNow = gpsNow.replace('Z', 'UTC')
				ctLong = gpsd.fix.longitude
				gpsNow = sid.parseDatetime(gpsNow)
				GST = sid.SiderealTime.fromDatetime(gpsNow)
				LST =GST.hours+(ctLong/15)
				h, m, s = dech(LST)

				#=========================================================get SAST
				timeNow = dt.datetime.now()
				HOURS = timeNow.hour
				MINUTES = timeNow.minute
				SECONDS = timeNow.second						
				
				#LCD strings
				#sidereal string
				hsid=str(h)
				msid=str(m)
				ssid=str(int(s))
				sidereal_time = "Sidereal: " + hsid.zfill(2) + ":" + msid.zfill(2) + ":" + ssid.zfill(2) + "  "
				#sast string
				Hsast=str(HOURS)
				Msast=str(MINUTES)
				Ssast=str(SECONDS)
				sast_time = "SAST: " + Hsast.zfill(2) + ":" + Msast.zfill(2) + ":" + Ssast.zfill(2) + "      "
								
				if SECONDS ==30: #reset the lcd display every minute to remove display errors
					lcd.reset(fd)
				if SECONDS >=59:
					GPIO.output(arm_pulse, True)
				else:
					GPIO.output(arm_pulse, False)
									
				diff=SECONDS-old_sast
				old_sast=SECONDS
				if diff >= 1 or diff==-59:								#If the time has changed by 1 second update the display
					#======================================================print to LCD display
					lcd.clear(fd) #clear display
					type = True
					lcd.writeString(sast_time, fd)
					try:
						IP = get_ip_address('eth0')
					except:
						IP= "No Network"
					if IP:
						ip_chars = list(IP)
						display_ip(ip_chars)
					lcd.writeString(sidereal_time, fd)
					
			else:	#else if gpsd reports no fix switch off led
				GPIO.output(gps_status, False)
				if fix_flag:
					no_gps_fix()
					fix_flag=False
				#time.sleep(0.5) #set to whatever
	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "\nKilling Thread..."
		gpsp.running = False
		gpsp.join() # wait for the thread to finish what it's doing

	except Exception, e:		
		gpsp.running = False
		gpsp.join() # wait for the thread to finish what it's doing
		
		exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default
		traceback_details={
							'filename': exc_traceback.tb_frame.f_code.co_filename,
							'lineno'  : exc_traceback.tb_lineno,
							'name'    : exc_traceback.tb_frame.f_code.co_name,
							'type'    : exc_type.__name__,
							'message' : exc_value.message, # or see traceback._some_str()
							}
		
		# This still isn't "completely safe", though!
		# "Best (recommended) practice: replace all exc_type, exc_value, exc_traceback
		# with sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
		print
		print traceback.format_exc()
		print
		print traceback_template % traceback_details
		print
					
		end = open("/home/time_for_pi/end.txt", 'wb')
		end.write("File:\t\t\t")
		end.write(exc_traceback.tb_frame.f_code.co_filename)
		end.write("\nLine:\t\t\t")
		end.write(str(exc_traceback.tb_lineno))
		end.write("\nModule:\t\t\t")
		end.write(exc_traceback.tb_frame.f_code.co_name)
		end.write("\nError Type:\t\t")
		end.write(exc_type.__name__)
		end.write("\nError:\t\t\t")
		end.write(exc_value.message)
		end.write("\n")
		end.close()
		del(exc_type, exc_value, exc_traceback) # So we don't leave our local labels/objects dangling
		

