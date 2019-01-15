#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
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
pin1 = [2, 4]
pin2 = [3, 5]
button1 = 8
button2 = 7

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# variables for the sensors
temp = [0, 0, 0]
humi = [0, 0, 0]

time_idx = None
time_idx_changed = False
room_idx = 0
room_idx_changed = False
timestamp = None
exitapp = False
sparkworks = SparkWorks(properties.client_id, properties.client_secret)

# Assign input and output pins
grovepi.pinMode(button1, "INPUT")
grovepi.pinMode(button2, "INPUT")
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")


# Take new values from the database
def updateData(group, param):
    global timestamp
    resource = sparkworks.groupAggResource(group['uuid'], param['uuid'])
    summary = sparkworks.summary(resource['uuid'])
    val = summary["minutes60"]
    timestamp = summary["latestTime"]
    return val


def getSensorData():
    # global temperature, humidity
    if not exitapp:
        for i in[0, 1]:
            temp[i] = updateData(rooms[i], sparkworks.phenomenon("Temperature"))
            humi[i] = updateData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


# Find out the minimum value
def minimum(v):
    min_value = min(v[0], v[1])
    for i in [0, 1]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Close all the leds
def closeAllLeds():
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


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


def calcDI(t, rh):
    DI = t - 0.55 * (1 - 0.01 * rh) * (t - 14.5)
    return float("{0:.1f}".format(float(DI)))


def traverseSubGroups(group):
    _bottom = []
    _subgroups = sparkworks.subGroups(group['uuid'])
    if len(_subgroups) == 0:
        _bottom.append(group)
    else:
        for _subgroup in _subgroups:
            _list = traverseSubGroups(_subgroup)
            for _item in _list:
                _bottom.append(_item)
    return _bottom


def selectRooms(site, local):
    _rooms = []
    for _local in local:
        for _site in site:
            if _site['name'].encode('utf-8').strip() == _local.strip():
                _rooms.append(_site)
    return _rooms


closeAllLeds()
# Print rooms
print("Όνομα χρήστη:\n\t%s\n" % properties.username)
print("Επιλεγμένη αίθουσα:")
for room in properties.the_rooms:
    print('\t%s' % room.decode('utf-8'))
print('\n')

sparkworks.connect(properties.username, properties.password)
site_rooms = traverseSubGroups(sparkworks.group(properties.uuid))
rooms = selectRooms(site_rooms, properties.the_rooms)


def loop():
    global time_idx, room_idx, time_idx_changed, room_idx_changed
    # Detect button used for selecting hours
    try:
        if (grovepi.digitalRead(button1)):
            print("Νέα ώρα")
            setText("New Hour")
            setRGB(50, 50, 50)
            time_idx += 1
            if time_idx >= 48:
                time_idx = None
            time_idx_changed = True
            time.sleep(1)
    except IOError:
        print("Button Error")
    # Detect button used for selecting rooms
    try:
        if (grovepi.digitalRead(button2)):
            print("Νέα αίθουσα")
            setText("New Room")
            setRGB(50, 50, 50)
            room_idx += 1
            if room_idx >= 2:
                room_idx = 0
            room_idx_changed = True
            time.sleep(1)
    except IOError:
        print("Button Error")

    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        setText(gaia_text.loading_data)
        setRGB(50, 50, 50)
        getSensorData()
        time_idx = 0
        time_idx_changed = True

    if time_idx_changed or room_idx_changed:
        room_idx_changed = False
        time_idx_changed = False
        timevalue = datetime.datetime.fromtimestamp((timestamp / 1000.0) - 3600 * (time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        # Calculate DI
        di = [0, 0]
        di_map = [None, None]
        for i in range(2):
            di[i] = calcDI(temp[i][time_idx], humi[i][time_idx])
            di_map[i] = mapDItoGauge(di[i])

        # Print to terminal
        print(" Ημερομηνία: {0:s}".format(strdate))
        print("Θερμοκρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], temp[room_idx][time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], humi[room_idx][time_idx]))
        print("         DI: {0:s}: {1:5.1f} {2:s}".format(properties.the_rooms[room_idx], di[room_idx], di_map[room_idx][1]))

        # Print DI to LCD
        str_di = "DI:{0:.1f}".format(di[room_idx]).rjust(16 - len(strtime))
        str_desc = di_map[room_idx][1].rjust(16)
        new_text = strtime + str_di + str_desc
        setRGB(R[room_idx], G[room_idx], B[room_idx])
        setText(new_text)

        arduino_gauge.write(di_map[0][0], di_map[1][0], 0)
        # Show minimum DI on the Leds
        minimum(di)


def main():
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
