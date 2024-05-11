#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import sys 
sys.path.append("/home/pi/lg-master/LCD_Module_RPI_code/RaspberryPi/python")
from lib import LCD_2inch4
from PIL import Image,ImageDraw,ImageFont  
import gpiozero



class App():
    def __init__(self):
        
        # LCD pins
        RST = 27
        DC = 25
        BL = 18
        bus = 0 
        device = 0
        
        self.lcd = LCD_2inch4.LCD_2inch4()

        # Initialize library.
        self.lcd.Init()

        #Set the backlight to 100
        self.lcd.bl_DutyCycle(100)

        # Setup buttons
        PIN_BTN_LEFT = 14
        PIN_BTN_RIGHT = 17
        PIN_BTN_MIDDLE = 15
        self.btn_left = gpiozero.Button(PIN_BTN_LEFT)
        self.btn_right = gpiozero.Button(PIN_BTN_RIGHT)
        self.btn_middle = gpiozero.Button(PIN_BTN_MIDDLE)
        self.btn_left.when_pressed = self.button_pressed
        self.btn_right.when_pressed = self.button_pressed
        self.btn_middle.when_pressed = self.button_pressed

        self.font1 = ImageFont.truetype("Font00.ttf",48)

        self.update_screen()
    

    def button_pressed(self, caller):
        if caller == self.btn_left:
            print('Left button pressed')
        if caller == self.btn_right:
            print('Right button pressed')
        if caller == self.btn_middle:
            print('Middle button pressed')
        
        self.update_screen()
        
    def update_screen(self):

        image = Image.open('leaf_320x240.jpg')	
        draw = ImageDraw.Draw(image)

        draw.text((35, 68), 'Hello world', fill = "WHITE",font=self.font1)

        image=image.rotate(90, expand=True)        
        self.lcd.ShowImage(image)