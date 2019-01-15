#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
from grove_rgb_lcd import *
import gaia_text

# select pins for the leds
pins = {'A': {'yellow': 2, 'white': 3},
        'B': {'yellow': 4, 'white': 5},
        'C': {'yellow': 6, 'white': 7}}

# select colors for the rooms
lcd_colors = [[255, 0, 255],
              [255, 128, 0],
              [0, 255, 0]]

exitapp = False

switch = 0

# Declare the LED pins as OUTPUT
grovepi.pinMode(pins['A']['yellow'], "OUTPUT")
grovepi.pinMode(pins['A']['white'], "OUTPUT")
grovepi.pinMode(pins['B']['yellow'], "OUTPUT")
grovepi.pinMode(pins['B']['white'], "OUTPUT")

# Declare the Switch pins as INPUT
grovepi.pinMode(switch, "INPUT")

# initialize the screen

setText("Starting..")
setRGB(50, 50, 50)
time.sleep(1)

mode = 0

text = ""
new_text = ""


def closeAllLeds():
    global pins
    # CLose LESD A
    grovepi.digitalWrite(pins['A']['yellow'], 0)
    grovepi.digitalWrite(pins['A']['white'], 0)
    # Close LED B
    grovepi.digitalWrite(pins['B']['yellow'], 0)
    grovepi.digitalWrite(pins['B']['white'], 0)


closeAllLeds()


def loop():
    global pins, new_text
    value = grovepi.analogRead(switch)
    # interruptor off
    if value < 800:
        new_text = "All Leds Closed"
        closeAllLeds()
    # interruptor on
    else:
        new_text = "All Leds Open"
        # open led A color blue
        grovepi.digitalWrite(pins['A']['yellow'], 1)
        grovepi.digitalWrite(pins['A']['white'], 0)

        # open led B color blue
        grovepi.digitalWrite(pins['B']['yellow'], 1)
        grovepi.digitalWrite(pins['B']['white'], 0)


def main():
    global text, new_text
    while not exitapp:
        loop()
        if text != new_text:
            text = new_text
            print("setText: " + text)
            setText(text)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
