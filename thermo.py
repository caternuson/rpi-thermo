#-------------------------------------------------------------------------
# thermo.py
#
# Raspberry Pi based home thermostat.
#   * Heat only
#   * left over RPi model A
#   * Adafruit 2.2" TFT display
#   * Adafruit BMP085 breakout board
#   * Adafruit MCP9808 breakout board
#
# 2015-09-09
# Carter Nelson
#-------------------------------------------------------------------------
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO.SPI as SPI
import Adafruit_BMP.BMP085 as BMP085
import Adafruit_MCP9808.MCP9808 as MCP9808

import RPi.GPIO as GPIO

import Image, ImageDraw, ImageFont

import mysql.connector

import time
from datetime import datetime, timedelta

current_time        = None
current_temp        = None
current_setpoint    = None
is_heating          = False
bmp180_temp         = None
bmp180_press        = None 
bmp180_alt          = None
bmp180_slp          = None
mcp9808_temp        = None

#--------------------------------
# Constants
#--------------------------------
SET_POINT       = 70.0
LED_PIN         = 22
DC_PIN          = 18
RST_PIN         = 23
SPI_PORT        = 0
SPI_DEVICE      = 0
FONT_PATH       = "/home/pi/rpi-thermo/test/fonts/"
FONT_FILE       = "KeepCalm-Medium.ttf"
SCREEN_WIDTH    = 240
SCREEN_HEIGHT   = 320
WHOLE_SCREEN    = ((0,0),(SCREEN_WIDTH,SCREEN_HEIGHT))

#--------------------------------
# GPIO Init
#--------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

#--------------------------------
# Sensor Init
#--------------------------------
bmp180  = BMP085.BMP085()
mcp9808 = MCP9808.MCP9808()
mcp9808.begin()

#--------------------------------
# TFT Display Init
#--------------------------------
disp = TFT.ILI9341(DC_PIN, rst=RST_PIN, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
disp.begin()

#--------------------------------
# PIL ImageDraw for screen
#--------------------------------
screen = Image.new("RGB",(SCREEN_WIDTH, SCREEN_HEIGHT), "black")
screen_draw = ImageDraw.Draw(screen)

#--------------------------------
# Load Fonts
#--------------------------------
font12 = ImageFont.truetype(FONT_PATH+FONT_FILE,12)
font14 = ImageFont.truetype(FONT_PATH+FONT_FILE,14)
font36 = ImageFont.truetype(FONT_PATH+FONT_FILE,36)
font72 = ImageFont.truetype(FONT_PATH+FONT_FILE,72)
font132 = ImageFont.truetype(FONT_PATH+FONT_FILE,132)
font164 = ImageFont.truetype(FONT_PATH+FONT_FILE,164)

#--------------------------------
# Functions
#--------------------------------
def CToF(degC):
    """Return the Centigrade value in degrees Fahrenheit."""
    return 32.0 + (degC * 9.0)/5.0

def LEDOn():
    """Turn on the LED."""
    GPIO.output(LED_PIN, GPIO.HIGH)
    
def LEDOff():
    """Turn off the LED."""
    GPIO.output(LED_PIN, GPIO.LOW)
    
def get_temperature():
    """Return the current ambient temperature."""
    global bmp180_temp, mcp9808_temp
    if (bmp180_temp==None) or (mcp9808_temp==None):
     bmp180_temp = bmp180.read_temperature()
     mcp9808_temp = mcp9808.readTempC()
    temp = 0.5 * (bmp180_temp + mcp9808_temp)
    temp = CToF(temp)
    return temp

def read_sensors():
    """Read the current values from the attached sensors."""
    global bmp180_temp, bmp180_press, bmp180_alt, bmp180_slp, mcp9808_temp
    bmp180_temp     = bmp180.read_temperature()             # deg C
    bmp180_press    = bmp180.read_pressure()                # Pa 
    bmp180_alt      = bmp180.read_altitude()                # m
    bmp180_slp      = bmp180.read_sealevel_pressure()       # Pa
    mcp9808_temp    = mcp9808.readTempC()                   # deg C

def get_setpoint():
    """Return the current temperature set point."""
    return SET_POINT

def update_state():
    """Update various global to current conditions."""
    global current_time, current_temp, current_setpoint
    read_sensors()
    current_time = datetime.now()
    current_temp = get_temperature()
    current_setpoint = get_setpoint()  

def thermostat():
    """Take whatever action is necessary for the current state."""
    global current_temp, current_setpoint, is_heating
    if current_temp < current_setpoint:
        is_heating = True
        LEDOn()
    else:
        is_heating = False
        LEDOff()
        
def update_database():
    """Add current conditions to the MySQL database."""
    global current_time, current_temp, current_setpoint, is_heating, \
            bmp180_temp, bmp180_press, bmp180_alt, bmp180_slp, mcp9808_temp
    
    cnx = mysql.connector.connect(user='thermo', password='thermo', database='thermo_test')
    cursor = cnx.cursor()
    add_data = ("INSERT INTO data "
                "(datetime, bmp180_temp, bmp180_press, bmp180_alt, bmp180_slp, mcp9808_temp, set_temp, thermostat) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    state = 1 if is_heating else 0
    data = (current_time, bmp180_temp, bmp180_press, bmp180_alt, bmp180_slp, mcp9808_temp, current_setpoint, state)
    cursor.execute(add_data, data)
    cnx.commit()
    cursor.close()
    cnx.close()
    
def get_temp_history(start_time=None, end_time=None):
    """Retrieve temperature history from the MySQL database."""
    cnx = mysql.connector.connect(user='thermo', password='thermo', database='thermo_test')
    cursor = cnx.cursor()
    if end_time==None:
        end_time=current_time
    if start_time==None:
        start_time=datetime(current_time.year, current_time.month, current_time.day,
                            0, 0, 0, 0) 
    get_data = ("SELECT datetime, bmp180_temp FROM data "
                "WHERE datetime BETWEEN %s AND %s")
    cursor.execute(get_data, (start_time, end_time))
    data=[]
    for (d,t) in cursor:
        data.append((d,t))
    cursor.close()
    cnx.close()
    return data

def plot_temp_history():
    """Return a PIL image representing a temperature history."""
    W = 240
    H = 120
    MAXT = 90.0
    MINT = 60.0
    plot = Image.new("RGB",(W,H),"black")
    plot_draw = ImageDraw.Draw(plot)
    area = [(0,0),(W,H)]
    border = [(0,0),(W-1,0),(W-1,H-1),(0,H-1),(0,0)]
    grid_lines = [
        [(int(W*0.25),0),(int(W*0.25),H)],
        [(int(W*0.50),0),(int(W*0.50),H)],
        [(int(W*0.75),0),(int(W*0.75),H)],
        [(0,int(H/3.0)),(W,int(H/3.0))],
        [(0,int(2*H/3.0)),(W,int(2*H/3.0))]
    ]
    # get data from database
    data = get_temp_history()
    # map/compress temperature history to display size
    tmap=W*[None]
    for (d,t) in data:
        if t==None:
            continue
        t = CToF(t)
        x = int(W * float(d.hour*3600+d.minute*60+d.second)/86400)
        if tmap[x]==None:
            tmap[x]=t
        else:
            tmap[x]=0.5*(tmap[x]+t)
    # generate points from mapping        
    points=[]
    for x,t in enumerate(tmap):
        if t==None:
            continue
        y = H - int(H*(t-MINT)/(MAXT-MINT))
        points.append((x,y))
    # draw items from bottom to top
    plot_draw.rectangle(area,fill=(80,80,80))    
    plot_draw.line(points,fill=(0,255,255),width=3)
    for grid in grid_lines:
        plot_draw.line(grid,fill=(255,255,255),width=1)
    plot_draw.line(border,fill=(255,255,255),width=1)
    return plot    
               
def clear_screen():
    """Clear the TFT display."""
    screen_draw.rectangle(WHOLE_SCREEN, outline="black", fill="black")

def update_display():
    """Update the TFT display."""
    global current_temp, current_setpoint, current_time
    
    day = current_time.strftime("%a").upper()
    mon = current_time.strftime("%b").upper()
    line1 = day + " " + mon + " " + current_time.strftime("%d, %Y")
    line2 = current_time.strftime("%I:%M %p")
    line3 = "%2i" % (int(SET_POINT))
    line4 = "%2i" % (int(current_temp))
  
    clear_screen()
    screen_draw.text((  1,  1),line1, font=font14, fill=(255,255,255))
    screen_draw.text((  1, 20),line2, font=font14, fill=(255,255,255))
    (w,h) = font36.getsize(line3)
    x = SCREEN_WIDTH - w - 5
    if is_heating:
        color = (255,0,0)
    else:
        color = (255,255,255)    
    screen_draw.text((  x,  1),line3, font=font36, fill=color)
    (w,h) = font164.getsize(line4)
    x = (SCREEN_WIDTH - w)/2
    screen_draw.text((  x, 40),line4, font=font164, fill=(255,255,255))
    
    screen.paste(plot_temp_history(),(0,200))
    
    disp.display(screen)

#==============================================
# M A I N
#==============================================
while True:
    update_state()          # read sensors, determine current temp and setpoint
    thermostat()            # take appropriate action based on state
    update_database()       # add current data to database
    update_display()        # update the display
    time.sleep(60)          # sleep for 1 minute