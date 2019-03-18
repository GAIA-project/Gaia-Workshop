#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaiapi

switch = 0

# select pins for the leds
pins = {'A': {'yellow': 2, 'white': 3},
        'B': {'yellow': 4, 'white': 5},
        'C': {'yellow': 6, 'white': 7}}

# select colors for the rooms
lcd_colors = [[255, 0, 255],
              [255, 128, 0],
              [0, 255, 0]]

text = ""
new_text = ""
exitapp = False


def setup():
    # Declare the Switch pins as INPUT
    grovepi.pinMode(switch, "INPUT")
    # Declare the LED pins as OUTPUT
    grovepi.pinMode(pins['A']['yellow'], "OUTPUT")
    grovepi.pinMode(pins['A']['white'], "OUTPUT")
    grovepi.pinMode(pins['B']['yellow'], "OUTPUT")
    grovepi.pinMode(pins['B']['white'], "OUTPUT")
    # Initialize the screen
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText("Starting..")

    time.sleep(1)


def loop():
    global text, new_text
    value = grovepi.analogRead(switch)
    # interruptor off
    if value < 800:
        new_text = "All Leds Closed"
        # CLose LED A
        grovepi.digitalWrite(pins['A']['yellow'], 0)
        grovepi.digitalWrite(pins['A']['white'], 0)
        # Close LED B
        grovepi.digitalWrite(pins['B']['yellow'], 0)
        grovepi.digitalWrite(pins['B']['white'], 0)
    # interruptor on
    else:
        new_text = "All Leds Open"
        # open led A color blue
        grovepi.digitalWrite(pins['A']['yellow'], 1)
        grovepi.digitalWrite(pins['A']['white'], 0)
        # open led B color blue
        grovepi.digitalWrite(pins['B']['yellow'], 1)
        grovepi.digitalWrite(pins['B']['white'], 0)

    if new_text is not text:
        text = new_text
        grovelcd.setText(text)
        print(text)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
