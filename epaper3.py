# ~/toma/bcm2835-1.68/e-Paper/RaspberryPi_JetsonNano/python/examples
# -*- coding:utf-8 -*-


import sys
import os
import time
import logging


#from waveshare_epd import epd2in13bc
from waveshare_epd import epd2in9bc
from PIL import Image, ImageDraw, ImageFont


from bs4 import BeautifulSoup

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
import requests
import re

#正規表現、URL取得、HTML整形ライブラリ

from selenium import webdriver
from html.parser import HTMLParser
from os import linesep
import folium

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

DATEFORMAT = "%a %x"
TIMEFORMAT = "%H:%M"
FONTBI = os.path.join(picdir, 'Futura Bold Italic font.otf')
FONT = os.path.join(picdir, 'Futura Medium Italic font.otf')
FONTWEATHER = os.path.join(picdir,'meteocons-webfont.ttf')
FONTWEATHERBIG = os.path.join(picdir,'meteocons-webfont.ttf')
FONTJP = os.path.join(picdir,'Nsimsun.ttf')



owm = pyowm.OWM('abb59b67e8d14bf5559688293f257d4b')
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





DISPMODE_EARTHQUAKE = 1
DISPMODE_WEATHER = 2
DISPMODE_CLOCK = 3
DISPMODE_SYSSTATS = 4

class Fonts:
    def __init__(self,timefont_size,datefont_size,infofont_size,smallfont_size,fontweather_size,fontweatherbig_size,fontjp_size):
        self.timefont = ImageFont.truetype(FONTBI,timefont_size)
        self.datefont = ImageFont.truetype(FONTBI,datefont_size)
        self.infofont = ImageFont.truetype(FONT,infofont_size)
        self.smallfont = ImageFont.truetype(FONT,smallfont_size)
        self.fontweather = ImageFont.truetype(FONTWEATHER,fontweather_size)
        self.fontweatherbig = ImageFont.truetype(FONTWEATHERBIG,fontweatherbig_size)
        self.fontjap = ImageFont.truetype(FONTJP,fontjp_size)
 
        
        
class Display:
    epd = None
    fonts = None
    mode = DISPMODE_EARTHQUAKE



    def __init__(self):
        self.fonts = Fonts(timefont_size = 70, datefont_size = 35, infofont_size = 13, smallfont_size=20,fontweather_size = 30,fontweatherbig_size = 34,fontjp_size=13)

        #self.epd = epd2in13bc.EPD()
        self.epd = epd2in9bc.EPD()
        self.epd.init()
        logging.info("Init Sys")

    
    
    def start(self,start_mode=DISPMODE_EARTHQUAKE):
        self.mode = start_mode
        while True:
            #if DISPMODE_SYSSTATS == self.mode:
            self.mode = DISPMODE_EARTHQUAKE
            self.getinfo()
            time.sleep(45)
                #self.mode = DISPMODE_SYSSTATS
            #self.sleep_until_next_min() 


    def getinfo(self):
        earthquake = requests.get('https://api.p2pquake.net/v1/human-readable?limit=4')
        earthquake_data = earthquake.content.decode('utf-8')
        earthquake_publish_time = []
        earthquake_time = []
        earthquake_coodinates = []  #震源地の緯度経度
        earthquake_scale = []   #最大震度の値
        earthquake_hypocenter = []  #震源地

        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)
        Bimage = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw1 = ImageDraw.Draw(Limage)
        drawblk = ImageDraw.Draw(Bimage)

        indexe = 0

        # str式のjsonデータをdict式のデータへ変換：
        dict_earthquake_data = json.loads(earthquake_data)
        #print(dict_earthquake_data)
        for data in dict_earthquake_data:
            if(data["code"] == 551):
                indexe = dict_earthquake_data.index(data)
                #print(dict_earthquake_data.index(data)) 
                #print(dict_earthquake_data[dict_earthquake_data.index(data)])
                t1 = dict_earthquake_data[dict_earthquake_data.index(data)]
                t2 = t1.get('earthquake')
                time = t1.get('time')

                #print(t2.get('hypocenter'))
                t3 = t2.get('hypocenter')
                center = t3.get('name')
                #center2 = 
                depth = t3.get('depth')
                mag = t3.get('magnitude')
                t4 = t3.get('latitude')+'  '+t3.get('longitude')
                string1 = '-'+str(indexe+1)+'- '+'Time:'+time[5:19]+' @'+center
                string2 = 'Mag:'+mag+'  @ '+t4

                #drawblk.text((5,5+indexe*10), str(t1), font = self.fonts.smallfont, fill = 0)
                draw1.text((5, 5+indexe*27), string1, font = self.fonts.fontjap, fill = 0)
                draw1.text((5, 17+indexe*27), string2, font = self.fonts.fontjap, fill = 0)
                draw1.line((5,31+indexe*27, 270, 31+indexe*27), fill = 0)
            else:
                string3 = '-'+str(indexe+2) +'- 尚未确认的地震源'
                string4 = '--- 震源地はまだ確認されていない'
                draw1.text((5, 5+(indexe+1)*27), string3, font = self.fonts.fontjap, fill = 0)
                draw1.text((5, 17+(indexe+1)*27), string4, font = self.fonts.fontjap, fill = 0)
                draw1.line((5,31+(indexe+1)*27, 270, 31+(indexe+1)*27), fill = 0)

        
        self.epd.display(self.epd.getbuffer(Limage))
        logging.info("Earthquake Updated")   


if __name__ == '__main__':

    display = Display()
    logging.info("Display Start")
    display.start(DISPMODE_CLOCK)