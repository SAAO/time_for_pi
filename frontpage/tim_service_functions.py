
import sqlite3, sys, traceback

def pulse_insert(tselect):
	the_id = '1'
	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	curs.execute(''' UPDATE time_pulse SET selection=? WHERE id=? ''', (tselect, the_id))
	conn.commit()
	return
def pulse_read():
        the_id=1
        conn = sqlite3.connect('/home/time_for_pi/main/timeserver.db', timeout=1)
        curs=conn.cursor()
        firing_db="SELECT* FROM time_pulse"
        curs.execute(firing_db)
        pulse=[dict(selection=row[1]) for row in curs.fetchall()]
        return pulse[0]['selection']
        

def time_firing():
        conn = sqlite3.connect('timeserver.db', timeout=1)
        curs=conn.cursor()
        firing_db="SELECT* FROM time_firing"
        curs.execute(firing_db)
        ft = [dict(firing_time=row[2], pulse_length=row[3], pre_fire=row[1]) for row in curs.fetchall()] #this returns a single element list of dictionaries containing the data in table time_firing
        pre_fire_pulse=ft[0]['pre_fire']
        pulse_len=ft[0]['pulse_length']
        firing=ft[0]['firing_time']
        return firing, pre_fire_pulse, pulse_len

def firing(warning, firing, pulse):
	firing_id = '1'
	conn = sqlite3.connect('timeserver.db', timeout=1)
	curs=conn.cursor()
	curs.execute(''' UPDATE time_firing SET pre_firing=?, firing_time=?, firing_pulse=? WHERE fid=? ''', (warning, firing, pulse, firing_id))
	conn.commit()
	return
      
def gps_data():
        conn=sqlite3.connect('timeserver.db', timeout=1)
        curs=conn.cursor()
        gps_time=1
        gps_status=3
        gps_long=123
        gps_lat=321
        gps_tdate=9
        curs.execute(''' UPDATE gps_check SET gpstime=?, gpsstatus=?, tdate=?, longitude=?, lattitude=? ''', (gps_time, gps_status, gps_tdate, gps_long, gps_lat))
        conn.commit()
        return      



if __name__ == '__main__':
            try:
                    ff=pulse_read()
                    print ff
                    if ff == '1pps':
                            print ff
              
            except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
                    print "\nKilling Thread..."

            
