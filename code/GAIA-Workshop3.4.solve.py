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
import forecastio
import gaia_text
import properties
from sparkworks import SparkWorks


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
in_temp = [0, 0, 0]
in_humi = [0, 0, 0]
out_temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
out_humi = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
    if not exitapp:
        for i in [0, 1]:
            in_temp[i] = updateData(rooms[i], sparkworks.phenomenon("Temperature"))
            in_humi[i] = updateData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


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


# Find out maximum value and show
def maximum(v):
    min_value = max(v[0], v[1])
    for i in [0, 1]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


def getOutsideData():
    # Outside weather necessary variables
    api_key = "a96063dd6aacda945d68bb05209e848f"
    current_time = datetime.datetime.now()
    print("forecast.io: " + str(current_time))
    forecast = forecastio.load_forecast(api_key, properties.GPSposition[0], properties.GPSposition[1], time=current_time)

    by_hour = forecast.hourly()
    i = 0
    hour = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for hourly_data in by_hour.data:
        if i < 16:
            hour[15 - i] = hourly_data.time
            out_temp[15 - i] = hourly_data.temperature
            out_humi[15 - i] = hourly_data.humidity * 100
            i += 1


# Close all the leds
def closeAllLeds():
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


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
            if time_idx >= 15:
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
        getOutsideData()
        time_idx = 0
        time_idx_changed = True

    if time_idx_changed or room_idx_changed:
        room_idx_changed = False
        time_idx_changed = False
        timevalue = datetime.datetime.fromtimestamp((timestamp / 1000.0) - 3600 * (time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        temp_diff = [0, 0]
        humi_diff = [0, 0]
        # Calculate the absolute of the different
        for i in range(2):
            temp_diff[i] = abs(in_temp[i][time_idx] - out_temp[time_idx])
            humi_diff[i] = abs(in_humi[i][time_idx] - out_humi[time_idx])

        # Print to terminal
        print(" Ημερομηνία: {0:s}".format(strdate))
        print("Θερμοκρασία: {0:s}: {1:5.1f}".format("Εξωτερική", out_temp[time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}".format("Εξωτερική", out_humi[time_idx]))
        print("Θερμοκρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], in_temp[room_idx][time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], in_humi[room_idx][time_idx]))
        print("Θερμοκρασία: {0:s}: {1:5.1f}".format("Διαφορά", temp_diff[room_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}".format("Διαφορά", humi_diff[room_idx]))

        # Print to LCD
        str_temp_diff = "Temp diff:{0:4.1f}".format(temp_diff[room_idx]).rjust(16)
        str_humi_diff = "Humi diff:{0:4.1f}".format(humi_diff[room_idx]).rjust(16)
        new_text = str_temp_diff + str_humi_diff
        setRGB(R[room_idx], G[room_idx], B[room_idx])
        setText(new_text)

        # Show red the classroom with maximum temperature difference
        maximum(temp_diff)


def main():
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
