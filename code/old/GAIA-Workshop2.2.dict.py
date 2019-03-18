#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
from threading import Thread
from collections import OrderedDict
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaia_text
import properties
from sparkworks import SparkWorks

from dbgprint import dbgprint

# Select pins for the leds and buttons
pins = {'A': {'yellow': 2, 'white': 3},
        'B': {'yellow': 4, 'white': 5},
        'C': {'yellow': 6, 'white': 7}}
pins = OrderedDict(sorted(pins.items(), key=lambda k: k[0]))
button = 8

# Colors for the rooms
lcd_colors = [[255, 0, 255],
              [255, 128, 0],
              [0, 255, 0]]

# Variables for the sensors
rooms = None
luminosity = [0, 0, 0]
timestamp = None

# Other global variables
option_idx = 0
option_idx_changed = True
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateSiteData(group, param):
    resource = sparkworks.groupDeviceResource(group['uuid'], param['uuid'])
    latest = sparkworks.latest(resource['uuid'])
    value = latest["latest"]
    return round(value, 1)


# Get data from database
def getData():
    for i in range(len(luminosity)):
        if not exitapp:
            luminosity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Luminosity"))


def threaded_function(sleep):
    i = sleep * 10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep
        time.sleep(.1)
        i -= 1


def checkButton(button, idx, init, limit, step=1):
    idx_changed = False
    try:
        if (grovepi.digitalRead(button)):
            idx += step
            if idx >= limit:
                idx = init
            idx_changed = True
            time.sleep(.5)
    except IOError:
        print("Button Error")
    return idx, idx_changed


# Find out the maximum value
def showMaximum(values):
    max_value = max(values)
    for port in pins.keys():
        if v[pins.keys().index(port)] == max_value:
            grovepi.digitalWrite(pins[port]['yellow'], 0)
            grovepi.digitalWrite(pins[port]['white'], 1)
        else:
            grovepi.digitalWrite(pins[port]['yellow'], 1)
            grovepi.digitalWrite(pins[port]['white'], 0)
    return max_value


# Find out the minimum value
def showMinimum(values):
    min_value = min(values)
    for port in pins.keys():
        if v[pins.keys().index(port)] == min_value:
            grovepi.digitalWrite(pins[port]['yellow'], 0)
            grovepi.digitalWrite(pins[port]['white'], 1)
        else:
            grovepi.digitalWrite(pins[port]['yellow'], 1)
            grovepi.digitalWrite(pins[port]['white'], 0)
    return min_value


# Close all the leds
def closeLeds():
    for port in pins.values():
        grovepi.digitalWrite(port['yellow'], 0)
        grovepi.digitalWrite(port['white'], 0)


# Show luminosity on leds
def showLuminosity(light_value, port):
    for p in pins.values():
        if p == port:
            if (light_value < 200):
                # red LED
                grovepi.digitalWrite(p['yellow'], 0)
                grovepi.digitalWrite(p['white'], 1)
            else:
                # blue LED
                grovepi.digitalWrite(p['yellow'], 1)
                grovepi.digitalWrite(p['white'], 0)
        else:
            grovepi.digitalWrite(p['yellow'], 0)
            grovepi.digitalWrite(p['white'], 0)


def setup():
    global sparkworks, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for i in [0, 1, 2]:
        grovepi.pinMode(pin1[i], "OUTPUT")
        grovepi.pinMode(pin2[i], "OUTPUT")
    closeLeds()
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    print("Όνομα χρήστη:\n\t{0:s}\n".format(properties.username))
    print("Επιλεγμένες αίθουσες:")
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    rooms = sparkworks.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}".format(room['name'].encode('utf-8')))
    print("\n")

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaia_text.loading_data)
    getData()

    thread = Thread(target=threaded_function, args=(10,))
    thread.start()


def loop():
    global option_idx, option_idx_changed

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if option_idx_changed:
        option_idx_changed = False
        if option_idx < 3:
            showLuminosity(luminosity[option_idx], pin1[option_idx], pin2[option_idx])
            print("Φωτεινότητα: {0:s}: {1:5.1f}".format(properties.the_rooms[option_idx], luminosity[option_idx]))
            new_text = "{0:s}:\n{1:>16.1f}".format("Light", luminosity[option_idx])
            grovelcd.setRGB(R[option_idx], G[option_idx], B[option_idx])

        if option_idx == 3:
            # maximum light
            maximum = showMaximum(luminosity)
            print("Μέγιστη  φωτεινότητα\t[μωβ, πορτοκαλί, πράσινο]")
            print("{0:^20.1f}\t{1:s}".format(maximum, str(luminosity)))
            new_text = "Max {0:s}:\n{1:>16.1f}".format("Luminosity", maximum)
            grovelcd.setRGB(60, 60, 60)

        if option_idx == 4:
            # minimum light
            minimum = showMinimum(luminosity)
            print("Ελάχιστη φωτεινότητα\t[μωβ, πορτοκαλί, πράσινο]")
            print("{0:^20.1f}\t{1:s}".format(minimum, str(luminosity)))
            new_text = "Min {0:s}:\n{1:>16.1f}".format("Luminosity", minimum)
            grovelcd.setRGB(60, 60, 60)

        grovelcd.setText(new_text)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    option_idx, option_idx_changed = checkButton(button, option_idx, 0, 5)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise

