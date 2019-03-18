#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
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
rooms = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]
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

    print("Επιλεγμένες αίθουσες:")
    rooms = sw.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}".format(room["name"].encode("utf-8")))
    print("\n")
    return sw, rooms


# Update values from the database
def updateData(sw, group, param):
    resource = sw.groupDeviceResource(group["uuid"], sw.phenomenon(param)["uuid"])
    latest = sw.latest(resource["uuid"])
    timestamp = latest["latestTime"]
    value = latest["latest"]
    return timestamp, round(value, 1)


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(rooms)):
        if verbose:
            print("{0:s}".format(rooms[i]["name"].encode('utf-8')))
        if not exitapp:
            timestamp, temperature[i] = updateData(api, rooms[i], "Temperature")
            if verbose:
                print("\tΘερμοκρασία: {0:.1f}".format(luminosity[i]))
        if not exitapp:
            timestamp, humidity[i] = updateData(api, rooms[i], "Relative Humidity")
            if verbose:
                print("\tΥγρασία: {0:.1f}".format(luminosity[i]))


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
    global api, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    api, rooms = initData()

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaiapi.loading_data)
    getData()
    gaiapi.printLastUpdate(timestamp)

    thread = Thread(target=threadedFunction, args=(10,))
    thread.start()


def loop():
    # minimum temperature
    val, idx = gaiapi.showMinimum(led_pins, temperature[:len(rooms)])
    gaiapi.printRoomsMinMax(temperature, val,
                            "Θερμοκρασία", "Ελάχιστη")
    new_text = "Min {0:s}\n{1:>14.1f}oC".format("Temperature", val)
    grovelcd.setRGB(60, 60, 60)
    grovelcd.setText(new_text)
    gaiapi.breakSleep(button, 5)

    for i in range(len(rooms)):
        gaiapi.printRoom(temperature[i],
                         properties.the_rooms[i],
                         "Θερμοκρασία", "oC")
        new_text = "{0:s}\n{1:>14.1f}oC".format("Temperature", temperature[i])
        grovelcd.setRGB(*lcd_rgbs[i])
        grovelcd.setText(new_text)
        gaiapi.breakSleep(button, 5)

    # maximum humidity
    val, idx = gaiapi.showMaximum(led_pins, humidity[:len(rooms)])
    gaiapi.printRoomsMinMax(humidity, val,
                            "Υγρασία", "Μέγιστη")
    new_text = "Max {0:s}\n{1:>13.1f}%RH".format("Humidity", val)
    grovelcd.setRGB(60, 60, 60)
    grovelcd.setText(new_text)
    gaiapi.breakSleep(button, 5)

    for i in range(len(rooms)):
        gaiapi.printRoom(humidity[i],
                         properties.the_rooms[i],
                         "Υγρασία", "%RH")
        new_text = "{0:s}\n{1:>13.1f}%RH".format("Humidity", humidity[i])
        grovelcd.setRGB(*lcd_rgbs[i])
        grovelcd.setText(new_text)
        gaiapi.breakSleep(button, 5)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
