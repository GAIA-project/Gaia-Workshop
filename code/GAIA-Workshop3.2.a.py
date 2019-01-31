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
import gaia_text
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]
button = 8

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
rooms = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]
timestamp = None

# Other global variables
option_idx = 0
option_idx_changed = True
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateSiteData(group, param):
    global timestamp
    resource = sparkworks.groupDeviceResource(group["uuid"], param["uuid"])
    latest = sparkworks.latest(resource["uuid"])
    timestamp = latest["latestTime"]
    value = latest["latest"]
    return round(value, 1)


# Get data from database
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Temperature"))
            humidity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


def threaded_function(sleep):
    i = sleep * 10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep*10
        time.sleep(0.1)
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
    for i in [0, 1, 2]:
        if values[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)
    return max_value


# Close all the leds
def closeLeds():
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def calcHI(t, hum):
    tmp = 1.8 * t + 32
    hy = -42.379 + 2.04901523 * tmp + 10.14333127 * hum - 0.22475541 * tmp * hum - 0.00683783 * tmp * tmp - 0.05481717 * hum * hum + 0.00122874 * tmp * tmp * hum
    hy = hy + 0.00085282 * tmp * hum * hum - 0.00000199 * tmp * tmp * hum * hum
    hy = (hy - 32) * 0.55
    return round(hy, 1)


def setup():
    global sparkworks, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for i in [0, 1, 2]:
        grovepi.pinMode(pin1[i], "OUTPUT")
        grovepi.pinMode(pin2[i], "OUTPUT")
    closeLeds()
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    print("Όνομα χρήστη:\n\t{0:s}\n"
          .format(properties.username))
    print("Επιλεγμένες αίθουσες:")
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    rooms = sparkworks.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}"
              .format(room['name'].encode('utf-8')))
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
    global option_idx, option_idx_changed

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if option_idx_changed:
        option_idx_changed = False

        hi = [0, 0, 0]
        for i in [0, 1, 2]:
            hi[i] = calcHI(temperature[i], humidity[i])
        showMaximum(hi)

        # Print to terminal
        print("Θερμοκρασία: {0:s}: {1:5.1f} oC "
              .format(properties.the_rooms[option_idx], temperature[option_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f} %RH"
              .format(properties.the_rooms[option_idx], humidity[option_idx]))
        print("         HI: {0:s}: {1:5.1f}"
              .format(properties.the_rooms[option_idx], hi[option_idx]))

        # Print to LCD
        lcd_temp = "{0:4.1f}oC".format(temperature[option_idx])
        lcd_hi = "HI:{0:4.1f}".format(hi[option_idx]).rjust(16 - len(lcd_temp))
        lcd_hum = "{0:4.1f}%RH".format(humidity[option_idx])
        new_text = lcd_temp + lcd_hi + lcd_hum
        grovelcd.setRGB(R[option_idx], G[option_idx], B[option_idx])
        grovelcd.setText(new_text)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    option_idx, option_idx_changed = checkButton(button, option_idx, 0, 3)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
