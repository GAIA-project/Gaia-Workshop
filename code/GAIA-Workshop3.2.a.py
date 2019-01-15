#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
from copy import deepcopy
from threading import Thread
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
from grove_rgb_lcd import *
import gaia_text
import properties
from sparkworks import SparkWorks


# select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]
button = 8

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# variables for the sensors
temp = [0, 0, 0]
humi = [0, 0, 0]

opt = 0
text = ""
new_text = ""
exitapp = False
sparkworks = SparkWorks(properties.client_id, properties.client_secret)

# Assign input and output pins
grovepi.pinMode(button, "INPUT")
for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")


# Take new values from the data base
def updateSiteData(group, param):
    resource = sparkworks.groupDeviceResource(group['uuid'], param['uuid'])
    latest = sparkworks.latest(resource['uuid'])
    latest_value = float("{0:.1f}".format(float(latest["latest"])))
    return latest_value


def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            humi[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Relative Humidity"))
    for i in [0, 1, 2]:
        if not exitapp:
            temp[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Temperature"))


def threaded_function(arg):
    while not exitapp:
        getData()


def maximum(v):
    max_value = max(v[0], v[1], v[2])
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
    for i in [0, 1, 2]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Close all the leds
def closeAllLeds():
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


# Function that check the button
def checkButton():
    global opt
    try:
        if (grovepi.digitalRead(button)):
            print("έχετε πιέσει το κουμπί")
            if (opt < 2):
                opt = opt + 1
            else:
                opt = 0
            time.sleep(.5)
    except IOError:
        print("Button Error")


def calHI(t, hum):
    tmp = 1.8 * t + 32
    hy = -42.379 + 2.04901523 * tmp + 10.14333127 * hum - 0.22475541 * tmp * hum - 0.00683783 * tmp * tmp - 0.05481717 * hum * hum + 0.00122874 * tmp * tmp * hum
    hy = hy + 0.00085282 * tmp * hum * hum - 0.00000199 * tmp * tmp * hum * hum
    hy = (hy - 32) * 0.55
    return float("{0:.1f}".format(float(hy)))


def traverseSubGroups(group_uuid):
    _lowest = []
    _subgroups = sparkworks.subGroups(group_uuid)
    if len(_subgroups) == 0:
        _lowest = group_uuid
    else:
        for _sg in _subgroups:
            _lowest.append(traverseSubGroups(_sg['uuid']))
    return _lowest


def flatten_list(nested_list):
    nested_list = deepcopy(nested_list)
    while nested_list:
        sublist = nested_list.pop(0)
        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


closeAllLeds()
# Print rooms
print("Όνομα χρήστη:\n\t%s\n" % properties.username)
print("Επιλεγμένη αίθουσα:")
for room in properties.the_rooms:
    print('\t%s' % room.decode('utf-8'))
print('\n')

sparkworks.connect(properties.username, properties.password)
rooms_list = traverseSubGroups(properties.uuid)
rooms_list = list(flatten_list(rooms_list))
rooms = []
for room in rooms_list:
    site = sparkworks.group(room)
    if site['name'].encode('utf-8').strip() in properties.the_rooms:
        rooms.append(site)

print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
setText(gaia_text.loading_data)
setRGB(50, 50, 50)
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()


def loop():
    global new_text, change, show, opt, text
    hi = [0, 0, 0]
    for i in [0, 1, 2]:
        hi[i] = calHI(temp[i], humi[i])
    maximum(hi)
    lcd_temp = "T:{0:4.1f}oC".format(temp[opt])
    lcd_hi = "HI:{0:4.1f}".format(hi[opt]).rjust(16 - len(lcd_temp))
    lcd_hum = "H:{0:4.1f}%RH".format(humi[opt])
    new_text = lcd_temp + lcd_hi + lcd_hum
    setRGB(R[opt], G[opt], B[opt])
    time.sleep(.1)
    if text != new_text:
        print("Θερμοκρασία: {0:s}: {1:5.1f} oC ".format(properties.the_rooms[opt], temp[opt]))
        print("    Υγρασία: {0:s}: {1:5.1f} %RH".format(properties.the_rooms[opt], humi[opt]))
        print("         HI: {0:s}: {1:5.1f}".format(properties.the_rooms[opt], hi[opt]))
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
