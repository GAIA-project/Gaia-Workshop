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
import gaia_text
import properties
from sparkworks import SparkWorks
import arduino_gauge_i2c as arduino_gauge

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
phases = None
current = [0, 0, 0]
power = [0, 0, 0]
max_power = [0, 0, 0]
timestamp = None

# Other global variables
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateData(resource):
    global timestamp
    summary = sparkworks.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    latest = summary["latest"]
    maximum = max(summary["minutes5"])
    return round(latest, 1), round(maximum, 1)


# Get data from database
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            current[i] = data[0] / 1000
            power[i] = data[0] * 230 / 1000
            max_power[i] = data[1] * 230 / 1000


def threaded_function(sleep):
    i = sleep*10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep*10
        time.sleep(0.1)
        i -= 1


def mapValueToLeds(value, max, leds_available):
    step = max / leds_available
    # num_leds = math.ceil(value/step)
    num_leds = round(value/step)
    return int(num_leds)


def setup():
    global sparkworks, phases, thread
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

    print("Όνομα χρήστη:\n\t{0:s}"
          .format(properties.username))
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    group = sparkworks.group(properties.uuid)
    print("\t{0:s}\n"
          .format(group["name"].encode("utf-8")))
    print("Επιλεγμένοι αισθητήρες:")
    phases = sparkworks.current_phases(properties.uuid)
    for phase in phases:
        print("\t{0:s}"
              .format(phase["systemName"]))
    print("\n")

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaia_text.loading_data)
    getData()
    print("Τελευταία ανανέωση δεδομένων: {0:s}\n"
          .format(datetime.datetime.fromtimestamp((timestamp/1000.0)).strftime('%Y-%m-%d %H:%M:%S')))

    thread = Thread(target=threaded_function, args=(10,))
    thread.start()


def loop():
    open_leds = [0, 0, 0]
    total = sum(power)
    basemax = max(max_power)
    print("Μέγιστη κατανάλωση στις προηγούμενες 4 ώρες: {0:.2f}"
          .format(basemax))

    for i in [0, 1, 2]:
        print("{0:s} Ρεύμα: {1:.2f}A, Κατανάλωση: {2:.2f}W"
              .format(phases[i]['systemName'], current[i], power[i]))
        open_leds[i] = mapValueToLeds(power[i], basemax, 12)
    arduino_gauge.write(*open_leds)

    time.sleep(0.5)
    grovelcd.setRGB(60, 60, 60)
    grovelcd.setText("Total Power:\n{0:>15.2f}W"
                     .format(total))
    time.sleep(10)

    for i in [0, 1, 2]:
        grovelcd.setRGB(R[i], G[i], B[i])
        grovelcd.setText("Phase: {0:d}\n{1:>15.2f}W"
                         .format(i+1, power[i]))
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

