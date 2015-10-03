#!/usr/bin/env python
#===========================================================================
# thermo_server.py
#
# The web interface for the thermostat.
#
# 2015-10-02
# Carter Nelson
#===========================================================================
import tornado.httpserver
import tornado.websocket
import tornado.web

# define port server will listen to
PORT = 6666

#-------------------------------------------------------------------------
# Tornado Server Setup
#-------------------------------------------------------------------------
# camera shut down
class ThermoMainHandler(tornado.web.RequestHandler):
    def get(self):
        print "GET Request from {}".format(self.request.remote_ip)
        kwargs = self.__build_kwargs__()
        self.render('thermo_status.html', **kwargs)
        
    def __build_kwargs__(self, ):
        kwargs = {}
        kwargs['DATE'] = 'FRI OCT 02, 2015'
        kwargs['TIME'] = '05:45 PM'
        kwargs['SETPOINT'] = '70'
        kwargs['SETPOINT_COLOR'] = 'red'
        kwargs['CURRENT_TEMP'] = '68'
        kwargs['TEMP_MIN'] = '62'
        kwargs['TEMP_MAX'] = '72'
        kwargs['TOTAL_ON_TIME'] = '00:38'
        kwargs['TEMP_PLOT'] = 'test/olsen.jpg'
        return kwargs
      
# map URLs to handlers
handlers = ([
    (r"/thermo_status",      ThermoMainHandler),
    # following is needed to serve <img src="..."/>
    (r"/(.*)", tornado.web.StaticFileHandler,{'path':'./'}),
])

#===========================
# MAIN
#===========================
print "create app..."
app = tornado.web.Application(handlers)
print "create http server..."
server = tornado.httpserver.HTTPServer(app)
print "start listening on port {}...".format(PORT)
server.listen(PORT)
print "start ioloop..."
tornado.ioloop.IOLoop.instance().start()
print "i guess we're done then."


