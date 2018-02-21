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
timestamp=0
main_site = None
temperature=[0,0,0]
humidity=[0,0,0]

#select pins for the leds
pin1 = [2, 4]
pin2 = [3, 5]

#select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""
t=0
new_t=0
rm=0
strtime=" "
strdate=" "


Button1=8
Button2=7
grovepi.pinMode(Button1, "INPUT")
grovepi.pinMode(Button2, "INPUT")
for i in [0, 1]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")



#initiliaze the LCD screen color and value
text=gaia_text.loading_data
setText(text)
setRGB(60, 60, 60)


def updateData(site,param):
    global timestamp, maximum
    resource=sparkworks.siteResource(site,param)	
    summary = sparkworks.summary(resource)
    val = summary["minutes60"]
    #print val
    timestamp=summary["latestTime"]
    return (val)

def getSensorData():
    global temperature, humidity
    if not exitapp:
	for i in[0,1,2]:
		val=updateData(rooms[i],"Temperature")
		temperature[i]=val
	for i in[0,1,2]:
		val=updateData(rooms[i],"Relative Humidity")
		humidity[i]=val

#Show the  temperature
def showTemperature(temperature_value, a, b):
    if 18 < temperature_value < 25:
        # BLue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        # red led
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


#Print rooms
print "όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένη αίθουσα:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'


#total Power
sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)
new_text="Click button to start!"




def loop():
    	global text, new_text, timestamp,t, rm, new_t, strtime,strdate
        #detect Button that choose houre
        try:
                if (grovepi.digitalRead(Button1)):
                        print "on click1"
                        setText("New Houre")
                        t=t+1
                        if t==24:
                                setText("Take new data")
                                t=0
                        time.sleep(1)
        except IOError:
                print "Button Error"
        #Detect the button that choose room
        try:
                if (grovepi.digitalRead(Button2)):
                        print  "on click 2"
                        rm=rm+1
                        if rm>=2:
                                rm=0
                        time.sleep(1)
        except IOError:
                print "Button Error"


	if t==0:
		print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
		getSensorData()
		new_text="Getting data..."
		setRGB(50, 50, 50)
		t=1

	else:
		if new_t != t:
			new_t=t
			timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(t-1))
			strdate=timevalue.strftime('%Y-%m-%d %H:%M:%S')
			strtime=timevalue.strftime('%H:%M:%S')
			print strdate

		showTemperature(temperature[rm][new_t-1],pin1[rm],pin2[rm])
		new_text= strtime + " T:" +  str("{0:.2f}".format(temperature[rm][new_t-1])) +"oC; H:" +str("{0:.2f}".format(humidity[rm][new_t-1]))+" %RH"
		setRGB(R[rm], G[rm], B[rm])


	if text != new_text:
		text = new_text
		print "θερμοκρασία:",properties.the_rooms[rm], "{0:.2f}".format(temperature[rm][new_t-1])
		print "υγρασία:",properties.the_rooms[rm],"{0:.2f}".format(humidity[rm][new_t-1])
		setText(text)


def main():     
    while not exitapp:
        loop()

try:
    	main()
except KeyboardInterrupt:
    	exitapp = True
    	raise
