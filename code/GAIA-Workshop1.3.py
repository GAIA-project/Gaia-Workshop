#!/usr/bin/python
# -*- coding: utf-8 -*-

#import libraries
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
luminosity = [0, 0, 0]
temperature = [0, 0, 0]
humidity = [0, 0, 0]
noise = [0, 0, 0]
swvalue=0

#Select the pins Outputs and inputs 
Button = 8
grovepi.pinMode(Button, "INPUT")
Interruptor = 0
grovepi.pinMode(Interruptor, "INPUT")

for i in [0, 1, 2]:
    grovepi.pinMode(pin1[i], "OUTPUT")
    grovepi.pinMode(pin2[i], "OUTPUT")

#initiliaze global variables
mode=0
show=0
set=0
exitapp = False

#Function that check the button
def checkButton():
	global show,change,set,exitapp, mode, Button
	try:
        	if (grovepi.digitalRead(Button)):
			print "έχετε πιέσει το κουμπί"
			if show==1:
            			show = 0
			if set==5:
				set=0
			elif set==14:
				set=0
			else:
				#print "Set", set
            			set = set + 1
			time.sleep(.3)
    	except IOError:
        	print "Button Error"
#Function that check the switch position	
def checkSwitch():
	global show,mode,change,set,exitapp
    	swvalue = grovepi.analogRead(0)
	#print "SWvalue:",swvalue	
	if swvalue < 500:
       		 if mode == 1:
            		print "Μεταβείτε στη λειτουργία 1"
			set = 0
        		mode = 0
    	else:
        	 if mode == 0:
			print "Μεταβείτε στη λειτουργία 2"
            		set = 0
        		mode = 1
	time.sleep(.3)
	

#Take new values from the data base 
def updateSiteData(site, param):
    resource = sparkworks.siteResource(site, param)
    latest = sparkworks.latest(resource)
    latest_value = float("{0:.1f}".format(float(latest["latest"])))
    return latest_value

#Get data from 
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            luminosity[i] = updateSiteData(rooms[i], "Luminosity")
    for i in [0, 1, 2]:
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], "Relative Humidity")
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], "Temperature")
    for i in [0, 1, 2]:
        if not exitapp:
            noise[i] = updateSiteData(rooms[i], "Noise")
    print "Νέα δεδομένα:"        
    for i in [0, 1, 2]:
        print properties.the_rooms[i],"Υγρασία:",humidity[i],"%RH Φωτεινότητα:",luminosity[i],"θερμοκρασία:",temperature[i],"C θόρυβος:",noise[i],"dB"


def threaded_function(arg):
    global temperature, humidity, noise, luminosity
    while not exitapp:
        getData()
        
print "όνομα χρήστη:\n\t%s\n" % properties.username
print "Επιλεγμένη αίθουσα:"
for room in properties.the_rooms:
    print '\t%s' % room.decode('utf-8')
print '\n'

sparkworks.connect(properties.username, properties.password)
rooms = sparkworks.select_rooms(properties.the_rooms)

print "Συλλογή δεδομένων, παρακαλώ περιμένετε..."
setText(gaia_text.loading_data)
getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()

# initialize the screen
setText(gaia_text.press_to_start)
setRGB(50, 50, 50)
time.sleep(1)

text = ""
new_text = ""

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

#show the humidity
def showHumidity(humidity_value, a, b):
    if 30 < humidity_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)

#show the noise
def showNoise(noise_value, a, b):
    if noise_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)

#close all the leds
closeAllLeds()

def loop():
    global new_text, change, show, set
    if set==0:
	if mode==0:
	    print "Λειτουργία 1: Πατήστε το κουμπί για να ξεκινήσετε"
	    new_text = ("Mode 1: Click the button to follow")
	    setRGB(50, 50, 50)
	    closeAllLeds()
	if mode==1:
	    print"Λειτουργία 2: Πατήστε το κουμπί για να ξεκινήσετε"
	    new_text = ("Mode 2: Click the button to follow")
	    setRGB(50, 50, 50)
	    closeAllLeds()	
    if set == 1:
	show=0 	
	if mode == 0:
	    set = 2
	if mode == 1:
	    set = 7
    if set == 2:
	if (show):
	    for i in [0, 1, 2]:
		showLuminosity(luminosity[i], pin1[i], pin2[i])
	else:
	    closeAllLeds()
	    i=0
	    print ("φωτεινότητα:[μοβ,πορτοκαλί,πράσινο]")
	    print(luminosity)
	    for i in [0, 1, 2]:
		setText("Light:" + str(luminosity[i]))
		setRGB(R[i], G[i], B[i])
		showLuminosity(luminosity[i], pin1[i], pin2[i])
		time.sleep(2)
		    
	    time.sleep(2)
	    new_text = ("LIGHT           " + gaia_text.click_to_continue)
	    setRGB(60, 60, 60)
	    show = 1
    if set == 3:
	if (show):
	    for i in [0, 1, 2]:
		showHumidity(humidity[i], pin1[i], pin2[i])
	else:
	    closeAllLeds()
	    print ("υγρασία:[μοβ,πορτοκαλί,πράσινο]")
	    print(humidity)
	    for i in [0, 1, 2]:
		setText("Humid:" + str(humidity[i]) + " %RH")
		setRGB(R[i], G[i], B[i])
		showHumidity(humidity[i], pin1[i], pin2[i])
		time.sleep(2)
	    new_text = ("HUMIDITY        " + gaia_text.click_to_continue)
	    setRGB(60, 60, 60)
	    show = 1
    if set == 4:
	if (show):
	    for i in [0, 1, 2]:
		showTemperature(temperature[i], pin1[i], pin2[i])
	else:
	    closeAllLeds()
	    print ("θερμοκρασία:[μοβ,πορτοκαλί,πράσινο]")
	    print(temperature)
	    for i in [0, 1, 2]:
		setText("Temp:" + str(temperature[i]) + " Cdeg")
		setRGB(R[i], G[i], B[i])
		showTemperature(temperature[i], pin1[i], pin2[i])
		time.sleep(2)

	    new_text = ("TEMPERATURE     " + gaia_text.click_to_continue)
	    setRGB(60, 60, 60)
	    show = 1
    if set == 5:
	if (show):
	    for i in [0, 1, 2]:
		showNoise(noise[i], pin1[i], pin2[i])
	else:
	    closeAllLeds()
	    print ("θόρυβο:[μοβ,πορτοκαλί,πράσινο]")
	    print(noise)
	    for i in [0, 1, 2]:
		setText("Noise:" + str(noise[i]) + " dB")
		setRGB(R[i], G[i], B[i])
		showNoise(noise[i], pin1[i], pin2[i])
		time.sleep(2)
	    new_text = ("NOISE           " + gaia_text.click_to_continue)
	    setRGB(60, 60, 60)
	    show = 1
    if set == 7:
	# maximum light
	print "μέγιστη φωτεινότητα [μοβ,πορτοκαλί,πράσινο]"
	maximum(luminosity, "Luminosity", " ")
	time.sleep(.1)
    if set == 8:
	# minimum light
	print "ελάχιστο φωτεινότητα [μοβ,πορτοκαλί,πράσινο]"
	minimum(luminosity, "Luminosity", " ")
	time.sleep(.1)
    if set == 9:
	# maximum humidity
	print "μέγιστη υγρασία [μοβ,πορτοκαλί,πράσινο]"
	#maximum(humidity, "Humidity", " %RH")
	time.sleep(.1)
    if set == 10:
	# minimum humidity
	print "ελάχιστο υγρασία [μοβ,πορτοκαλί,πράσινο] %RH"
	minimum(humidity, "Humidity", "%RH")
	time.sleep(.1)
    if set == 11:
	# maximum temperature
	print "μέγιστη θερμοκρασία [μοβ,πορτοκαλί,πράσινο] Cdeg"
	maximum(temperature, "Temp", " Cdeg")
	time.sleep(.1)
    if set == 12:
	# minimum temperature
	print "ελάχιστο θερμοκρασία [μοβ,πορτοκαλί,πράσινο] Cdeg"
	minimum(temperature, "Temp", " Cdeg")
	time.sleep(.1)
    if set == 13:
	# maximum noise
	print "μέγιστη θόρυβο [μοβ,πορτοκαλί,πράσινο] dB"
	maximum(noise, "Noise", " dB")
	time.sleep(.1)
    if set == 14:
	# minimum noise
	print "ελάχιστο Noise [μοβ,πορτοκαλί,πράσινο] dB"
	minimum(noise, "θόρυβο", " dB")
	time.sleep(.1)

def main():
    global text,new_text
	
    while not exitapp:
	checkButton()
	checkSwitch()	
        loop()
        if text != new_text:
            text = new_text
            print "settext", text
            setText(text)

try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
