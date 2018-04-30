#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())
import time
import properties
import sparkworks
import grovepi
import math
import arduinoGauge
import datetime
from threading import Thread
import gaia_text
from grove_rgb_lcd import *

exitapp = False
button = 8

pin1 = [2, 4, 6]
for i in range(len(pin1)):
    grovepi.pinMode(pin1[i], "OUTPUT")
pin2 = [3, 5, 7]
for i in range(len(pin2)):
    grovepi.pinMode(pin2[i], "OUTPUT")

arduinoGauge.connect()
arduinoGauge.write(1, 2, 3)

setRGB(60, 60, 60)
setText(gaia_text.loading_data)

school_idx = 0
school_data = []
for i in range(len(properties.school)):
    school_data.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False])


def updateData(resource):
    summary = sparkworks.summary(resource)
    value = summary["minutes60"][1]
    return float("{0:.1f}".format(float(value)))


def updateSiteData(site, param):
    resource = sparkworks.siteResource(site, param)
    summary = sparkworks.summary(resource)
    value = summary["minutes5"][0]
    return float("{0:.1f}".format(float(value)))


def getData(idx):
    sparkworks.connect(properties.school[idx]['username'], properties.school[idx]['password'])
    main_site = sparkworks.main_site()

    total_power = sparkworks.total_power(main_site)
    power = updateData(total_power)

    total_temp = sparkworks.total_site(main_site, "Temperature")
    temp = updateData(total_temp)

    total_humid = sparkworks.total_site(main_site, "Relative Humidity")
    humid = updateData(total_humid)

    the_rooms = [ properties.school[idx]['purple'],
                  properties.school[idx]['orange'],
                  properties.school[idx]['green'] ]
    rooms = sparkworks.select_rooms(the_rooms)
    motion = [0, 0, 0]
    for i in range(len(rooms)):
        motion[i] = updateSiteData(rooms[i], "Motion")

    return [power, temp, humid, motion[0], motion[1], motion[2], True]


def getDataThread():
    global exitapp, school_data
    while not exitapp:
        for idx in range(len(properties.school)):
            school_data[idx] = getData(idx)
            time.sleep(10)


for idx in range(len(properties.school)):
    school_data[idx] = getData(idx)


thread = Thread(target = getDataThread, args = ())
thread.start()


def mapValueToLeds(maximum, value, num_leds):
    if value == 0:
        return(0)
    steap = maximum / num_leds
    mod = value / steap + 1
    return int(math.floor(mod))


def showMotion(motion, a, b):
    if motion == 0:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)
    else:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)


def main():
    global exitapp, school_idx, school_data
    power_max = 10000000
    temp_max = 40
    humid_max = 100
    idx_changed = True
    while not exitapp:

        if idx_changed:
            setText(properties.school[school_idx]['name'])

        if idx_changed or school_data[school_idx][6]:
            print "School Index:" + str(school_idx)
            print properties.school[school_idx]['name']
            for i in range(len(school_data[school_idx])):
                print school_data[school_idx][i]
            power_led = mapValueToLeds(power_max, school_data[school_idx][0], 8)
            temp_led  = mapValueToLeds(temp_max,  school_data[school_idx][1], 8)
            humid_led = mapValueToLeds(humid_max, school_data[school_idx][2], 8)
            arduinoGauge.write(power_led, temp_led, humid_led)
            for i in range(3):
                showMotion(school_data[school_idx][i+3], pin1[i], pin2[i])
            school_data[school_idx][6] = False

        try:
            if grovepi.digitalRead(button):
                idx_changed = True
                school_idx = school_idx + 1
                if school_idx >= len(properties.school):
                    school_idx = 0
                time.sleep(.5)
            else:
                idx_changed = False
        except IOError:
            print("Button error")


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
