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

import forecastio


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
outTmp=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
outHum=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

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
#Find out the minimum value
def minimum(v):
    min_value = min(v[0], v[1])
    #print min_value, v
    for i in [0, 1]:
        if v[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)


def getOutsideData():
	global outTem,outHum
	#Outside weather necessary variables
	api_key = "a96063dd6aacda945d68bb05209e848f"
	current_time = datetime.datetime.now()
	print "time:", current_time
	forecast = forecastio.load_forecast(api_key, properties.GPSposition[0], properties.GPSposition[1], time=current_time)

	byHour = forecast.hourly()
	i=0
	houre=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	for hourlyData in byHour.data:
        	if i<16:
                	houre[15-i]=hourlyData.time
                	outTmp[15-i]=hourlyData.temperature
                	outHum[15-i]=hourlyData.humidity*100
                	i=i+1
	


#Close all the leds
def closeAllLeds():
    global pin1, pin2
    for i in [0, 1]:
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
new_text="Click button to start!"
setRGB(50,50,50)



def loop():
    	global text, new_text, timestamp,t, rm, new_t, strtime,strdate,outTem,outHum
        v=[0,0]
	#detect Button that choose houre
        try:
                if (grovepi.digitalRead(Button1)):
                        print "Νέα ώρα"
                        setText("New Houre")
                        t=t+1
                        if t==15:
                                setText("Take new data")
                                t=0
                        time.sleep(1)
        except IOError:
                print "Button Error"
        #Detect the button that choose room
        try:
                if (grovepi.digitalRead(Button2)):
                        print  "Νέα τάξηy"
                        rm=rm+1
                        if rm>=2:
                                rm=0
                        time.sleep(1)
        except IOError:
                print "Button Error"


	if t==0:
		print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
		getSensorData()
		getOutsideData()
		new_text="Getting data..."
		setRGB(50, 50, 50)		
		t=1

	else:
		if new_t != t:
			new_t=t
			timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(t-1))
			strdate=timevalue.strftime('%Y-%m-%d %H:%M:%S')
			strtime=timevalue.strftime('%H:%M:%S')
			#print strdate
			v[0]=temperature[0][new_t-1]
                	v[1]=temperature[1][new_t-1]
                	minimum(v)
			print strdate
			print "εξωτερική θερμοκρασία:", outTmp[new_t-1]
			print "εξωτερική υγρασία:",outHum[new_t-1]


		new_text= "Ti:" +  str("{0:.2f}".format(temperature[rm][new_t-1])) +"To:"+str(outTmp[new_t-1])+"Hi:" +str("{0:.2f}".format(humidity[rm][new_t-1]))+"Ho:"+str(outHum[new_t-1])
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
