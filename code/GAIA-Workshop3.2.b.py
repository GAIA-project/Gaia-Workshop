#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
import time
from threading import Thread
import gaia_text
import properties
import sparkworks
import arduino_gauge_serial as arduino_gauge

import grovepi
from grove_rgb_lcd import *
import threading
import math

# select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# variables for the sensors
humidity = [0, 0, 0]
temperature = [0, 0, 0]

# Select the pins Outputs and inputs
Button = 8
grovepi.pinMode(Button, "INPUT")

for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

# initiliaze global variables
set = 0
exitapp = False
var = 0

# Take new values from the data base
def updateSiteData(site, param):
    resource = sparkworks.siteResourceDevice(site, param)
    latest = sparkworks.latest(resource)
    latest_value = float("{0:.1f}".format(float(latest["latest"])))
    return latest_value


# Get data from
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], "Relative Humidity")
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], "Temperature")


def threaded_function(arg):
    global var
    while not exitapp:
        var=1
        getData()
        time.sleep(2)
        var=0
#       print ("Finish get data")
        time.sleep(10)


def threaded_function2(arg):
    while not exitapp:
        checkButton()


def mapDItoLED(di):
    led = 0
    word = " "
    if di < -1.7:
        led = 1
        word = "POLY KPIO"
    if -1.7 < di < 12.9:
        led = 2
        word = "KPIO"
    if 12.9 < di < 14.9:
        led = 3
        word = "DPOSIA"
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


# Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


# Function that check the button
def checkButton():
    global set, exitapp, mode
    try:
        if (grovepi.digitalRead(Button)):
            print("έχετε πιέσει το κουμπί")
            if (set < 2):
                set = set + 1
            else:
                set = 0
            time.sleep(.5)

    except IOError:
        print("Button Error")


def calDI(t, rh):
    DI = t - 0.55 * (1 - 0.01 * rh) * (t - 14.5)
    return float("{0:.2f}".format(float(DI)))


print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
setText(gaia_text.loading_data)
setRGB(50, 50, 50)
arduino_gauge.connect()
arduino_gauge.write(1, 1, 1)

print("όνομα χρήστη:\n\t%s\n" % properties.username)
print("Επιλεγμένη αίθουσα:")
for room in properties.the_rooms:
    print('\t%s' % room.decode('utf-8'))
print('\n')


sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()
thread2 = Thread(target=threaded_function2, args=(10,))
thread2.start()


text = ""
new_text = ""


def loop():
    global new_text, change, show, set, text, var
    DI = [0, 0, 0]
    led = [0, 0, 0]
    word = [" ", " ", " "]
    for i in [0, 1, 2]:
        DI[i] = calDI(temperature[i], humidity[i])
        m = mapDItoLED(DI[i])
        led[i] = m[0]
        word[i] = m[1]
    if var==0:	
        arduino_gauge.write(led[0], led[1], led[2])
    new_text = ("DI: " + str(DI[set]) + "\n" + word[set])
    setRGB(R[set], G[set], B[set])
    time.sleep(.1)
    if text != new_text:
        print(properties.the_rooms[set] + " θερμοκρασία: " + str(temperature[set]) + " Centrigrade")
        print(properties.the_rooms[set] + " υγρασία: " + str(humidity[set]) + " %RH")
        print(properties.the_rooms[set] + " DI: " + str(DI[set]) + " " + word[set])
        text = new_text
        setText(text)


def main():
    global new_text, text, set
    while not exitapp:
        # checkButton()
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
