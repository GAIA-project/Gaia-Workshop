#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
import time
from threading import Thread
import gaia_text
import properties
import sparkworks

import grovepi
from grove_rgb_lcd import *
import threading
import math

# select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# variables for the sensors
humidity = [0, 0, 0]
temperature = [0, 0, 0]

# Select the pins Outputs and inputs
Button = 8
grovepi.pinMode(Button, "INPUT")

for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

# initiliaze global variables
set = 0
exitapp = False


# Take new values from the data base
def updateSiteData(site, param):
    resource = sparkworks.siteResourceDevice(site, param)
    latest = sparkworks.latest(resource)
    latest_value = float("{0:.1f}".format(float(latest["latest"])))
    return latest_value


# Get data from
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], "Relative Humidity")
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], "Temperature")


def threaded_function(arg):
    while not exitapp:
        getData()


def maximum(v):
    max_value = max(v[0], v[1], v[2])
    #print max_value, v
    for i in [0, 1, 2]:
        if v[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Find out the minimum value
def minimum(v):
    min_value = min(v[0], v[1], v[2])
    #print min_value, v
    for i in [0, 1, 2]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


# Function that check the button
def checkButton():
    global set, exitapp, mode
    try:
        if (grovepi.digitalRead(Button)):
            print("έχετε πιέσει το κουμπί")
            if (set < 2):
                set = set + 1
            else:
                set = 0
            time.sleep(.8)

    except IOError:
        print("Button Error")


def calHI(t, hum):
    tmp = 1.8 * t + 32
    #print "tempera",tmp
    hy = -42.379 + 2.04901523 * tmp + 10.14333127 * hum - 0.22475541 * tmp * hum - 0.00683783 * tmp * tmp - 0.05481717 * hum * hum + 0.00122874 * tmp * tmp * hum
    hy = hy + 0.00085282 * tmp * hum * hum - 0.00000199 * tmp * tmp * hum * hum
    hy = (hy - 32) * 0.55
    #print "HY:",hy
    return float("{0:.2f}".format(float(hy)))


# Print rooms
closeAllLeds()

print("όνομα χρήστη:\n\t%s\n" % properties.username)
print("Επιλεγμένη αίθουσα:")
for room in properties.the_rooms:
    print('\t%s' % room.decode('utf-8'))
print('\n')


sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)

print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
setText(gaia_text.loading_data)
setRGB(50, 50, 50)
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()

text = ""
new_text = ""


def loop():
    global new_text, change, show, set, text
    hi = [0, 0, 0]
    for i in [0, 1, 2]:
        hi[i] = calHI(temperature[i], humidity[i])
    maximum(hi)
    new_text = ("T:" + str(temperature[set]) + "oC,H:" + str(humidity[set]) + "%RH HI = " + str(hi[set]))
    setRGB(R[set], G[set], B[set])
    time.sleep(.1)
    if text != new_text:
        print("θερμοκρασία " + properties.the_rooms[set] + ": " + str(temperature[set]) + "  Centrigrade")
        print("υγρασία " + properties.the_rooms[set] + ": " + str(humidity[set]) + " %RH")
        print("HI " + properties.the_rooms[set] + ": " + str(hi[set]))
        text = new_text
        setText(text)


def main():
    while not exitapp:
        checkButton()
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
