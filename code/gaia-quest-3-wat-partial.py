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
max_power = 0
current=[0,0,0]
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
    val = summary["latest"] 
    val_max = max(summary["minutes5"]) 
    return (float("{0:.1f}".format(float(val))), float("{0:.1f}".format(float(val_max))))


def getData():
    global main_site, power_consumption, current
    # get per phase data
    for i in [0, 1, 2]:
        if not exitapp:	
            data = updateData(phases[i])
	    current[i]=data[0]/1000	
            power_consumption[i] = (current[i]*230)
            maximum[i] = data[1]*230/1000


def threaded_function(arg):
    global power_consumption, current, maximum
    while not exitapp:
        getData()


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(1, 2, 3)

sparkworks.connect(properties.username, properties.password)
for room in properties.the_power_room:
	print '\t%s' % room.decode('utf-8')

room = sparkworks.select_rooms(properties.the_power_room)
phases=sparkworks.current_phases(room[0])

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
  #print "led number:"+str(math.floor(mod))+"Val"+str(val)	
    return math.floor(mod)


def main():
    time.sleep(1)
    led=[0,0,0]	
    while not exitapp:
	
	p=power_consumption[0]+power_consumption[1]+power_consumption[2]
        basemax = max(maximum[0], maximum[1], maximum[2])
        print "Maximum base:" + str(basemax)
        for i in [0, 1, 2]:
        	print phases[i]["uri"], " Current: " + str(current[i]) +" Ampere  "+ "Power: "+ str(power_consumption[i]) + " Wat" 
            	led[i]=	map_value_to_leds(basemax, power_consumption[i], 11)
	    	print led[i]
	arduinoGauge.write(led[0],led[1],led[2])
        time.sleep(0.5)
        setText("Total Power:    " + str(p) + "       W")
        setRGB(60, 60, 60)
        time.sleep(10)
        for i in [0, 1, 2]:
            setText("Phase " + str(i + 1) + "         " + str(power_consumption[i]) + "       W")
            setRGB(R[i], G[i], B[i])
            time.sleep(5)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
