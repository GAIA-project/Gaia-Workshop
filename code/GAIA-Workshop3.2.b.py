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
rooms = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]
timestamp = None

# Other global variables
option_idx = 0
option_idx_changed = True
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
                print("\tΘερμοκρασία: {0:.1f}".format(temperature[i]))
        if not exitapp:
            timestamp, humidity[i] = updateData(api, rooms[i], "Relative Humidity")
            if verbose:
                print("\tΥγρασία: {0:.1f}".format(humidity[i]))


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


def calcDI(t, rh):
    di = t - 0.55 * (1 - 0.01 * rh) * (t - 14.5)
    return round(di, 1)


def mapDiToLeds(di):
    led = 0
    word = " "
    if di < -1.7:
        led = 1
        word = "POLY KRIO"
    if -1.7 < di < 12.9:
        led = 2
        word = "KRIO"
    if 12.9 < di < 14.9:
        led = 3
        word = "DROSIA"
    if 15.0 < di < 19.9:
        led = 4
        word = "KANONIKO"
    if 20.0 < di < 26.4:
        led = 5
        word = "ZESTH"
    if 26.5 < di < 29.9:
        led = 6
        word = "POLY ZESTH"
    if 30.0 < di:
        led = 7
        word = "KAFSONAS"
    return led, word


def setup():
    global api, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

    api, rooms = initData()

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaiapi.loading_data)
    getData()
    gaiapi.printLastUpdate(timestamp)

    thread = Thread(target=threadedFunction, args=(10,))
    thread.start()


def loop():
    global option_idx, option_idx_changed, data_updated

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if option_idx_changed:
        option_idx_changed = False

        di = [{"val": 0, "led": 0, "wrd": ""},
              {"val": 0, "led": 0, "wrd": ""},
              {"val": 0, "led": 0, "wrd": ""}]
        for i in range(len(rooms)):
            di[i]["val"] = calcDI(temperature[i], humidity[i])
            di[i]["led"], di[i]["wrd"] = mapDiToLeds(di[i]["val"])
        arduino_gauge.write(*[d["led"] for d in di])

        # Print to terminal
        gaiapi.printRoom(temperature[option_idx],
                         properties.the_rooms[option_idx],
                         "Θερμοκρασία", "oC")
        gaiapi.printRoom(humidity[option_idx],
                         properties.the_rooms[option_idx],
                         "    Υγρασία", "%RH")
        gaiapi.printRoom(di[option_idx]["val"],
                         properties.the_rooms[option_idx],
                         "         DI", di[option_idx]["wrd"])

        # Print to LCD
        lcd_temp = "{0:4.1f}oC".format(temperature[option_idx])
        lcd_di = "DI:{0:4.1f}".format(di[option_idx]["val"]).rjust(16-len(lcd_temp))
        lcd_hum = "{0:4.1f}%RH".format(humidity[option_idx])
        lcd_di2 = "{0:s}".format(di[option_idx]["wrd"]).rjust(16-len(lcd_hum))
        new_text = lcd_temp + lcd_di + lcd_hum + lcd_di2
        grovelcd.setRGB(*lcd_rgbs[option_idx])
        grovelcd.setText(new_text)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    option_idx, option_idx_changed = gaiapi.checkButton(button, option_idx, 0, len(rooms)-1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
