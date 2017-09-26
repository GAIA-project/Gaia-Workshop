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
    summary = sparkworks.summary(resource)
    global maximum
    val_kwh = summary["minutes60"][10]*230/1000 
    val_max = max(summary["minutes60"])*230/1000  
    return (float("{0:.1f}".format(val_kwh)), float("{0:.1f}".format(val_max)))


def getData():
    global main_site, power_consumption, power
    # get per phase data
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            power_consumption[i] = data[0]
            maximum[i] = data[1]


def threaded_function(arg):
    global power_consumption, power, maximum
    while not exitapp:
        getData()


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(3, 2, 1)

sparkworks.connect(properties.username, properties.password)
main_site = sparkworks.main_site()
phases = sparkworks.current_phases(main_site)


print "\t%s" % phases[0]["uri"]
print "\t%s" % phases[1]["uri"]
print "\t%s" % phases[2]["uri"]
print "Collecting data, please wait..."
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()


def map_value_to_leds(m, val, leds_available):
    if val == 0:
        return 0
    steap = m / leds_available
    mod = val / steap + 1
  #  print "led number:"+str(math.floor(mod))+"Val"+str(val)	
    return math.floor(mod)


def main():
    time.sleep(1)
    led=[0,0,0]	
    while not exitapp:
	
	p=power_consumption[0]+power_consumption[1]+power_consumption[2]
        basemax = max(maximum[0], maximum[1], maximum[2])
        print "Maximum base:" + str(basemax)
        for i in [0, 1, 2]:
        	print phases[i]["uri"], "Current:" + str(power_consumption[i]) 
            	led[i]=	map_value_to_leds(basemax, power_consumption[i], 7)
	    	print led[i]
	arduinoGauge.write(led[0],led[1],led[2])
        time.sleep(0.5)
        setText("Total Power:    " + str(p) + " W")
        setRGB(60, 60, 60)
        time.sleep(10)
        for i in [0, 1, 2]:
            setText("Phase " + str(i + 1) + "         " + str(power_consumption[i]) + " W")
            setRGB(R[i], G[i], B[i])
            time.sleep(5)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
