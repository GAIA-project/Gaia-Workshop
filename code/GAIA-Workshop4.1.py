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
import grove_rgb_lcd as grovelcd
import gaiapi
import properties
from sparkworks import SparkWorks
import arduino_gauge_i2c as arduino_gauge

# Select pins for the leds and buttons
led_pins = [[2, 3],
            [4, 5],
            [6, 7]]
button = 8

# Colors for the rooms
lcd_rgbs = [[255, 0, 255],
            [255, 128, 0],
            [0, 255, 0]]

# Variables for the sensors
phases = None
current = [None, None, None]
power = [None, None, None]
max_power = [None, None, None]
timestamp = None

# Other global variables
thread = None
data_updated = False
exitapp = False
api = None
verbose = False


# Initialize connection to the database
def initData():
    print("Όνομα χρήστη:\n\t{0:s}".format(properties.username))
    sw = SparkWorks(properties.client_id, properties.client_secret)
    sw.connect(properties.username, properties.password)
    group = sw.group(properties.uuid)
    print("\t{0:s}\n".format(group["name"].encode("utf-8")))

    room, phases = sw.select_power_meters(properties.uuid, properties.lab_room)
    print("Επιλεγμένη αίθουσα:")
    print("\t{0:s}".format(room["name"].encode("utf-8")))
    print("Επιλεγμένοι αισθητήρες:")
    for phase in phases:
        print("\t{0:s}".format(phase["systemName"]))
    print("\n")
    return sw, phases


# Update values from the database
def updateData(sw, resource):
    summary = sw.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    latest = summary["latest"]
    maximum = max(summary["minutes5"])
    return timestamp, round(latest, 1), round(maximum, 1)


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(phases)):
        if verbose:
            print("{0:s}".format(phases[i]["systemName"].encode('utf-8')))
        if not exitapp:
            timestamp, latest, maximum = updateData(api, phases[i])
            current[i] = latest/1000
            power[i] = latest*230/1000
            max_power[i] = maximum*230/1000
            if verbose:
                print("\tΙσχύς: {0:.1f} {1:.1f}".format(power[i], max_power[i]))


def threadedFunction(sleep):
    global data_updated
    i = sleep*10
    while not exitapp:
        if i == 0:
            getData()
            data_updated = True
            i = sleep*10
        time.sleep(0.1)
        i -= 1


def setup():
    global api, phases, thread
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

    api, phases = initData()

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaiapi.loading_data)
    getData()
    gaiapi.printLastUpdate(timestamp)

    thread = Thread(target=threadedFunction, args=(10,))
    thread.start()


def loop():
    open_leds = [0, 0, 0]
    basemax = max(max_power)
    print("Μέγιστη κατανάλωση στις προηγούμενες 4 ώρες: {0:.2f}"
          .format(basemax))

    for i in range(len(phases)):
        gaiapi.printRoom(current[i],
                         "Φάση {0:d}".format(i+1),
                         "Ρεύμα", "A")
        gaiapi.printRoom(power[i],
                         "Φάση {0:d}".format(i+1),
                         "Κατανάλωση", "W")
        open_leds[i] = gaiapi.mapToLeds(power[i], basemax, 12)
    arduino_gauge.write(*open_leds)

    for i in range(len(phases)):
        grovelcd.setRGB(*lcd_rgbs[i])
        grovelcd.setText("Phase: {0:d}\n{1:>15.2f}W".format(i+1, power[i]))
        time.sleep(5)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise

