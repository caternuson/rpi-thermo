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
import tornado.web

#-------------------------------------------------------------------------
# Tornado Server Setup
#-------------------------------------------------------------------------
# define port server will listen to
PORT = 6666

# import handlers
import ThermoStatusHandler
      
# map URLs to handlers
handlers = ([
    (r"/thermo_status",      ThermoStatusHandler.ThermoStatusHandler),
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


