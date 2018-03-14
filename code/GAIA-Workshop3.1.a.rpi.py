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
import threading

#select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]

#select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

#variables for the sensors
humidity = [0, 0, 0]
temperature = [0, 0, 0]

#Select the pins Outputs and inputs 
Button = 8
grovepi.pinMode(Button, "INPUT")

for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

#initiliaze global variables
set=0
exitapp = False

#Take new values from the data base 
def updateSiteData(site, param):
    resource = sparkworks.siteResourceDevice(site, param)
    latest = sparkworks.latest(resource)
    latest_value = float("{0:.1f}".format(float(latest["latest"])))
    return latest_value

#Get data from 
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], "Relative Humidity")
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], "Temperature")


def threaded_function(arg):
    global temperature, humidity
    while not exitapp:
        #getData()
	checkButton()

#check button        
def checkButton():
        global set,exitapp, mode
        try:
                if (grovepi.digitalRead(Button)):
                        print "έχετε πιέσει το κουμπί"
                        if (set==0):
                                set=1
                        else:
                                set=0
                        time.sleep(.5)

        except IOError:
                print "Button Error"

# Find out the maximum value 
def maximum(v, sensor, unit):
    global new_text
    max_value = max(v[0], v[1], v[2])
    print max_value, v
    #print(gaia_text.max_message % (sensor, max_value, unit))
    new_text = (gaia_text.max_message % (sensor, max_value, unit))
    setRGB(60, 60, 60)
    for i in [0, 1, 2]:
        if v[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)

#Find out the minimum value
def minimum(v, sensor, unit):
    global pin1, pin2, new_text
    min_value = min(v[0], v[1], v[2])
    print min_value, v
    #print(gaia_text.min_message % (sensor, min_value, unit))
    new_text = (gaia_text.min_message % (sensor, min_value, unit))
    setRGB(60, 60, 60)
    for i in [0, 1, 2]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)

#Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)

#Sleep that break on click
def breakSleep(the_set):
    global set
    i=0 
    while (i<50):
        i=i+1
        if (the_set!=set):
                continue
        time.sleep(.1)

closeAllLeds()
#Print rooms
print "όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένη αίθουσα:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'

sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)

print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
setText(gaia_text.loading_data)
setRGB(50, 50, 50)

thread = Thread(target=threaded_function, args=(10,))
thread.start()


text = ""
new_text = ""


def loop():
    global new_text,set
    # get data
    print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
    setText(gaia_text.loading_data)
    setRGB(50, 50, 50)
    getData()	
    # minimum temperature
    print "ελάχιστο θερμοκρασία [μοβ,πορτοκαλί,πράσινο]"
    minimum(temperature, "Temperature", "oC ")
    setText(new_text)
    #time.sleep(3)
    breakSleep(set);
    for i in [0,1,2]:
	print "θερμοκρασία:", properties.the_rooms[i],":", temperature[i], " oC"
	new_text=("Temperature:    " + str(temperature[i])+" oC")
	setText(new_text)
	setRGB(R[i], G[i], B[i])
	#time.sleep(3)
	breakSleep(set);

    # maximum humidity
    print "μέγιστη υγρασία [μοβ,πορτοκαλί,πράσινο]"
    maximum(humidity, "Humidity", "%RH")
    setText(new_text)
    #time.sleep(3)
    breakSleep(set);

    for i in [0,1,2]:
	print "υγρασία: ",properties.the_rooms[i],":",humidity[i]," %RH"
	new_text=("Humidity:       " + str(humidity[i])+" %RH")	
	setText(new_text)
	setRGB(R[i], G[i], B[i])
	breakSleep(set);

	#time.sleep(3)
	

def main():
    #close all the leds
    closeAllLeds()
    while not exitapp:
        loop()

try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
