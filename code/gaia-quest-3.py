#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())

from threading import Thread
import time

import gaia_text
import properties
import sparkworks

from grove_rgb_lcd import *
import math

import arduinoGauge

exitapp = False
power = 0
max_power = 0
power_consumption = [0, 0, 0]
maximum = [0, 0, 0, 0]
main_site = None
phases = []
total_power = None

R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

setText(gaia_text.loading_data)
setRGB(60, 60, 60)


def updateData(resource):
    global maximum
    summary = sparkworks.summary(resource)
    val_kwh = summary["minutes5"][0] / 1000
    val_max = max(summary["minutes5"]) / 1000
    return (float("{0:.1f}".format(val_kwh)), float("{0:.1f}".format(val_max)))


def getData():
    global main_site, power_consumption, power
    # get per phase data
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            power_consumption[i] = data[0]
            maximum[i] = data[1]
    # get total data
    data = updateData(total_power)
    power = data[0]
    print power, power_consumption


def threaded_function(arg):
    global power_consumption, power, maximum
    while not exitapp:
        getData()


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(0, 0, 0)

sparkworks.connect(properties.username, properties.password)
main_site = sparkworks.main_site()
phases = sparkworks.power_phases(main_site)
total_power = sparkworks.total_power(main_site)

print "\t%s" % phases[0]["uri"]
print "\t%s" % phases[1]["uri"]
print "\t%s" % phases[2]["uri"]
print ""
print "\t%s" % total_power["uri"]
print ""

print "Collecting data, please wait..."
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()


def map_value_to_leds(m, val, leds_available):
    if val == 0:
        return 0
    steap = m / leds_available
    mod = val / steap + 1
    return math.floor(mod)


def main():
    time.sleep(1)

    while not exitapp:

        basemax = max(maximum[0], maximum[1], maximum[2])
        print "Maximum base:" + str(basemax)
        for i in [0, 1, 2]:
            print phases[i]["uri"], power_consumption[i], map_value_to_leds(basemax, power_consumption[i], 7)
        arduinoGauge.write(map_value_to_leds(basemax, power_consumption[0], 7),
                           map_value_to_leds(basemax, power_consumption[1], 7),
                           map_value_to_leds(basemax, power_consumption[2], 7))
        time.sleep(0.5)
        setText("Total Power:    " + str(power) + " Wh")
        setRGB(60, 60, 60)
        time.sleep(10)
        for i in [0, 1, 2]:
            setText("Phase " + str(i + 1) + "         " + str(power_consumption[i]) + " Wh")
            setRGB(R[i], G[i], B[i])
            time.sleep(5)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
