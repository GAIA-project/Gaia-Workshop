#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
sys.dont_write_bytecode = True

from threading import Thread
import time

import gaia_text
import properties
import sparkworks
import grovepi
from grove_rgb_lcd import *
import math

import arduinoGauge
import datetime

exitapp = False
timestamp = 0
main_site = None
sensorValues = [0, 0, 0]

# select pins for the leds
pin1 = [2, 4]
pin2 = [3, 5]

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""

Button1 = 8
Button2 = 7
grovepi.pinMode(Button1, "INPUT")
grovepi.pinMode(Button2, "INPUT")
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")


# initiliaze the LCD screen color and value
text = gaia_text.loading_data
setText(text)
setRGB(60, 60, 60)


def updateData(site, param):
    global timestamp, maximum
    resource = sparkworks.siteResource(site, param)
    summary = sparkworks.summary(resource)
    val = summary["minutes5"]
    # print val
    timestamp = summary["latestTime"]
    return (val)


def getSensorData(SensorName):
    global sensorValues
    if not exitapp:
        for i in[0, 1, 2]:
            val = updateData(rooms[i], SensorName)
            sensorValues[i] = val


# Show the luminosity
def showLuminosity(light_value, a, b):
    if (light_value < 200):
        # red LED
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)
    else:
        # blue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)


# Print rooms
print "Όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένες αίθουσες:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'


# total Power
sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)
new_text = "Click button to start!"


def main():
    global text, new_text, timestamp, sensorValues
    time.sleep(1)
    t = 1
    new_t = 0
    rm = 0
    new_rm = 0
    val = 0

    print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
    getSensorData("Luminosity")
    new_text = "Loading data..."
    setRGB(50, 50, 50)

    while not exitapp:
        # Initialize
        if new_t != t:
            new_t = t
            timevalue = datetime.datetime.fromtimestamp((timestamp / 1000.0) - 300 * (t - 1))
            strtime = timevalue.strftime('%Y-%m-%d %H:%M:%S')
            print strtime

        val = sensorValues[rm][new_t - 1]
        showLuminosity(val, pin1[rm], pin2[rm])
        new_text = strtime + ": " + str(float("{0:.2f}".format(val)))
        setRGB(R[rm], G[rm], B[rm])
        # Update LCD and Terminal display
        if (text != new_text) or (new_rm != rm):
            text = new_text
            new_rm = rm
            print "Φωτεινότητα: ", properties.the_rooms[rm], val
            # print "LCD show:", text
            setText(text)
        # Detect the button that changes the hour
        try:
            if (grovepi.digitalRead(Button1)):
                setText("New minute")
                t = t + 1
                if t == 48:
                    setText("Continuing from the beggining")
                    t = 0
                time.sleep(.4)
        except IOError:
            print "Button Error"
        # Detect the button that changes the room
        try:
            if (grovepi.digitalRead(Button2)):
                rm = rm + 1
                if rm >= 2:
                    rm = 0
                time.sleep(.5)
        except IOError:
            print "Button Error"


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
