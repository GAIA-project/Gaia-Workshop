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
import arduino_gauge_i2c as arduino_gauge

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
temperature = [0, 0]
humidity = [0, 0]
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
            temperature[i] = updateData(rooms[i], sparkworks.phenomenon("Temperature"))
            humidity[i] = updateData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


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


# Find out the minimum value
def showMinimum(values):
    min_value = min(values)
    for i in [0, 1]:
        if values[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)
    return min_value


# Close all the leds
def closeLeds():
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


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
    global sparkworks, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for i in [0, 1]:
        grovepi.pinMode(pin1[i], "OUTPUT")
        grovepi.pinMode(pin2[i], "OUTPUT")
    closeLeds()
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

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

        # Calculate DI
        di = [0, 0]
        di_map = [None, None]
        for i in [0, 1]:
            di[i] = calcDI(temperature[i][time_idx], humidity[i][time_idx])
            di_map[i] = mapDiToLeds(di[i])
        arduino_gauge.write(di_map[0][0], di_map[1][0], 0)

        # Print to terminal
        print(" Ημερομηνία: {0:s}".format(strdate))
        print("Θερμοκρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], temperature[room_idx][time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}".format(properties.the_rooms[room_idx], humidity[room_idx][time_idx]))
        print("         DI: {0:s}: {1:5.1f} {2:s}".format(properties.the_rooms[room_idx], di[room_idx], di_map[room_idx][1]))

        # Print to LCD
        str_di = "DI:{0:.1f}".format(di[room_idx]).rjust(16 - len(strtime))
        str_desc = di_map[room_idx][1].rjust(16)
        new_text = strtime + str_di + str_desc
        grovelcd.setRGB(R[room_idx], G[room_idx], B[room_idx])
        grovelcd.setText(new_text)

        # Show with red the classroom with minimum DI
        showMinimum(di)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = checkButton(button, time_idx, None, 48)
    room_idx, room_idx_changed = checkButton(button2, room_idx, 0, 2)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
