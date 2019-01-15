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
humidity = [0, 0, 0]
temperature = [0, 0, 0]

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
            humidity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Relative Humidity"))
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Temperature"))


# Find out the maximum value
def maximum(v, phenomenon, unit):
    global new_text
    max_value = max(v[0], v[1], v[2])
    print(max_value, v)
    new_text = "Min {0:s}\n{1:>16s}".format(phenomenon, str(max_value) + unit)
    setText(new_text)
    setRGB(60, 60, 60)
    for i in [0, 1, 2]:
        if v[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Find out the minimum value
def minimum(v, phenomenon, unit):
    global pin1, pin2, new_text
    min_value = min(v[0], v[1], v[2])
    print(min_value, v)
    new_text = "Min {0:s}\n{1:>16s}".format(phenomenon, str(min_value) + unit)
    setText(new_text)
    setRGB(60, 60, 60)
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


# Sleep that break on click
def breakSleep():
    i = 0
    while (i < 50):
        i += 1
        try:
            if (grovepi.digitalRead(button)):
                print("Έχετε πιέσει το κουμπί")
                time.sleep(.5)
                break
        except IOError:
            print("Button Error")
        time.sleep(.1)


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
    global new_text, temperature, humidity

    # get data
    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    setText(gaia_text.loading_data)
    setRGB(50, 50, 50)
    getData()

    # minimum temperature
    print("Ελάχιστη θερμοκρασία [μοβ,πορτοκαλί,πράσινο]")
    minimum(temperature, "Temperature", "oC")
    breakSleep()

    for i in [0, 1, 2]:
        print("Θερμοκρασία: {0:s}: {1:5.1f} oC".format(properties.the_rooms[i], temperature[i]))
        new_text = "{0:s}\n{1:>14.1f}oC".format("Temperature", temperature[i])
        setText(new_text)
        setRGB(R[i], G[i], B[i])
        breakSleep()

    # maximum humidity
    print("Μέγιστη υγρασία [μοβ,πορτοκαλί,πράσινο]")
    maximum(humidity, "Humidity", "%RH")
    breakSleep()

    for i in [0, 1, 2]:
        print("Υγρασία: {0:s}: {1:5.1f} %RH".format(properties.the_rooms[i], humidity[i]))
        new_text = "{0:s}\n{1:>13.1f}%RH".format("Humidity", humidity[i])
        setText(new_text)
        setRGB(R[i], G[i], B[i])
        breakSleep()
        # time.sleep(3)


def main():
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
