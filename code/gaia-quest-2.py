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

import grovepi
from grove_rgb_lcd import *

# from grove_rgb_lcd import setText_norefresh as setText

pin1 = [2, 4, 6]
pin2 = [3, 5, 7]
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

luminosity = [0, 0, 0]
temperature = [0, 0, 0]
humidity = [0, 0, 0]
noise = [0, 0, 0]

exitapp = False


def updateSiteData(site, param):
    resource = sparkworks.siteResource(site, param)
    latest = sparkworks.latest(resource)
    latest_value = float("{0:.1f}".format(latest["latest"]))
    return latest_value


def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            luminosity[i] = updateSiteData(rooms[i], "Luminosity")
    for i in [0, 1, 2]:
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], "Relative Humidity")
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], "Temperature")
    for i in [0, 1, 2]:
        if not exitapp:
            noise[i] = updateSiteData(rooms[i], "Noise")
    for i in [0, 1, 2]:
        print properties.the_rooms[i], humidity[i], luminosity[i], temperature[i], noise[i]


def threaded_function(arg):
    global temperature, humidity, noise, luminosity
    while not exitapp:
        getData()
        # time.sleep(1)


print "Username:\n\t%s\n" % properties.username
print "Selected Rooms:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'

sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)

print "Collecting data, please wait..."
setText(gaia_text.loading_data)
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()

Button = 8
Interruptor = 0

# Motor=6
poten = 0
for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
grovepi.pinMode(pin2[i], "OUTPUT")

grovepi.pinMode(Interruptor, "INPUT")
grovepi.pinMode(Button, "INPUT")

# initialize the screen

print "Press button to start..."
setText(gaia_text.press_to_start)
setRGB(50, 50, 50)
time.sleep(1)

change = 0
set = 0
mode = 0

text = ""
new_text = ""


def maximum(v, sensor, unit):
    global new_text
    max_value = max(v[0], v[1], v[2])
    print max_value, v
    print(gaia_text.max_message % (sensor, max_value, unit))
    new_text = (gaia_text.max_message % (sensor, max_value, unit))
    setRGB(60, 60, 60)
    for i in [0, 1, 2]:
        if v[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


def minimum(v, sensor, unit):
    global pin1, pin2, new_text
    min_value = min(v[0], v[1], v[2])
    print min_value, v
    print(gaia_text.min_message % (sensor, min_value, unit))
    new_text = (gaia_text.min_message % (sensor, min_value, unit))
    setRGB(60, 60, 60)
    for i in [0, 1, 2]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


def closeAllLeds():
    global pin1, pin2
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def showLuminosity(light_value, a, b):
    if (light_value < 200):
        # red LED
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)
    else:
        # blue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)


def showTemperature(temperature_value, a, b):
    if 18 < temperature_value < 25:
        # BLue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        # red led
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


def showHumidity(humidity_value, a, b):
    if 30 < humidity_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


def showNoise(noise_value, a, b):
    if noise_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


closeAllLeds()


def loop():
    global mode, set, new_text
    value = grovepi.analogRead(Interruptor)
    if value < 500:
        if mode == 1:
            set = 0
        mode = 0
        change = 0
    else:
        if mode == 0:
            set = 6
        mode = 1
        change = 0

    try:
        if (grovepi.digitalRead(Button)):
            show = 0
            change = 1
            set = set + 1
            time.sleep(.5)
    except IOError:
        print "Button Error"

    show = 1

    if (change or show):
        if change:
            change = 0
            show = 0
        if set == 1:
            new_text = ("Show Data excercise")
            setRGB(50, 50, 50)
            time.sleep(1)

            if mode == 0:
                new_text = ("Mode1: Press the button to start")
                setRGB(50, 50, 50)
                #time.sleep(1)
                closeAllLeds()
            if mode == 1:
                new_text = ("Mode2: Press the button to start")
                setRGB(50, 50, 50)
                #time.sleep(2)
                set = 7
        # closeAllLeds()
        if set == 2:
            if (show):
                for i in [0, 1, 2]:
                    showLuminosity(luminosity[i], pin1[i], pin2[i])
            else:
                closeAllLeds()
                print(luminosity)
                for i in [0, 1, 2]:
                    setText("Light:" + str(luminosity[i]))
                    setRGB(R[i], G[i], B[i])
                    showLuminosity(luminosity[i], pin1[i], pin2[i])
                    time.sleep(2)

                time.sleep(2)
                new_text = ("LIGHT           " + gaia_text.click_to_continue)
                setRGB(60, 60, 60)
                show = 1
        if set == 3:
            if (show):
                for i in [0, 1, 2]:
                    showHumidity(humidity[i], pin1[i], pin2[i])
            else:
                closeAllLeds()
                print(humidity)
                for i in [0, 1, 2]:
                    setText("Humid:" + str(humidity[i]) + " %RH")
                    setRGB(R[i], G[i], B[i])
                    showHumidity(humidity[i], pin1[i], pin2[i])
                    time.sleep(2)

                new_text = ("HUMIDITY        " + gaia_text.click_to_continue)
                setRGB(60, 60, 60)
                show = 1
        if set == 4:
            if (show):
                for i in [0, 1, 2]:
                    showTemperature(temperature[i], pin1[i], pin2[i])
            else:
                closeAllLeds()
                print(temperature)
                for i in [0, 1, 2]:
                    setText("Temp:" + str(temperature[i]) + " Cdeg")
                    setRGB(R[i], G[i], B[i])
                    showTemperature(temperature[i], pin1[i], pin2[i])
                    time.sleep(2)

                new_text = ("TEMPERATURE     " + gaia_text.click_to_continue)
                setRGB(60, 60, 60)
                show = 1
        if set == 5:
            if (show):
                for i in [0, 1, 2]:
                    showNoise(noise[i], pin1[i], pin2[i])
            else:
                closeAllLeds()
                print(noise)
                for i in [0, 1, 2]:
                    setText("Noise:" + str(noise[i]) + " dB")
                    setRGB(R[i], G[i], B[i])
                    showNoise(noise[i], pin1[i], pin2[i])
                    time.sleep(2)
                new_text = ("NOISE           " + gaia_text.click_to_continue)
                setRGB(60, 60, 60)
                show = 1
        if set == 6:
            set = 0
            new_text = ("Press the button to start!")
            setRGB(60, 60, 60)
        if set == 7:
            # maximum light
            print "Maximum Luminosity", luminosity
            maximum(luminosity, "Luminosity", " ")
            time.sleep(.1)
        if set == 8:
            # minimum light
            print "Minimum Luminosity"
            minimum(luminosity, "Luminosity", " ")
            time.sleep(.1)
        if set == 9:
            # maximum humidity
            print "Maximum Humidity", humidity
            maximum(humidity, "Humidity", " %RH")
            time.sleep(.1)
        if set == 10:
            # minimum humidity
            print "Minimum Humidity", humidity
            minimum(humidity, "Humidity", "%RH")
            time.sleep(.1)
        if set == 11:
            # maximum temperature
            print "Maximum Temperature", temperature
            maximum(temperature, "Temp", " Cdeg")
            time.sleep(.1)
        if set == 12:
            # minimum temperature
            print "Minimum Temperature", temperature
            minimum(temperature, "Temp", " Cdeg")
            time.sleep(.1)
        if set == 13:
            # maximum noise
            print "Maximum Noise", noise
            maximum(noise, "Noise", " dB")
            time.sleep(.1)
        if set == 14:
            # minimum noise
            print "Minimum Noise", noise
            minimum(noise, "Noise", " dB")
            time.sleep(.1)
        if set == 15:
            set = 0
            new_text = ("Press the button to start...")
            setRGB(60, 60, 60)


def main():
    global text,new_text
    while not exitapp:
        loop()
        if text != new_text:
            text = new_text
            print "settext", text
            setText(text)
        # time.sleep(0.5)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
