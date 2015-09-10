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

import time

current_time        = None
current_temp        = None
current_setpoint    = None
is_heating          = False
temp_history        = 240*[None]

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
    return 32.0 + (degC * 9.0)/5.0

def LEDOn():
    GPIO.output(LED_PIN, GPIO.HIGH)
    
def LEDOff():
    GPIO.output(LED_PIN, GPIO.LOW)
    
def get_temperature():
    bmp180_temp = bmp180.read_temperature()
    mcp9808_temp = mcp9808.readTempC()
    temp = 0.5 * (bmp180_temp + mcp9808_temp)
    temp = CToF(temp)
    return temp

def get_setpoint():
    return SET_POINT

def thermostat():
    global current_temp
    global current_setpoint
    global is_heating
    if current_temp < current_setpoint:
        is_heating = True
        LEDOn()
    else:
        is_heating = False
        LEDOff()

def update_temp_history():
    global current_temp
    global current_time
    global temp_history
    
    # absolute minutes
    m = current_time.tm_hour*60 + current_time.tm_min
    
    # reset if just after midnite
    if m<=1:
        for i in xrange(len(temp_history)):
            temp_history[i]=None
            
    # get index
    i = int(SCREEN_WIDTH * float(m)/float(1440))
    
    # update temp as necessary
    temp = temp_history[i]
    if temp==None:
        temp_history[i] = current_temp
    else:
        temp_history[i] = 0.5 * (temp + current_temp)
        
def plot_temp_history():
    global temp_history
    W = 240
    H = 120
    MAXT = 90.0
    MINT = 60.0
    plot = Image.new("RGB",(W,H),"black")
    plot_draw = ImageDraw.Draw(plot)
    border = [(0,0),(W-1,0),(W-1,H-1),(0,H-1),(0,0)]
    plot_draw.line(border,fill=(0,255,0),width=1)
    points=[]
    for x,temp in enumerate(temp_history):
        if temp==None:
            continue
        y = H - int(H*(temp-MINT)/(MAXT-MINT))
        points.append((x,y))
    plot_draw.point(points,fill=(0,255,0))
    return plot    
    
            
def clear_screen():
    screen_draw.rectangle(WHOLE_SCREEN, outline="black", fill="black")

def update_display():
    global current_temp
    global current_setpoint
    global current_time
    
    day = time.strftime("%a",current_time).upper()
    mon = time.strftime("%b",current_time).upper()
    line1 = day + " " + mon + " " + time.strftime("%d, %Y",current_time)
    line2 = time.strftime("%I:%M %p",current_time)
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
    current_time = time.localtime()
    current_setpoint = get_setpoint()
    current_temp = get_temperature()
    thermostat()
    update_temp_history()
    update_display()
    time.sleep(60)