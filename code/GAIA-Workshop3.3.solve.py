#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
from threading import Thread
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True

import gaia_text
import properties
import sparkworks
import grovepi
from grove_rgb_lcd import *
import arduinoGauge

exitapp = False
timestamp = 0
main_site = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]

# select pins for the leds
pin1 = [2, 4]
pin2 = [3, 5]

# select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""
t = 0
new_t = 0
rm = 0
rmchange = 0
strtime = " "
strdate = " "


Button1 = 8
Button2 = 7
grovepi.pinMode(Button1, "INPUT")
grovepi.pinMode(Button2, "INPUT")
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

# initiliaze the LCD screen color and value
text = gaia_text.loading_data
setText(text)
setRGB(60, 60, 60)


def updateData(site, param):
    global timestamp, maximum
    resource = sparkworks.siteResource(site, param)
    summary = sparkworks.summary(resource)
    val = summary["minutes60"]
    timestamp = summary["latestTime"]
    return (val)


def getSensorData():
    global temperature, humidity
    if not exitapp:
        for i in[0, 1]:
            val = updateData(rooms[i], "Temperature")
            temperature[i] = val
        for i in[0, 1]:
            val = updateData(rooms[i], "Relative Humidity")
            humidity[i] = val


# Find out the minimum value
def minimum(v):
    min_value = min(v[0], v[1])
    for i in [0, 1]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


# Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def mapDItoLED(di):
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


def calDI(t, rh):
    DI = t - 0.55 * (1 - 0.01 * rh) * (t - 14.5)
    return float("{0:.2f}".format(float(DI)))


closeAllLeds()
# Print rooms
print("Όνομα χρήστη:\n\t%s\n" % properties.username)
print("Επιλεγμένη αίθουσα:")
for room in properties.the_rooms:
    print('\t%s' % room.decode('utf-8'))
print('\n')


# total Power
sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)
new_text = "Click button to start!"
setRGB(50, 50, 50)


arduinoGauge.connect()
arduinoGauge.write(1, 1, 1)

def loop():
    global text, new_text, timestamp, t, rm, new_t, strtime, strdate, rmchange
    tem = [0, 0]
    hum = [0, 0]
    # detect Button that choose houre
    try:
        if (grovepi.digitalRead(Button1)):
            print("νέα ώρα")
            setText("New Hour")
            t = t + 1
            if t == 24:
                setText("Take new data")
                t = 0
            time.sleep(1)
    except IOError:
        print("Button Error")
    # Detect the button that choose room
    try:
        if (grovepi.digitalRead(Button2)):
            print("νέα τάξη")
            rmchange = 1
            rm = rm + 1
            if rm >= 2:
                rm = 0
            time.sleep(1)
    except IOError:
        print("Button Error")

    if t == 0:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        getSensorData()
        new_text = "Getting data..."
        setRGB(50, 50, 50)
        t = 1

    else:
        if (new_t != t) or rmchange:
            new_t = t
            rmchange = 0
            timevalue = datetime.datetime.fromtimestamp((timestamp / 1000.0) - 3600 * (t - 1))
            strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
            strtime = timevalue.strftime('%H:%M')

            # Temperature at the time
            # Temperature room Purple
            tem[0] = temperature[0][new_t - 1]
            # Temperature room Orange
            tem[1] = temperature[1][new_t - 1]

            # Humidity at the time
            # Humidity room Purple
            hum[0] = humidity[0][new_t - 1]
            # temperature room Orange
            hum[1] = humidity[1][new_t - 1]

            # Calculate DI
            DI = [0, 0]
            led = [0, 0]
            word = [" ", " ", " "]
            # DI for room Purple
            DI[0] = calDI(tem[0], hum[0])
            # DI for room Orange
            DI[1] = calDI(tem[1], hum[1])

            # Calculate the Number of leds open at Purple room
            val = mapDItoLED(DI[0])
            led[0] = val[0]
            word[0] = val[1]
            # Calculate the number od leds open at Orange room
            val = mapDItoLED(DI[1])
            led[1] = val[0]
            word[1] = val[1]

            # Print to terminal
            print(strdate)
            print(properties.the_rooms[rm] + ": Θερμοκρασία: {0:.1f}".format(tem[rm]))
            print(properties.the_rooms[rm] + ": Ύγρασία: {0:.1f}".format(hum[rm]))
            print(properties.the_rooms[rm] + ": DI: {0:.1f} ".format(DI[rm]) + word[rm])

            # Print DI to LCD
            new_text = strtime + "DI:{0:.1f}".format(DI[rm]).rjust(16 - len(strtime)) + word[rm].rjust(16)
            setRGB(R[rm], G[rm], B[rm])
            setText(new_text)

            arduinoGauge.write(led[0], led[1], 0)
            # Show minimum DI on the Leds
            minimum(DI)


def main():
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
