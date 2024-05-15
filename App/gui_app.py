#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import sys, logging, math, time
from enum import Enum
from datetime import datetime, timedelta
sys.path.append("/home/pi/lg-master/LCD_Module_RPI_code/RaspberryPi/python")
from lib import LCD_2inch4
import gpiozero
from PIL import Image,ImageDraw,ImageFont, ImageEnhance
import queue  # Import the queue module


class State(Enum):
    WELCOME = 0
    MAIN = 1
    SCAN_OUT = 2
    MAIN_SCANNED = 3
    SCAN_OUT_SCANNED = 4
    SLEEP = 5

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



        # Setup buttons
        PIN_BTN_LEFT = 15
        PIN_BTN_RIGHT = 17
        PIN_BTN_MIDDLE = 14
        self.btn_left = gpiozero.Button(PIN_BTN_LEFT, bounce_time=0.05)
        self.btn_right = gpiozero.Button(PIN_BTN_RIGHT, bounce_time=0.05)
        self.btn_middle = gpiozero.Button(PIN_BTN_MIDDLE, bounce_time=0.05)
        self.commands_queue = queue.Queue()  # Define a queue for commands

        self.btn_left.when_pressed = lambda: self.commands_queue.put(('left',))
        self.btn_right.when_pressed = lambda: self.commands_queue.put(('right',))
        self.btn_middle.when_pressed = lambda: self.commands_queue.put(('middle',))

        self.is_btn_left_just_pressed = False
        self.is_btn_right_just_pressed = False
        self.is_btn_middle_just_pressed = False

        self.no_input_ts = datetime.now()

        self.font1 = ImageFont.truetype("Font00.ttf",48)

        self.exit = False

        self.init_welcome_state()

    def init_welcome_state(self):
        self.state = State.WELCOME
        self.welcome_text_y = 240
        self.welcome_start_ts = datetime.now()

        #Set the backlight to 100
        self.lcd.bl_DutyCycle(100)
#        self.lcd.clear()

    def init_main_state(self):
        self.state = State.MAIN
        self.menu_scroll_position = 0
        self.menu_cursor_position = 0
        self.no_input_ts = datetime.now()

    def init_scan_out_state(self):
        self.state = State.SCAN_OUT

    def init_main_scanned_state(self, barcode):
        self.state = State.MAIN_SCANNED
        self.scanned_item_name = self.inventory[barcode]["name"]
        self.scanned_start_ts = datetime.now()

    def init_scan_out_scanned_state(self, barcode):
        self.state = State.SCAN_OUT_SCANNED
        self.scanned_item_name = self.inventory[barcode]["name"]
        self.scanned_start_ts = datetime.now()

    def init_sleep_state(self):
        self.state = State.SLEEP
        #Set the backlight to 0
        self.lcd.bl_DutyCycle(0)

    def start(self):
        while self.exit == False:
            self.update_inputs()
            self.update()
            self.render()
    
    def shutdown(self):
        self.exit = True
    
    def update_inputs(self):
        self.is_btn_left_just_pressed = False
        self.is_btn_right_just_pressed = False
        self.is_btn_middle_just_pressed = False
        while not self.commands_queue.empty(): 
            self.no_input_ts = datetime.now()
            command = self.commands_queue.get()
            if command[0] == 'left':
                self.is_btn_left_just_pressed = True
            elif command[0] == 'right':
                self.is_btn_right_just_pressed = True
            elif command[0] == 'middle':
                self.is_btn_middle_just_pressed = True
        self.sec_since_last_input = (datetime.now() - self.no_input_ts).seconds

    def update(self):
        match self.state:
            case State.WELCOME:
                self.welcome_text_y += (120 - self.welcome_text_y) * 0.25
                ellapsed_time = datetime.now() - self.welcome_start_ts
                if ellapsed_time.seconds > 1:
                    self.init_main_state()
            case State.MAIN:
                if self.is_btn_left_just_pressed:
                    self.menu_cursor_position -= 1  # Move up in the list
                    if self.menu_cursor_position < 0:
                        self.menu_cursor_position = 0  # Ensure the position doesn't go below 0
                    if self.menu_scroll_position > self.menu_cursor_position:
                        self.menu_scroll_position = self.menu_cursor_position
                if self.is_btn_right_just_pressed:
                    self.menu_cursor_position += 1  # Move down in the list
                    length = len(self.process_items())
                    if self.menu_cursor_position > length - 1:
                        self.menu_cursor_position = length - 1
                    if self.menu_scroll_position + 4 < self.menu_cursor_position:
                        self.menu_scroll_position = self.menu_cursor_position - 4
                if self.is_btn_middle_just_pressed:
                    self.init_scan_out_state()
                if self.sec_since_last_input > 60:
                    self.init_sleep_state()
            case State.SCAN_OUT:
                if self.is_btn_middle_just_pressed or \
                   self.is_btn_left_just_pressed or \
                   self.is_btn_right_just_pressed:
                    self.init_main_state()
            case State.MAIN_SCANNED:
                elapsed_time = datetime.now() - self.scanned_start_ts
                if elapsed_time.seconds > 0.5:
                    self.init_main_state()
            case State.SCAN_OUT_SCANNED:
                elapsed_time = datetime.now() - self.scanned_start_ts
                if elapsed_time.seconds > 0.5:
                    self.init_scan_out_state()
            case State.SLEEP:
                if self.sec_since_last_input < 60:
                    self.init_welcome_state()

    def render(self):
        match self.state:
            case State.WELCOME:
                image = Image.open('leaf_320x240.jpg')
                enhancer = ImageEnhance.Brightness(image)
                # to reduce brightness by 50%, use factor 0.5
                image = enhancer.enhance(0.5)#translate(self.welcome_text_y, 240, 120, 1.0, 0.5))
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
                enhancer = ImageEnhance.Brightness(image)
                # to reduce brightness by 50%, use factor 0.5
                image = enhancer.enhance(0.5)
                
                cursor = Image.new("RGBA", image.size, (255, 255, 255, 0))
                b = ImageDraw.Draw(cursor)

                y1 = 15 + (self.menu_cursor_position-self.menu_scroll_position)*32*1.25
                y2 = y1 + 40
                b.rectangle((10, y1, 310, y2), fill=(255,255,255,50))
                
                image = Image.alpha_composite(image.convert("RGBA"), cursor)
                draw = ImageDraw.Draw(image)

                # Calculate the position for each item
                y_position = 15
                font_size = 32
                
                # Process items to get the top 3 expiring items
                top_expiring_items = self.process_items()
                
                # Display items based on the current position
                for i, item in enumerate(top_expiring_items):
                    if i >= self.menu_scroll_position and i < self.menu_scroll_position + 5:  # Only draw items within the current view
                        draw.multiline_text((10, y_position), f"{item['name']}", fill=(255, 255, 255), font=ImageFont.truetype("Font00.ttf", font_size), anchor='la')
                        draw.multiline_text((310, y_position), f"{item['days_left']}d", fill=(255, 255, 255), font=ImageFont.truetype("Font00.ttf", font_size), anchor='ra')
                        y_position += font_size *1.25  # Adjust the Y position for the next item
                
                # Update the LCD with the drawn content
                image=image.rotate(90, expand=True)        
                self.lcd.ShowImage(image)

            case State.SCAN_OUT:
                image = Image.open('leaf_320x240.jpg')
                enhancer = ImageEnhance.Brightness(image)
                # to reduce brightness by 50%, use factor 0.5
                image = enhancer.enhance(0.5)
                draw = ImageDraw.Draw(image)
                
                draw.multiline_text((160, 120), "Scan to Remove", fill=(255, 0, 0), font=ImageFont.truetype("Font00.ttf", 32), anchor='mm')

                # Update the LCD with the drawn content
                image=image.rotate(90, expand=True)        
                self.lcd.ShowImage(image)

            case State.MAIN_SCANNED:
                image = Image.open('leaf_320x240.jpg')
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.5)
                draw = ImageDraw.Draw(image)
                draw.multiline_text((160, 100), f"Added ", fill=(0, 255, 0), font=ImageFont.truetype("Font00.ttf", 32), anchor='mm')
                draw.multiline_text((160, 130), f"{self.scanned_item_name}", fill=(0, 255, 0), font=ImageFont.truetype("Font00.ttf", 32), anchor='mm')
                image = image.rotate(90, expand=True)
                self.lcd.ShowImage(image)

            case State.SCAN_OUT_SCANNED:
                image = Image.open('leaf_320x240.jpg')
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.5)
                draw = ImageDraw.Draw(image)
                draw.multiline_text((160, 100), f"Removed ", fill=(255, 0, 0), font=ImageFont.truetype("Font00.ttf", 32), anchor='mm')
                draw.multiline_text((160, 130), f"{self.scanned_item_name}", fill=(255, 0, 0), font=ImageFont.truetype("Font00.ttf", 32), anchor='mm')
                image = image.rotate(90, expand=True)
                self.lcd.ShowImage(image)
            
            case State.SLEEP:
                image = Image.new("RGB", (320,240), (0, 0, 0))
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

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
