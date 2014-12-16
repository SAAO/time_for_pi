#!/usr/bin/env python
import sys, traceback
import os
import subprocess
import math
import time
import threading
import decimal 
import string

 #=====================================================================================================
if __name__ == '__main__':
	raw_logs=[[]]
	f_log=[[]]
	skew_ppm_total=0
	offset_total=0
	offset_sd_total=0
	rem_corr_total=0
	statistics = "/var/log/chrony/tracking.log"
	try:
		#get the text file into a list
		with open(statistics) as f:
			logs=f.readlines()
		#split by whitespace
		for x in logs:
			raw_logs.append(x.split(' '))
		#remove empty list elements
		for x in raw_logs:
			z=filter(None, x)
			f_log.append(z)
		#remove the first few lines because.
		del f_log[0]
		del f_log[0]
		del f_log[0]
		#summarise the columns
		i=0
		for x in f_log:
			if(len(x)>0):
				skew_ppm=math.fabs(float(x[5]))
				offset=math.fabs(float(x[6])) #convert the exponential notation string to an absolute float
				offset_sd=math.fabs(float(x[8]))
				rem_corr=offset_sd=math.fabs(float(x[9]))
				if offset <0.001:
					skew_ppm_total+=skew_ppm
					offset_total+=offset
					offset_sd_total+=offset_sd
					rem_corr_total+=rem_corr
				i=i+1
				
		offset_avg=offset_total/i
		skew_ppm_avg=skew_ppm_total/i
		offset_sd_avg=offset_sd_total/i
		rem_corr_avg=rem_corr_total/i
		start_dt=f_log[0][0] + " " + f_log[0][1]
		length=len(f_log)
		end_dt=f_log[length-1][0] + " " + f_log[length-1][1]
		the_line= start_dt + " ->" + end_dt + "		" + str(skew_ppm_avg) + "		" + str(offset_avg) + "		" + str(offset_sd_avg) + "		" + str(rem_corr_avg)
		print the_line
		#try to open file with append option if it does not exist create it
		file=open("/var/log/chrony/tracking_summary.log" , "a")
		file.write("Summary Period ================================= ppm skew =================== offset ============== offset sd =================== rem. corr. \n")
		file.write(the_line)
		file.close
		#restart chronyd
		os.system("rm /var/log/chrony/tracking.log") #MAY HAVE STOPPED CHRONY FROM LOGGING
		os.system("sudo killall chronyd")
		os.system("sudo /usr/local/sbin/chronyd")
		
		#print "START: ", start_dt, "END: ", end_dt, "offset: ", offset_avg, "   skew_pps: ", skew_ppm_avg, "		offset_SD: ", offset_sd_avg, "		rem_corr: ", rem_corr_avg
			
                                        
	except(KeyboardInterrupt, SystemExit):#, IndexError ): #when you press ctrl+c
			if KeyboardInterrupt:
					print "\n\nWhy U quit >:| ...\n"

