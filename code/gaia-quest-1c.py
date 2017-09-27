#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
import time
import gaia_text

import grovepi
from grove_rgb_lcd import *

# from grove_rgb_lcd import setText_norefresh as setText

pin1 = [2, 4]
pin2 = [3, 5]

exitapp = False

Interruptor = 0

# Motor=6
poten = 0
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

grovepi.pinMode(Interruptor, "INPUT")

# initialize the screen

setText("Starting..")
setRGB(50, 50, 50)
time.sleep(1)

mode = 0

text = ""
new_text = ""

def closeAllLeds():
    global pin1, pin2
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)

closeAllLeds()

def loop():
    global mode, led, new_text
    value = grovepi.analogRead(Interruptor)
   
    #interruptor off
    if value < 800:
	mode=0
    #interruptor on 
    else:
        mode=1

    if mode==0:
	new_text="Led 1 open"
	#open led 1 color blue
	grovepi.digitalWrite(pin1[0], 1)
        grovepi.digitalWrite(pin2[0], 0)
	#close led 2 
	grovepi.digitalWrite(pin1[1], 0)
        grovepi.digitalWrite(pin2[1], 0)

    if mode==1:
        new_text="Led 2 ppen"
	#open led 2 color blue
	grovepi.digitalWrite(pin1[1], 1)
        grovepi.digitalWrite(pin2[1], 0)

	#close led 1 
	grovepi.digitalWrite(pin1[0], 0)
        grovepi.digitalWrite(pin2[0], 0)

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
