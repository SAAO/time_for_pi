from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
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
	firing = [dict(firing_time=row[2]) for row in curs.fetchall()]
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

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=4000, debug=True)
