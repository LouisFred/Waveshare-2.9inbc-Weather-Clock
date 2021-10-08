# ~/toma/bcm2835-1.68/e-Paper/RaspberryPi_JetsonNano/python/examples
# -*- coding:utf-8 -*-


import sys
import os
import time
import logging
logging.basicConfig(level=logging.DEBUG)

#from waveshare_epd import epd2in13bc
from waveshare_epd import epd2in9bc
from PIL import Image, ImageDraw, ImageFont

import traceback
from datetime import datetime
import subprocess
import psutil
import socket
import random
import json
import textwrap
import epdconfig
import pyowm

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

DATEFORMAT = "%a %x"
TIMEFORMAT = "%H:%M"
FONTBI = os.path.join(picdir, 'Futura Bold Italic font.otf')
FONT = os.path.join(picdir, 'Futura Medium Italic font.otf')
FONTWEATHER = os.path.join(picdir,'meteocons-webfont.ttf')
FONTWEATHERBIG = os.path.join(picdir,'meteocons-webfont.ttf')
#BOUNCETIME = 500


owm = pyowm.OWM('abb*******b')
city_id = 2110683 #Tsukuba City
weather_icon_dict = {200 : "6", 201 : "6", 202 : "6", 210 : "6", 211 : "6", 212 : "6", 
                     221 : "6", 230 : "6" , 231 : "6", 232 : "6", 

                     300 : "7", 301 : "7", 302 : "8", 310 : "7", 311 : "8", 312 : "8",
                     313 : "8", 314 : "8", 321 : "8", 
 
                     500 : "7", 501 : "7", 502 : "8", 503 : "8", 504 : "8", 511 : "8", 
                     520 : "7", 521 : "7", 522 : "8", 531 : "8",

                     600 : "V", 601 : "V", 602 : "W", 611 : "X", 612 : "X", 613 : "X",
                     615 : "V", 616 : "V", 620 : "V", 621 : "W", 622 : "W", 

                     701 : "M", 711 : "M", 721 : "M", 731 : "M", 741 : "M", 751 : "M",
                     761 : "M", 762 : "M", 771 : "M", 781 : "M", 

                     800 : "1", 

                     801 : "H", 802 : "N", 803 : "N", 804 : "Y"
}


#DISPMODE_LOGO = 1
DISPMODE_WEATHER = 2
DISPMODE_CLOCK = 3
DISPMODE_SYSSTATS = 4

class Fonts:
    def __init__(self,timefont_size,datefont_size,infofont_size,smallfont_size,fontweather_size,fontweatherbig_size):
        self.timefont = ImageFont.truetype(FONTBI,timefont_size)
        self.datefont = ImageFont.truetype(FONTBI,datefont_size)
        self.infofont = ImageFont.truetype(FONT,infofont_size)
        self.smallfont = ImageFont.truetype(FONT,smallfont_size)
        self.fontweather = ImageFont.truetype(FONTWEATHER,fontweather_size)
        self.fontweatherbig = ImageFont.truetype(FONTWEATHERBIG,fontweatherbig_size)
 
        
        
class Display:
    epd = None
    fonts = None
    mode = DISPMODE_WEATHER



    def __init__(self):
        self.fonts = Fonts(timefont_size = 70, datefont_size = 30, infofont_size = 13, smallfont_size=20,fontweather_size = 30,fontweatherbig_size = 34)

        #self.epd = epd2in13bc.EPD()
        self.epd = epd2in9bc.EPD()
        self.epd.init()
        logging.info("Init Sys")

    
    
    def start(self,start_mode=DISPMODE_WEATHER):
        self.mode = start_mode
        while True:
            if DISPMODE_SYSSTATS == self.mode:
                self.draw_system_data()
                self.mode = DISPMODE_WEATHER
            elif DISPMODE_CLOCK == self.mode:
               self.draw_clock_data()
                #self.mode = DISPMODE_LOGO
               self.mode = DISPMODE_SYSSTATS
            else :
                self.mode == DISPMODE_WEATHER
                self.draw_weather_data()
                self.mode = DISPMODE_CLOCK
            #else:
                #self.mode = DISPMODE_LOGO
                #self.draw_rpi_logo()
                #self.mode = DISPMODE_SYSSTATS
            self.sleep_until_next_min() 

    def sleep_until_next_min(self):
        now = datetime.now()
        seconds_until_next_minute = 60-now.time().second
        time.sleep(seconds_until_next_minute) #loop per min
        #time.sleep(25)
        logging.info("Sleep until next minute")

    def draw_rpi_logo(self):
        blackimage1 = Image.new('1', (self.epd.height, self.epd.width), 255)  
        redimage1 = Image.new('1', (self.epd.height, self.epd.width), 255) 
        image1 = Image.open(os.path.join(picdir, 't1.bmp'))
        image2 = Image.open(os.path.join(picdir, 't2.bmp'))
        blackimage1.paste(image1, (0,0))
        redimage1.paste(image2,(0,0))    
        self.epd.display(self.epd.getbuffer(blackimage1), self.epd.getbuffer(redimage1))
        
        logging.info("Show Picture ")

    def draw_clock_data(self):
        datetime_now = datetime.now()
        datestring = datetime_now.strftime(DATEFORMAT).capitalize()
        timestring = datetime_now.strftime(TIMEFORMAT)
        

        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        Bimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 296×128
        width = self.epd.width
        height = self.epd.height
        draw = ImageDraw.Draw(Limage)
        drawbl = ImageDraw.Draw(Bimage)
        draw.text((25, 0), timestring, font = self.fonts.timefont, fill = 0)
        drawbl.text((27,2), timestring, font = self.fonts.timefont, fill = 0)
        draw.text((30, 70), datestring, font = self.fonts.datefont, fill = 0)
        draw.text((31, 72), datestring, font = self.fonts.datefont, fill = 0)
        draw.text((32, 71), datestring, font = self.fonts.datefont, fill = 1)
        self.epd.display(self.epd.getbuffer(Limage),self.epd.getbuffer(Bimage))
        logging.info("Clock Updated")


    def draw_weather_data(self):
        obs = owm.weather_at_id(city_id)
        location = obs.get_location().get_name()
        weather = obs.get_weather()
        reftime = weather.get_reference_time()
        description = weather.get_detailed_status()
        temperature = weather.get_temperature(unit='celsius')
        humidity = weather.get_humidity()
        pressure = weather.get_pressure()
        clouds = weather.get_clouds()
        wind = weather.get_wind()
        rain = weather.get_rain()
        sunrise = weather.get_sunrise_time()
        sunset = weather.get_sunset_time()
        
        #print("location: " + location)
        #print("weather: " + str(weather))
        #print("description: " + description)
        #print("temperature: " + str(temperature))
        #print("humidity: " + str(humidity))
        #print("pressure: " + str(pressure))
        #print("clouds: " + str(clouds))
        #print("wind: " + str(wind))
        #print("rain: " + str(rain))
        #print("sunrise: " + time.strftime( '%H:%M', time.localtime(sunrise)))
        #print("sunset: " + time.strftime( '%H:%M', time.localtime(sunset)))

        Limage1 = Image.new('1', (self.epd.height, self.epd.width), 255)
        Bimage1 = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw1 = ImageDraw.Draw(Limage1)
        drawblk = ImageDraw.Draw(Bimage1)
        tempstr = str(temperature.get('temp'))
        tempmax = str(temperature.get('temp_max'))
        tempmin = str(temperature.get('temp_min'))
        tempstring = 'TEMP'+'@'+tempstr+u"\N{DEGREE SIGN}"+'C   '+'             +'+tempmax+u"\N{DEGREE SIGN}"+'C '+' -'+tempmin+u"\N{DEGREE SIGN}"+'C';
        pressurestr = 'AERO Pressure'+'@'+str(pressure.get('sea_level'))+'hPA'
        windstr = 'Wind'+'@'+str(wind.get('speed'))+'                                 '+'Degree'+'@'+str(wind.get('deg'))
        desstr = str(description)
        w1 = len(description)
        w2 = 296-w1-95
        #print(w1)
        #print(type(w1))
        #print(w2)


        drawblk.text((5,0), location, font = self.fonts.smallfont, fill = 0)
        draw1.text((155, 7), "Observed @" + time.strftime( '%I:%M %p', time.localtime(reftime)), font = self.fonts.infofont, fill = 0)
        draw1.text((5,23),windstr,font = self.fonts.infofont,fill=0)

        draw1.text((5,40),tempstring,font = self.fonts.infofont,fill=0)

        draw1.text((5, 55), pressurestr,font = self.fonts.infofont,fill = 0)
        drawblk.text((170, 55), str("Humidity @"+"{}% RH".format(int(round(humidity)))),font = self.fonts.infofont,fill = 0)

        drawblk.text((195, 80), "A", font = self.fonts.fontweather, fill = 0)
        drawblk.text((245, 80), "J", font = self.fonts.fontweather, fill = 0)
        draw1.text((w2, 108), time.strftime( '%I:%M ', time.localtime(sunrise)), font = self.fonts.infofont, fill = 0)
        draw1.text((245, 108), time.strftime( '%I:%M ', time.localtime(sunset)), font = self.fonts.infofont, fill = 0)
        draw1.text((8, 108), description, font = self.fonts.infofont, fill = 0)
        drawblk.text((20,77), weather_icon_dict[weather.get_weather_code()], font = self.fonts.fontweatherbig, fill = 0)

        self.epd.display(self.epd.getbuffer(Limage1),self.epd.getbuffer(Bimage1))
        logging.info("weather Updated")

        time.sleep(2500)
        logging.info("2500s slept")




    def draw_system_data(self):
        corestring = 'CPU freq: ' + str(psutil.cpu_freq().current) + ' MHz';
        usagestring = 'CPU usage: ' + str(psutil.cpu_percent());
        tempstring = 'CPU temp. ' + str(round(psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current)) + u"\N{DEGREE SIGN}";
        memstring = 'Free RAM: ' + str(int(psutil.virtual_memory().available/(1024*1024))) + ' MiB';
        psstring = 'Running ps: ' + str(len(psutil.pids()))
        ifaddresses = [ifname+' '+str(ip.address) for ifname in psutil.net_if_addrs().keys() for ip in psutil.net_if_addrs()[ifname] if ip.family == socket.AF_INET]
        sysstring = corestring + '\n' + usagestring + '\n' + tempstring + '\n' + memstring + '\n' + psstring
        netstring = '\n'.join(ifaddresses)

        Limage2 = Image.new('1', (self.epd.height, self.epd.width), 255)
        Bimage2 = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(Limage2)
        drawbl = ImageDraw.Draw(Bimage2)
        draw.text((10, 10), sysstring, font = self.fonts.infofont, fill = 0)
        drawbl.text((10, 110), netstring, font = self.fonts.infofont, fill = 0)
        self.epd.display(self.epd.getbuffer(Limage2),self.epd.getbuffer(Bimage2))
        logging.info("Sys Info Updated")
        time.sleep(125)
        logging.info("25s slept")

if __name__ == '__main__':

    display = Display()
    logging.info("Display Start")
    display.start(DISPMODE_CLOCK)



    
