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
import grovepi
from grove_rgb_lcd import *
import math

import arduinoGauge
import datetime
exitapp = False

set=0
timestamp=0
main_site = None
temperature=[0,0,0]
humidity=[0,0,0]
#Slect how much houres you use for the average
hours=5

#select pins for the leds
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]

#select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""

Button=8

grovepi.pinMode(Button, "INPUT")

for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")



#initiliaze the LCD screen color and value
text=gaia_text.loading_data
setText(text)
setRGB(60, 60, 60)


def updateDataAvg(site,param):
    global timestamp, maximum, average, hours
    resource=sparkworks.siteResource(site,param)	
    summary = sparkworks.summary(resource)
    val = summary["minutes60"]
    #make the averages 	
    i=0
    average=0
    while (i<hours): 
    	average=average+val[i]
	i=i+1
    average=average/hours
    timestamp=summary["latestTime"]
    return float("{0:.2f}".format(float(average)))

def getData():
    global temperature
    if not exitapp:
	for i in[0,1,2]:
		val=updateDataAvg(rooms[i],"Temperature")
		temperature[i]=val
	for i in[0,1,2]:
		val=updateDataAvg(rooms[i],"Relative Humidity")
		humidity[i]=val



def threaded_function(arg):
    global temperature, humidity, noise, luminosity
    while not exitapp:
	checkButton()	


#Function that check the button
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

def breakSleep(the_set):
    global set
    i=0	
    while (i<50):
	i=i+1
        if (the_set!=set):
		continue
	time.sleep(.1)
#Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)
	
closeAllLeds()
#Print rooms
print "όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένη αίθουσα:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'


#total Power
sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)

thread = Thread(target=threaded_function, args=(10,))
thread.start()

def loop():
    global new_text, temperature,humidity,set

    #get data
    print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
    setText(gaia_text.loading_data)
    setRGB(50, 50, 50)
    getData()   

    # minimum temperature
    print "ελάχιστο θερμοκρασία μέσος όρος [μοβ,πορτοκαλί,πράσινο]"
    minimum(temperature, "Temperature", "oC ")
    setText(new_text)
    breakSleep(set)

    for i in [0,1,2]:
        print "θερμοκρασία μέσος όρος :", properties.the_rooms[i],": ",temperature[i], " oC"
        new_text=("Avg Temperature:" + str(temperature[i])+" oC")
        setText(new_text)
        setRGB(R[i], G[i], B[i])
	breakSleep(set)

    # maximum humidity
    print "μέγιστη υγρασία μέσος όρος [μοβ,πορτοκαλί,πράσινο]"
    maximum(humidity, "Humidity", "%RH")
    setText(new_text)
    breakSleep(set)

    for i in [0,1,2]:
        print "υγρασία μέσος όρος:", properties.the_rooms[i], ":",humidity[i], " %RH"
        new_text=("Avg Humidity:   " + str(humidity[i])+" %RH") 
        setText(new_text)
       	setRGB(R[i], G[i], B[i])
        breakSleep(set)
    

def main():	
    while not exitapp:
        loop()

try:
    	main()
except KeyboardInterrupt:
    	exitapp = True
    	raise
