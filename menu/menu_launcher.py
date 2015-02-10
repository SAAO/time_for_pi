#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Topmenu and the submenus are based of the example found at this location http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/
# The rest of the work was done by Matthew Bennett and he requests you keep these two mentions when you reuse the code :-)
# Basic code refactoring by Andrew Scheller
#The menu has been adapted to modify a Raspberry Pi time service gpio configuration by Jeran Cloete

from time import sleep
import curses, os #curses is the interface for capturing key presses on the menu, os launches the files
import signal
import time
import subprocess
import sqlite3
from crontab import CronTab


def sigint_handler(signum, frame):
	print 'Stop pressing the CTRL+C!'
 
signal.signal(signal.SIGINT, sigint_handler) #disable ctrl C

screen = curses.initscr() #initializes a new window for capturing key presses
curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
curses.start_color() # Lets you use colors when highlighting selected menu option
screen.keypad(1) # Capture input from keypad

# Change this to use different colors when highlighting
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
h = curses.color_pair(2) #h is the coloring for a highlighted menu option
n = curses.A_NORMAL #n is the coloring for a non highlighted menu option


tp_dict = {'0':'1PPS timepulse selected and ON', 
			'1':'2Hz time pulse selected and ON',
			'2':'5Hz time pulse selected and ON',
			'3':'10Hz time pulse selected and ON',
			'4':'100Hz time pulse selected and ON',
			'5':'1kHz time pulse selected and ON',
			'6':'time pulse OFF'} 

MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"
PASSWORD = "saao"
display_tp="nothing"
user_input_password = "wrongpass"
passPrompt = False
tp_options=["1PPS", "2 Hz", "5 Hz", "10 Hz", "100 Hz", "1 kHz", "OFF"]
tp_selected = '0'
lcd_options=["Sidereal Time", "South African Local Time", "UTC", "GPS Data"]
tp_option=''


#get the currently selected time pulse


menu_data = {
		'title': "Time Service Configuration", 'type': MENU, 'subtitle': "Please select an option...",
		'options':[
		{ 'title': "This is a menu option", 'type': COMMAND, 'command': 'time_pulse' },
			
			{ 'title': "Time Pulse Selection", 'type': MENU, 'subtitle': display_tp,
			'options': [
			  { 'title': tp_options[0], 'type': COMMAND, 'command': 'P1' },
			  { 'title': tp_options[1], 'type': COMMAND, 'command': 'P2' },
			  { 'title': tp_options[2], 'type': COMMAND, 'command': 'P3' },
			  { 'title': tp_options[3], 'type': COMMAND, 'command': 'P4' },
			  { 'title': tp_options[4], 'type': COMMAND, 'command': 'P5' },
			  { 'title': tp_options[5], 'type': COMMAND, 'command': 'P6' },
			  { 'title': tp_options[6], 'type': COMMAND, 'command': 'P7' },
			]
			},
			{ 'title': "Check GPS Data (Press CTRL+C to return)", 'type': COMMAND, 'command': 'gpsmon' },
			{ 'title': "Timed Firing Pulse", 'type': MENU, 'subtitle': "Please select an option...",
			'options': [
			  { 'title': 'Firing and Pre Fire warning time', 'type': COMMAND, 'command': 'ft' },
			  { 'title': 'Firing Pulse Duration', 'type': COMMAND, 'command': 'fpd' },
			]
			},
			{ 'title': "Reboot", 'type': MENU, 'subtitle': "Select Yes to Reboot",
			'options': [
			  {'title': "NO", 'type': EXITMENU, },
			  {'title': "", 'type': COMMAND, 'command': '' },
			  {'title': "", 'type': COMMAND, 'command': '' },
			  {'title': "", 'type': COMMAND, 'command': '' },
			  {'title': "YES", 'type': COMMAND, 'command': 'sudo shutdown -r -time now' },
			  {'title': "", 'type': COMMAND, 'command': '' },
			  {'title': "", 'type': COMMAND, 'command': '' },
			  {'title': "", 'type': COMMAND, 'command': '' },
			]
			},
		]		
}
#=====================================================================================================	
#=====================================================================================================	
#Database interface functions

def pulse_read():
        the_id=1
        conn = sqlite3.connect('/home/time_for_pi/frontpage/timeserver.db', timeout=1)
        curs=conn.cursor()
        firing_db="SELECT* FROM time_pulse"
        curs.execute(firing_db)
        pulse=[dict(selection=row[1]) for row in curs.fetchall()]
        return pulse[0]['selection']

def pulse_insert(tselect):
	the_id = '1'
	conn = sqlite3.connect('/home/time_for_pi/frontpage/timeserver.db', timeout=1)
	curs=conn.cursor()
	curs.execute(''' UPDATE time_pulse SET selection=? WHERE id=? ''', (tselect, the_id))
	conn.commit()
	return

def firing(warning, firing, pulse):
	firing_id = '1'
	conn = sqlite3.connect('/home/time_for_pi/frontpage/timeserver.db', timeout=1)
	curs=conn.cursor()
	curs.execute(''' UPDATE time_firing SET pre_firing=?, firing_time=?, firing_pulse=? WHERE fid=? ''', (warning, firing, pulse, firing_id))
	conn.commit()
	return

#=====================================================================================================	
#=====================================================================================================	
#this function edits a single line of a text file.
def replace_line(file_name, line_num, text):
	lines=[]
	with open(file_name) as lcd_file:
		for line in lcd_file:
			lines.append(line)
	text += "\n"
	lines[line_num] = text
	out = open(file_name, 'wb')
	out.writelines(lines)
	out.close()
	return
def read_lines(file_name):
	data=[]
	with open(file_name) as fire_file:
		for line in fire_file:
			data.append(line)
	return data
#=====================================================================================================	
#=====================================================================================================
def putinfile(file_name, text):
	out = open(file_name, 'wb')
	out.write(text)
	out.close()
	return
#=====================================================================================================
def user_input(prompt):
	result = False
	while not result:
		try:
			integer = int(raw_input(prompt))
			result = True
		except:
			print "Please Enter a valid String"		
	
	return integer
#=====================================================================================================	
#=====================================================================================================	
# This function displays the appropriate menu and returns the option selected
def runmenu(menu, parent):

  # work out what text to display as the last menu option
  if parent is None:
    lastoption = "Exit"
  else:
    lastoption = "Return to %s menu" % parent['title']

  optioncount = len(menu['options']) # how many options in this menu

  pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
  oldpos=None # used to prevent the screen being redrawn every time
  x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

  # Loop until return key is pressed
  while x !=ord('\n'):
    if pos != oldpos:
      oldpos = pos
      screen.border(0)
      screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
      screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

      # Display all the menu items, showing the 'pos' item highlighted
      for index in range(optioncount):
        textstyle = n
        if pos==index:
          textstyle = h
        screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
      # Now display Exit/Return at bottom of menu
      textstyle = n
      if pos==optioncount:
        textstyle = h
      screen.addstr(5+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
      screen.refresh()
      # finished updating screen

    x = screen.getch() # Gets user input

    # What is user input?
    if x >= ord('1') and x <= ord(str(optioncount+1)):
      pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
    elif x == 258: # down arrow
      if pos < optioncount:
        pos += 1
      else: pos = 0
    elif x == 259: # up arrow
      if pos > 0:
        pos += -1
      else: pos = optioncount
  # return index of the selected item
  return pos, parent
#=====================================================================================================
def noon_cron(hour, minute, second, pre_f_warn):
	second=second-pre_f_warn-10
	if second<0:
		second=60+second
		minute=minute-1
		if minute<0:
			minute=60+minute
			hour=hour-1
			if hour<0:
				hour=24+hour
	
	hou=str(hour)
	min=str(minute)
	sec=str(second)
	root_cron = CronTab(user='root')
	root_cron.remove_all(command='/usr/bin/python /home/time_for_pi/menu/noon_fire.py 2> /etc/noon_error.txt')
	noon_job = root_cron.new(command='/usr/bin/python /home/time_for_pi/menu/noon_fire.py 2> /etc/noon_error.txt', comment='fire the noon gun')	
	noon_job.set_command("sleep " + sec + "; /usr/bin/python /home/time_for_pi/menu/noon_fire.py 2> /etc/noon_error.txt")
	noon_job.hour.on(hou)
	noon_job.minute.on(minute)
	root_cron.write()
	
	for job in root_cron:
		print job
	
	return	
#=====================================================================================================	
# This function calls showmenu and then acts on the selected item
def processmenu(menu, parent=None):
	display_tp=pulse_read()
	optioncount = len(menu['options'])
	exitmenu = False
	while not exitmenu: #Loop until the user exits the menu
		getin, sub = runmenu(menu, parent)
		#processes the final menu option and prompts for password if it is on the main menu to get into the pi's shell
		if getin == optioncount:
			if sub is None:		#if it is a submenu do not prompt for password
				curses.def_prog_mode()    # save curent curses environment
				os.system('reset')
				screen.clear() #clears previous screen
				passPrompt = True
				user_input_password = raw_input('enter the administrator password:') #Prompt for password
				if user_input_password == PASSWORD:
					exitmenu = True
					passPrompt= False
					user_input_password = "wrongpass"
				curses.reset_prog_mode()   # reset to 'current' curses environment
				curses.curs_set(1)         # reset doesn't do this right
				curses.curs_set(0)
			else:
				exitmenu = True
		elif menu['options'][getin]['type'] == COMMAND:
			curses.def_prog_mode()    # save current curses environment
			os.system('reset')
			#=====================================================================================================		
				
			#=====================================================================================================	
			if menu['options'][getin]['command'] == "ft": #firing time
				screen.clear() #clears previous screen
				print "Enter the Firing Time in hours minutes and seconds"
				hours=user_input('Enter HOURS as a whole number between 0 and 23:')
				while hours>23 or hours<0:
					hours=user_input('Enter HOURS as a whole number between 0 and 23:') #Prompt hours				
				minutes = user_input('Enter MINUTES as a whole number between 0 and 59:') #Prompt minutes
				while minutes>60 or minutes<0:
					minutes = user_input('Enter MINUTES as a whole number between 0 and 59:') #Prompt minutes	
				seconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds	
				while seconds>60 or seconds<0:
					seconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds
				#====================pre fire warning
				print "Time before firing time when the warning pulse triggers in seconds *NOTE* this is an offset not a time."
				wseconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds
				while wseconds>60 or wseconds<0:
					wseconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds
				#=========firing pulse duration
				pulse_duration=user_input('Enter firing pulse duration in seconds: ')
				
				if(hours<10):
					fire_time="0"+str(hours)
				else:
					fire_time=str(hours)
				if(minutes<10):
					fire_time+=":"+"0"+str(minutes)
				else:
					fire_time+=":"+str(minutes)
				if(seconds<10):
					fire_time+=":" +"0"+ str(seconds)
				else:
					fire_time+=":" + str(seconds)



				firing(wseconds, fire_time, pulse_duration)
				noon_cron(int(hours), int(minutes), int(seconds), int(wseconds)) #setup the noon gun firing cron job
				
				
			if menu['options'][getin]['command'] == "fpd": # firing pulse duration
				seconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds	
				while seconds>60 or seconds<0:
					seconds = user_input('Enter SECONDS as a whole number between 0 and 59:') #Prompt seconds
				seconds=str(seconds)
				replace_line("/home/time_for_pi/menu/gun_time", 2,seconds)
			#=====================================================================================================
			if menu['options'][getin]['command'] == "P1": #light pulse 1PPS
				pulse_insert("1pps")
			if menu['options'][getin]['command'] == "P2": #light pulse 2Hz
				pulse_insert("2Hz")
			if menu['options'][getin]['command'] == "P3": #light pulse 5Hz
				pulse_insert("5Hz")
			if menu['options'][getin]['command'] == "P4": #light pulse 10Hz
				pulse_insert("10Hz")
			if menu['options'][getin]['command'] == "P5": #light pulse 100Hz
				pulse_insert("100Hz")
			if menu['options'][getin]['command'] == "P6": #light pulse 1Khz
				pulse_insert("1kHz")
			if menu['options'][getin]['command'] == "P7": #light pulse OFF
				pulse_insert("off")
			#=====================================================================================================			
			screen.clear() #clears previous screen
			os.system(menu['options'][getin]['command']) # run the command
			screen.clear() #clears previous screen on key press and updates display based on pos
			curses.reset_prog_mode()   # reset to 'current' curses environment
			curses.curs_set(1)         # reset doesn't do this right
			curses.curs_set(0)
		elif menu['options'][getin]['type'] == MENU:
				screen.clear() #clears previous screen on key press and updates display based on pos
				processmenu(menu['options'][getin], menu) # display the submenu
				screen.clear() #clears previous screen on key press and updates display based on pos

# Main program
processmenu(menu_data)

curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
os.system('clear')
