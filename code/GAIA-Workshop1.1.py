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

# Connect the Grove Button to digital port D8
# SIG,NC,VCC,GND
button = 8

new_text = ""
text1 = "Waiting\nfor a click..."
text2 = "YOU HAVE CLICKED\nTHE BUTTON!!"

grovepi.pinMode(button, "INPUT")
grovelcd.setRGB(0, 0, 0)
grovelcd.setText("")

while True:
    try:
        if new_text is not text1:
            new_text = text1
            grovelcd.setRGB(50, 50, 50)
            grovelcd.setText(new_text)
            print(new_text.replace("\n", " "))

        if grovepi.digitalRead(button):
            new_text = text2
            grovelcd.setRGB(0, 255, 0)
            grovelcd.setText(new_text)
            print(new_text.replace("\n", " "))
            time.sleep(.5)

    except IOError:
        print("Error")
