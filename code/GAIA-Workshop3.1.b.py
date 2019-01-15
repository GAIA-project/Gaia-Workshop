#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
from copy import deepcopy
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

timestamp = 0
main_site = None
humidity = [0, 0, 0]
temperature = [0, 0, 0]
# Hours to average
hours = 5

text = ""
new_text = ""
exitapp = False
sparkworks = SparkWorks(properties.client_id, properties.client_secret)

# Select the pins Outputs and inputs
grovepi.pinMode(button, "INPUT")
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")


# initiliaze the LCD screen color and value
text = gaia_text.loading_data
setText(text)
setRGB(60, 60, 60)


def updateDataAvg(group, param):
    global timestamp, maximum, average, hours
    resource = sparkworks.groupAggResource(group['uuid'], param['uuid'])
    summary = sparkworks.summary(resource['uuid'])
    val = summary["minutes60"]
    # make the averages
    i = 0
    average = 0
    while (i < hours):
        average = average + val[i]
        i = i + 1
    average = average / hours
    timestamp = summary["latestTime"]
    return float("{0:.1f}".format(float(average)))


def getData():
    if not exitapp:
        for i in[0, 1, 2]:
            val = updateDataAvg(rooms[i], sparkworks.phenomenon("Temperature"))
            temperature[i] = val
        for i in[0, 1, 2]:
            val = updateDataAvg(rooms[i], sparkworks.phenomenon("Relative Humidity"))
            humidity[i] = val


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
    global pin1, pin2
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
        print("Μέσος όρος θερμοκρασίας: {0:s}: {1:5.1f} oC".format(properties.the_rooms[i], temperature[i]))
        new_text = "{0:s}\n{1:>14.1f}oC".format("Avg Temperature", temperature[i])
        setText(new_text)
        setRGB(R[i], G[i], B[i])
        breakSleep()

    # maximum humidity
    print("Μέγιστη υγρασία [μοβ,πορτοκαλί,πράσινο]")
    maximum(humidity, "Humidity", "%RH")
    breakSleep()

    for i in [0, 1, 2]:
        print("Μέσος όρος υγρασίας: {0:s}: {1:5.1f} %RH".format(properties.the_rooms[i], humidity[i]))
        new_text = "{0:s}\n{1:>13.1f}%RH".format("Avg Humidity", humidity[i])
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
