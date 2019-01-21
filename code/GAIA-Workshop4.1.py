#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
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

# Other global variables
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateData(resource):
    summary = sparkworks.summary(resource['uuid'])
    latest = summary["latest"]
    maximum = max(summary["minutes5"])
    return (round(latest, 1), round(maximum, 1))


# Get data from database
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            current[i] = data[0] / 1000
            power[i] = data[0] * 230 / 1000
            max_power[i] = data[1] * 230 / 1000


def threaded_function(sleep):
    i = sleep * 10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep
        time.sleep(.1)
        i -= 1


def map_value_to_leds(value, max, leds_available):
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

    print("Όνομα χρήστη:\n\t{0:s}\n".format(properties.username))
    print("Επιλεγμένοι αισθητήρες:")
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    phases = sparkworks.current_phases(properties.uuid)
    for phase in phases:
        print("\t{0:s}".format(phase['systemName']))
    print("\n")

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaia_text.loading_data)
    getData()

    thread = Thread(target=threaded_function, args=(10,))
    thread.start()


def loop():
    open_leds = [0, 0, 0]
    basemax = max(max_power)
    print("Μέγιστη κατανάλωση στις προηγούμενες 4 ώρες: " + str(basemax))

    msg = "{0:s} Ρεύμα: {1:.2f}A, Κατανάλωση: {2:.2f}W"
    for i in [0, 1, 2]:
        print(msg.format(phases[i]['systemName'], current[i], power[i]))
        open_leds[i] = map_value_to_leds(power[i], basemax, 12)
    arduino_gauge.write(*open_leds)

    for i in [0, 1, 2]:
        grovelcd.setRGB(R[i], G[i], B[i])
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
