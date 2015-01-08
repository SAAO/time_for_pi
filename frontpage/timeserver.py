from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
import sys, os
from crontab import CronTab
app = Flask(__name__)

app.secret_key = 'tawanda'

@app.route('/')
def index():
  return redirect( url_for('login'))

@app.route('/home')
def home():
  if not session.get('logged_in', False):
    error = 'You need to login to access this page'
    return render_template('login.html', error=error)
  
  return render_template('index.html')

@app.route('/pulseinsert', methods= ['GET','POST'])
def pulse_insert():
	if not session.get('logged_in', False):
	    error = 'You need to login to access this page'
	    return render_template('login.html', error=error)

	the_id = '1'
	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	tselect= request.form['timepulse']
	curs.execute(''' UPDATE time_pulse SET selection=? WHERE id=? ''', (tselect, the_id))
	conn.commit()
	return redirect(url_for('time_pulse'))

@app.route("/timepulse")
def time_pulse():
	if not session.get('logged_in', False):
	    error = 'You need to login to access this page'
	    return render_template('login.html', error=error)

	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	pulse_selected="SELECT* FROM time_pulse"
	curs.execute(pulse_selected)
	pulse = [dict(selection=row[1]) for row in curs.fetchall()]
	return render_template('timepulse.html', pulse=pulse)

@app.route("/gpscheck")
def gps_check():
	if not session.get('logged_in', False):
	    error = 'You need to login to access this page'
	    return render_template('login.html', error=error)

	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	gps_select="SELECT* FROM gps_check"
	curs.execute(gps_select)
	gps = [dict(tdate=row[0], gpstime=row[1], gpsstatus=row[2], longitude=row[3], lattitude=row[4]) for row in curs.fetchall()]
	return render_template ('checkgps.html', gps=gps)

@app.route("/timefiring")
def time_firing():
	if not session.get('logged_in', False):
	    error = 'You need to login to access this page'
	    return render_template('login.html', error=error)

	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	firing_time="SELECT* FROM time_firing"
	curs.execute(firing_time)
	firing = [dict(pre_firing=row[1], firing_time=row[2], firing_pulse=row[3] ) for row in curs.fetchall()]
	return render_template('timefiring.html', firing=firing)

@app.route('/firing', methods=['GET','POST'])
def firing():
	if not session.get('logged_in', False):
	    error = 'You need to login to access this page'
	    return render_template('login.html', error=error)
	    
	firing_id = '1'
	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	warning = request.form['prefiring']
	firing= request.form['firingtime']
	pulse = request.form['firingpulse']

	curs.execute(''' UPDATE time_firing SET pre_firing=?, firing_time=?, firing_pulse=? WHERE fid=? ''', (warning, firing, pulse, firing_id))
	conn.commit()
	noon_cron(firing, warning)
	return redirect(url_for('time_firing'))

#=================================================LOGIN AND LOGOUT FUNTIONS
@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != 'admin' or request.form['password'] != 'admin':
      error = 'Invalid credentials, either your username or password is wrong'

    else:
      session['logged_in'] = True
      return redirect(url_for('home'))

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  error = None
  return render_template('login.html', error=error)

@app.route('/reboot')
def reboot():
  os.system('sudo reboot')
  return redirect('http://www.saao.ac.za', 302)

def noon_cron(fire_t, pre_f_warn):
	fire_t_list = fire_t.split(":")
	hour=int(fire_t_list[0])
	minute=int(fire_t_list[1])
	second=int(fire_t_list[2])
	second=second-int(pre_f_warn)-10
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
	
	return  
  
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=4000, debug=True)
