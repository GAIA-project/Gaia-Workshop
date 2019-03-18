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
import gaiapi
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
led_pins = [[2, 3],
            [4, 5]]
button = 8
button2 = 7

# Colors for the rooms
lcd_rgbs = [[255, 0, 255],
            [255, 128, 0],
            [0, 255, 0]]

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

    print("Επιλεγμένες αίθουσες:")
    rooms = sw.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}".format(room["name"].encode("utf-8")))
    print("\n")
    return sw, rooms


# Update values from the database
def updateData(sw, group, param):
    resource = sw.groupAggResource(group["uuid"], sw.phenomenon(param)["uuid"])
    summary = sw.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    values = summary["minutes60"]
    return timestamp, [round(value, 1) for value in values]


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(led_pins)):
        if verbose:
            print("{0:s}".format(rooms[i]["name"].encode('utf-8')))
        if not exitapp:
            timestamp, luminosity[i] = updateData(api, rooms[i], "Luminosity")
            if verbose:
                print("\tΦωτεινότητα: {0:.1f}".format(luminosity[i]))


def setup():
    global api, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    api, rooms = initData()


def loop():
    global time_idx, room_idx, time_idx_changed, room_idx_changed
    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaiapi.loading_data)
        getData()
        gaiapi.printLastUpdate(timestamp)
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
        gaiapi.printDate(strdate)
        gaiapi.printRoom(luminosity[room_idx][time_idx],
                         properties.the_rooms[room_idx],
                         "Φωτεινότητα")

        # Print to LCD
        new_text = "{0:s}\nLuminosity:{1:>5.1f}".format(strtime, luminosity[room_idx][time_idx])
        grovelcd.setRGB(*lcd_rgbs[room_idx])
        grovelcd.setText(new_text)

        # Show luminosity on the leds for the current room
        gaiapi.closeLeds(led_pins)
        gaiapi.showLuminosity(luminosity[room_idx][time_idx], *led_pins[room_idx])
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = gaiapi.checkButton(button, time_idx, None, 23)
    room_idx, room_idx_changed = gaiapi.checkButton(button2, room_idx, 0, len(led_pins)-1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
