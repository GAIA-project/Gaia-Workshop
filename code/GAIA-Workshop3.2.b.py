#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
from copy import deepcopy
from threading import Thread
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
from grove_rgb_lcd import *
import gaia_text
import properties
from sparkworks import SparkWorks
import arduino_gauge_i2c as arduino_gauge


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
block_gauge = False
text = ""
new_text = ""
exitapp = False
sparkworks = SparkWorks(properties.client_id, properties.client_secret)


# Assign input and output pins
grovepi.pinMode(button, "INPUT")
for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

arduino_gauge.connect()
arduino_gauge.write(1, 1, 1)


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
    global block_gauge
    wait = 0
    while not exitapp:
        if wait >= 100:
            block_gauge = True
            getData()
            time.sleep(.5)
            block_gauge = False
            # print("Finish get data")
            wait = 0
        else:
            wait += 1
            time.sleep(.1)


def mapDItoGauge(di):
    led = 0
    word = " "
    if di < -1.7:
        led = 1
        word = "POLY KRIO"
    if -1.7 < di < 12.9:
        led = 2
        word = "KRIO"
    if 12.9 < di < 14.9:
        led = 3
        word = "DROSIA"
    if 15.0 < di < 19.9:
        led = 4
        word = "KANONIKO"
    if 20.0 < di < 26.4:
        led = 5
        word = "ZESTH"
    if 26.5 < di < 29.9:
        led = 6
        word = "POLY ZESTH"
    if 30.0 < di:
        led = 7
        word = "KAFSONAS"
    return led, word


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


def calcDI(t, rh):
    DI = t - 0.55 * (1 - 0.01 * rh) * (t - 14.5)
    return float("{0:.1f}".format(float(DI)))


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
    global new_text, change, show, opt, text, block_gauge
    di = [0, 0, 0]
    di_map = [None, None, None]
    for i in range(3):
        di[i] = calcDI(temp[i], humi[i])
        di_map[i] = mapDItoGauge(di[i])
    if not block_gauge:
        arduino_gauge.write(di_map[0][0], di_map[1][0], di_map[2][0])
    new_text = "DI: {0:.1f}\n{1:s}".format(di[opt], di_map[opt][1])
    setRGB(R[opt], G[opt], B[opt])
    time.sleep(.1)
    if text != new_text:
        print("Θερμοκρασία: {0:s}: {1:5.1f} oC ".format(properties.the_rooms[opt], temp[opt]))
        print("    Υγρασία: {0:s}: {1:5.1f} %RH".format(properties.the_rooms[opt], humi[opt]))
        print("         DI: {0:s}: {1:5.1f} {2:s}".format(properties.the_rooms[opt], di[opt], di_map[opt][1]))
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
