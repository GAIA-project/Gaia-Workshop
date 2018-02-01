
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
sensorValues=[0,0,0]

#select pins for the leds
pin1 = [2, 4]
pin2 = [3, 5]

#select colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""

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

def getSensorData(SensorName):
    global sensorValues
    if not exitapp:
	for i in[0,1,2]:
		val=updateData(rooms[i],SensorName)
		sensorValues[i]=val

#Show the luminosity
def showLuminosity(light_value, a, b):
    if (light_value < 200):
        # red LED
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)
    else:
        # blue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)	



print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"


#total Power
sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)


new_text="Click button to start!"


def main():
    	global text, new_text, timestamp, sensorValues	
   	time.sleep(1)
        t=0
	new_t=0
	rm=0
	val=0	
    	while not exitapp:
		#detect Button that choose houre
		try:
        		if (grovepi.digitalRead(Button1)):
		       		setText("New Houre")
				t=t+1
				if t==24:
					setText("Take new data")
					t=0
	           		time.sleep(.5)
				print "houre"+str(t)
    		except IOError:
      			print "Button Error"
		#Detect the button that choose room
		try:
                        if (grovepi.digitalRead(Button2)):
                                #setText("click...")
                                rm=rm+1
                                if rm>=2:
                                        rm=0
                                time.sleep(.5)
                except IOError:
                        print "Button Error"



		if t==0:
			getSensorData("Luminosity")
			new_text="Getting data..."
			t=1

		else:
			if new_t != t:
				new_t=t
				timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(t-1))
				strtime=timevalue.strftime('%Y-%m-%d %H:%M:%S')
				print strtime
 		
			val=sensorValues[rm][new_t-1]
			showLuminosity(val,pin1[rm],pin2[rm])
			new_text= strtime + ": " +  str(float("{0:.2f}".format(val))) 
			setRGB(R[rm], G[rm], B[rm])


		if text != new_text:
            		text = new_text
			print "Luminosity:",properties.the_rooms[rm], val

            		#print "LCD show:", text
       			setText(text)




try:
    	main()
except KeyboardInterrupt:
    	exitapp = True
    	raise
