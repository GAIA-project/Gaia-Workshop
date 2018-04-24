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
import grovepi
from grove_rgb_lcd import *
import arduinoGauge

exitapp = False
power = 0
temperature = 0
humidity = 0
main_site = None
phases = []
total_power = None
total_temp = None
total_humid = None
motion=[0,0,0]

#select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]

R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

setText(gaia_text.loading_data)
setRGB(60, 60, 60)


for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")



def updateData(resource):
    summary = sparkworks.summary(resource)
    #latestTime = time.gmtime(summary["latestTime"] / 1000)
    val = (summary["minutes60"][0])
    return (float("{0:.1f}".format(float(val))))

#Take new values from the data base 
def updateSiteData(site, param):
    
 #   print site, param
    resource = sparkworks.siteResource(site, param)
#    print "resource:",resource	
    summary = sparkworks.summary(resource)
    val = (summary["minutes5"][0])
    return (float("{0:.1f}".format(float(val))))
#def updateSiteData(site, param):
#    resource = sparkworks.siteResourceDevice(site, param)
#    latest = sparkworks.latest(resource)
#    latest_value = float("{0:.1f}".format(float(latest["latest"])))
#    return latest_value



def getData():
    global  total_power, power, temperature, total_humid,total_temp, humidity,motion
    # get total data
    data = updateData(total_power)
    power = data
    data = updateData(total_temp)
    temperature = data
    data = updateData(total_humid)
    humidity = data
    for i in [0, 1, 2]:
#	    print rooms[i]['name']	
            motion[i] = updateSiteData(rooms[i], "Motion")
    print power, temperature, humidity

def threaded_function(arg):
    global  power
    while not exitapp:
        getData()


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(0, 0, 0)

sparkworks.connect(properties.username, properties.password)
main_site = sparkworks.main_site()
total_power = sparkworks.total_power(main_site)
total_temp = sparkworks.total_site(main_site, "Temperature")
total_humid = sparkworks.total_site(main_site, "Relative Humidity")
rooms = sparkworks.select_rooms(properties.the_rooms)
#for room in rooms:
#	print room["name"]


print "\t%s" % total_power["uri"]
print ""
print "\t%s" % total_temp["uri"]
print ""
print "\t%s" % total_humid["uri"]
print ""
print "όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένη αίθουσα:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'


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

def showMotion(motion,a,b):
	if motion==0:
		grovepi.digitalWrite(a, 0)
        	grovepi.digitalWrite(b, 1)
	else:
	        grovepi.digitalWrite(a, 1)
        	grovepi.digitalWrite(b, 0)

def main():
    global temperature,humidity,power,motion	
    time.sleep(1)
    while not exitapp:
	maxPower = 5000000
	maxTemp = 40
	maxHumid = 100
        ledPower=map_value_to_leds(maxPower, power, 8)
        ledTemp=map_value_to_leds(maxTemp, temperature, 8)
        ledHumid=map_value_to_leds(maxHumid, humidity, 8)
        arduinoGauge.write(ledPower,ledTemp,ledHumid)
        time.sleep(0.5)
        print "Total Power:    " + str(power) + " Wh"
        print "Total Temperature avg:    " + str(temperature) + " oC"
        print "Total Humidity avg:    " + str(humidity) + " %RH"
	print "Motion purple:	"+str(motion[0])
	print "Motion orange:	"+str(motion[1])
	print "Motion green:	"+str(motion[2])

	for i in [0, 1, 2]:
        	showMotion(motion[i], pin1[i], pin2[i]);

	#Motion
        time.sleep(5)
try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
