#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
import time
import gaia_text

import grovepi
from grove_rgb_lcd import *

pinAYellow = 2 
pinAWhite = 3
pinBYellow = 4
pinBWhite = 5

exitapp = False

Button = 8

#Declare the LED pins as OUTPUT
grovepi.pinMode(pinAYellow, "OUTPUT")
grovepi.pinMode(pinAWhite, "OUTPUT")
grovepi.pinMode(pinBYellow, "OUTPUT")
grovepi.pinMode(pinBWhite, "OUTPUT")

#Declare the Switch pins as INPUT
grovepi.pinMode(Button, "INPUT")

# initialize the screen
setText("Starting..")
setRGB(50, 50, 50)
time.sleep(1)

open = 0
text = ""
new_text = ""

def closeAllLeds():
    global pinAYellow,pinAWhite,pinBYello,pinBWithe	
    #CLose LESD A	
    grovepi.digitalWrite(pinAYellow, 0)
    grovepi.digitalWrite(pinAWhite, 0)
    #Close LED B	
    grovepi.digitalWrite(pinBYellow, 0)
    grovepi.digitalWrite(pinBWhite, 0)

closeAllLeds()

def loop():
    global pinAYellow,pinAWhite,pinBYello,pinBWithe,new_text,open
    if grovepi.digitalRead(Button):
	open =1
    #when click the button
    if open == 1:
	new_text="Leds  Open"
	#open led A color blue
	grovepi.digitalWrite(pinAYellow, 1)
	grovepi.digitalWrite(pinAWhite, 0)

	#open led B color blue
	grovepi.digitalWrite(pinBYellow, 1)
	grovepi.digitalWrite(pinBWhite, 0)

	open=0
    	
    else:
	new_text="All leds close"
	closeAllLeds()

def main():
    global text,new_text
    while not exitapp:
        loop()
        if text != new_text:
            text = new_text
            print "settext:", text
            setText(text)

try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
