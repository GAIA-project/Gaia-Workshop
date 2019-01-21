#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaia_text
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
pin1 = [2, 4]
pin2 = [3, 5]
button = 8
button2 = 7

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
rooms = None
luminosity = [0, 0, 0]
timestamp = None

# Other global variables
time_idx = None
time_idx_changed = False
room_idx = 0
room_idx_changed = False
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateData(group, param):
    global timestamp
    resource = sparkworks.groupAggResource(group['uuid'], param['uuid'])
    summary = sparkworks.summary(resource['uuid'])
    values = summary["minutes60"]
    timestamp = summary["latestTime"]
    return values


# Get data from database
def getSensorData():
    for i in [0, 1]:
        if not exitapp:
            luminosity[i] = updateData(rooms[i], sparkworks.phenomenon("Luminosity"))


# Show luminosity on leds
def showLuminosity(light_value, a, b):
    for i in [0, 1]:
        if a == pin1[i] and b == pin2[i]:
            if (light_value < 200):
                # red LED
                grovepi.digitalWrite(a, 0)
                grovepi.digitalWrite(b, 1)
            else:
                # blue LED
                grovepi.digitalWrite(a, 1)
                grovepi.digitalWrite(b, 0)
        else:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 0)


# Close all the leds
def closeLeds():
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def setup():
    global sparkworks, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for i in [0, 1]:
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


def loop():
    global time_idx, room_idx, time_idx_changed, room_idx_changed
    # Detect button used for selecting hours
    try:
        if (grovepi.digitalRead(button)):
            print("Προηγούμενη ώρα")
            grovelcd.setRGB(50, 50, 50)
            grovelcd.setText("Previous Hour")
            time_idx += 1
            if time_idx >= 48:
                time_idx = None
                grovelcd.setText("Starting over...")
            time_idx_changed = True
            time.sleep(.5)
    except IOError:
        print("Button Error")
    # Detect button used for selecting rooms
    try:
        if (grovepi.digitalRead(button2)):
            print("Επόμενη αίθουσα")
            grovelcd.setRGB(50, 50, 50)
            grovelcd.setText("Next Room")
            room_idx += 1
            if room_idx >= 2:
                room_idx = 0
            room_idx_changed = True
            time.sleep(.5)
    except IOError:
        print("Button Error")

    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaia_text.loading_data)
        getSensorData()
        time_idx = 0
        time_idx_changed = True

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if time_idx_changed or room_idx_changed:
        room_idx_changed = False
        time_idx_changed = False

        timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        # Print to terminal
        print(" Ημερομηνία: {0:s}".format(strdate))
        print("Φωτεινότητα: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], luminosity[room_idx][time_idx]))

        # Print to LCD
        new_text = "{0:s}\nLuminosity:{1:>5.1f}".format(strtime, luminosity[room_idx][time_idx])
        grovelcd.setRGB(R[room_idx], G[room_idx], B[room_idx])
        grovelcd.setText(new_text)

        # Show luminosity on the leds for the current room
        showLuminosity(luminosity[room_idx][time_idx], pin1[room_idx], pin2[room_idx])
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
