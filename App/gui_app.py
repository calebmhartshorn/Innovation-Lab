#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import sys, logging, math
from enum import Enum
from datetime import datetime, timedelta
sys.path.append("/home/pi/lg-master/LCD_Module_RPI_code/RaspberryPi/python")
from lib import LCD_2inch4
import gpiozero
from PIL import Image,ImageDraw,ImageFont  


class State(Enum):
    WELCOME = 0
    MAIN = 1
    
class App():

    def __init__(self, logger, inventory):

        self.logger = logger    
        self.inventory = inventory

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

        self.exit = False

        self.init_welcome_state()

    def init_welcome_state(self):
        self.state = State.WELCOME
        self.welcome_text_y = 240
        self.welcome_start_ts = datetime.now()

    def init_main_state(self):
        self.state = State.MAIN
        print(self.process_items())

    def start(self):
        while self.exit == False:
            self.update()
            self.render()
    
    def shutdown(self):
        self.exit = True


    def button_pressed(self, caller):
        if caller == self.btn_left:
            print('Left button pressed')
        if caller == self.btn_right:
            print('Right button pressed')
        if caller == self.btn_middle:
            print('Middle button pressed')
            self.welcome_text_y = 240
        
    def update(self):
        match self.state:
            case State.WELCOME:
                self.welcome_text_y += (120 - self.welcome_text_y) * 0.25
                ellapsed_time = datetime.now() - self.welcome_start_ts
                if ellapsed_time.seconds > 3:
                    self.init_main_state()

    def render(self):
        match self.state:
            case State.WELCOME:
                image = Image.open('leaf_320x240.jpg')
                draw = ImageDraw.Draw(image)
                
                txt = Image.new("RGBA", image.size, (255, 255, 255, 0))
                b = ImageDraw.Draw(txt)
                b.multiline_text(
                    (160, self.welcome_text_y), 
                    'Welcome', 
                    fill = (255,255,255,255-round(self.welcome_text_y-120)*3),
                    font=self.font1,
                    anchor='mm')
                
                image = Image.alpha_composite(image.convert("RGBA"), txt)

                image=image.rotate(90, expand=True)        
                self.lcd.ShowImage(image)
            
            case State.MAIN:                
                image = Image.open('leaf_320x240.jpg')
                draw = ImageDraw.Draw(image)
                draw.text((10, 10), "Top 3 Expiring Items", fill=(255, 255, 255), font=self.font1)
                
                # Calculate the position for each item
                y_position = 60
                font_size = 20
                
                # Process items to get the top 3 expiring items
                top_expiring_items = self.process_items()[:5]
                
                # Draw each item
                for item in top_expiring_items:
                    draw.text((10, y_position), f"{item['name']}: {item['days_left']} days left", fill=(255, 255, 255), font=ImageFont.truetype("Font00.ttf", font_size))
                    y_position += font_size + 5  # Adjust the Y position for the next item
                
                # Update the LCD with the drawn content
                image=image.rotate(90, expand=True)        
                self.lcd.ShowImage(image)
        
    # Returns list of item scans sorted by days left
    def process_items(self):
        # Initialize an empty list to store the processed items
        processed_items = []
        
        # Iterate through each item
        for item_id, item_data in self.inventory.items():
            # Iterate through each scan date
            for scan_date in item_data['scans']:
                # Calculate the days left for the scan date
                days_left = self.calculate_days_left(scan_date, item_data['shelf_life'])
                
                # Create a new dictionary with the name and days left
                item_with_days_left = {
                    'name': item_data['name'],
                    'days_left': days_left
                }
                
                # Append the new dictionary to the processed items list
                processed_items.append(item_with_days_left)
        
        # Sort the processed items by days left
        processed_items.sort(key=lambda x: x['days_left'])
        
        return processed_items

    def calculate_days_left(self, date_string, shelf_life):
        # Parse the given date string into a datetime object
        start_date = datetime.strptime(date_string, '%Y-%m-%d')
        
        # Calculate the expiration date by adding the shelf life to the start date
        expiration_date = start_date + timedelta(days=shelf_life)

        # Get the current date
        current_date = datetime.now()

        # Calculate the difference in seconds between the expiration date and the current date
        difference_seconds = (expiration_date - current_date).total_seconds()

        # Convert seconds to days (1 day = 24 * 60 * 60 seconds)
        days_left = math.ceil(difference_seconds / (60 * 60 * 24))

        return days_left

