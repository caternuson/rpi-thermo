#!/usr/bin/env python
#===========================================================================
# ThermoStatusHandler.py
#
# Class to handle thermostat status.
#
# 2015-10-02
# Carter Nelson
#===========================================================================
import tornado.web
import mysql.connector

def CToF(degC):
    """Return the Centigrade value in degrees Fahrenheit."""
    return 32.0 + (degC * 9.0)/5.0

class ThermoStatusHandler(tornado.web.RequestHandler):
    def get(self):
        print "GET Request from {}".format(self.request.remote_ip)
        self.write("<html><body><center>           \
                   <img src='status.jpg'/>         \
                   </center></body></html>")
        #kwargs = self.__build_kwargs__()
        #self.render('html/thermo_status.html', **kwargs)
        
    def __get_latest_row__(self, ):
        """Return the most recent row from the database."""
        cnx = mysql.connector.connect(user='thermo', password='thermo', database='thermo_test')
        cursor = cnx.cursor()
        get_row = ("SELECT * FROM data ORDER BY datetime DESC LIMIT 1")
        cursor.execute(get_row)
        data = None
        for line in cursor:
            data = line
        return data
        
    def __build_kwargs__(self, ):
        kwargs = {}
        data = self.__get_latest_row__()
        if data==None:
            return kwargs
        kwargs['DATE'] = data[0].strftime("%a %b %d, %Y").upper()
        kwargs['TIME'] = data[0].strftime("%I:%M %p")
        kwargs['SETPOINT'] = "%2i" % data[6]
        kwargs['SETPOINT_COLOR'] = 'black'
        if data[7]==1:
            kwargs['SETPOINT_COLOR'] = 'red'
        kwargs['CURRENT_TEMP'] = "%2i" % CToF(data[5])
        kwargs['TEMP_MIN'] = '?'
        kwargs['TEMP_MAX'] = '?'
        kwargs['TOTAL_ON_TIME'] = '??:??'
        kwargs['TEMP_PLOT'] = 'test/olsen.jpg'
        return kwargs
    
#--------------------------------------------------------------------
# MAIN 
#--------------------------------------------------------------------
if __name__ == '__main__':
    print "I'm just a class, nothing to do..."