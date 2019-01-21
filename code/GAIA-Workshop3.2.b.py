#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
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
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Temperature"))
            humidity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


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


# Close all the leds
def closeLeds():
    for i in [0, 1, 2]:
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
    global sparkworks, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for i in [0, 1, 2]:
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

        di = [0, 0, 0]
        di_map = [None, None, None]
        for i in [0, 1, 2]:
            di[i] = calcDI(temperature[i], humidity[i])
            di_map[i] = mapDiToLeds(di[i])
        arduino_gauge.write(di_map[0][0], di_map[1][0], di_map[2][0])

        # Print to terminal
        print("Θερμοκρασία: {0:s}: {1:5.1f} oC ".format(properties.the_rooms[option_idx], temperature[option_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f} %RH".format(properties.the_rooms[option_idx], humidity[option_idx]))
        print("         DI: {0:s}: {1:5.1f} {2:s}".format(properties.the_rooms[option_idx], di[option_idx], di_map[option_idx][1]))

        # Print to LCD
        lcd_temp = "{0:4.1f}oC".format(temperature[option_idx])
        lcd_di = "DI:{0:4.1f}".format(di[option_idx]).rjust(16-len(lcd_temp))
        lcd_hum = "{0:4.1f}%RH".format(humidity[option_idx])
        lcd_di2 = "{0:s}".format(di_map[option_idx][1]).rjust(16-len(lcd_hum))
        new_text = lcd_temp + lcd_di + lcd_hum + lcd_di2
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
