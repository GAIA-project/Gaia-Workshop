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
import arduino_gauge_i2c as arduino_gauge

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
temperature = [0, 0, 0]
humidity = [0, 0, 0]
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
            timestamp, temperature[i] = updateData(api, rooms[i], "Temperature")
            if verbose:
                print("\tΘερμοκρασία: {0:.1f}".format(temperature[i]))
        if not exitapp:
            timestamp, humidity[i] = updateData(api, rooms[i], "Relative Humidity")
            if verbose:
                print("\tΥγρασία: {0:.1f}".format(humidity[i]))


def calcDi(t, rh):
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
    global api, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

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

        # Calculate DI
        di = [{"val": 0, "led": 0, "wrd": ""},
              {"val": 0, "led": 0, "wrd": ""},
              {"val": 0, "led": 0, "wrd": ""}]
        for i in range(len(led_pins)):
            di[i]["val"] = calcDi(temperature[i][time_idx], humidity[i][time_idx])
            di[i]["led"], di[i]["wrd"] = mapDiToLeds(di[i]["val"])
        arduino_gauge.write(*[d["led"] for d in di])

        # Print to terminal
        gaiapi.printDate(strdate)
        gaiapi.printRoom(temperature[room_idx][time_idx],
                         properties.the_rooms[room_idx],
                         "Θερμοκρασία", "oC")
        gaiapi.printRoom(humidity[room_idx][time_idx],
                         properties.the_rooms[room_idx],
                         "    Υγρασία", "%RH")
        gaiapi.printRoom(di[room_idx]["val"],
                         properties.the_rooms[room_idx],
                         "         DI", di[room_idx]["wrd"])

        # Print to LCD
        str_di = "DI:{0:.1f}".format(di[room_idx]["val"]).rjust(16 - len(strtime))
        str_desc = di[room_idx]["wrd"].rjust(16)
        new_text = strtime + str_di + str_desc
        grovelcd.setRGB(*lcd_rgbs[room_idx])
        grovelcd.setText(new_text)

        # Show with red the classroom with minimum DI
        val, idx = gaiapi.showMinimum(led_pins, [d["val"] for d in di[:len(led_pins)]])
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
