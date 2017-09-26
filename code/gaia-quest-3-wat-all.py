\
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

exitapp = False
max_power = 0
current=[0,0,0]
current_part=[0,0,0]
power_consumption = [0, 0, 0]
power_consumption_part = [0, 0, 0]
maximum = [0, 0, 0, 0]
maximum_part = [0, 0, 0, 0]
dev=0
ph=0


main_site = None
phases = []
phases_part = []
total_power = None

R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

text = ""
new_text = ""

ButtonDev=8
ButtonPh=7
grovepi.pinMode(ButtonDev, "INPUT")
grovepi.pinMode(ButtonPh, "INPUT")

text=gaia_text.loading_data
setText(text)

setRGB(60, 60, 60)


def updateData(resource):
    summary = sparkworks.summary(resource)
    global maximum
    val = summary["latest"] 
    val_max = max(summary["minutes5"]) 
    return (float("{0:.1f}".format(val)), float("{0:.1f}".format(val_max)))


def getData():
    global main_site, power_consumption, current, current_part, power_consumption_part
    # get per phase data
    for i in [0, 1, 2]:
        if not exitapp:	
	    #Totoal Power	
            data = updateData(phases[i])
	    current[i]=data[0]/1000	
            power_consumption[i] = (current[i]*230)
            maximum[i] = data[1]*230/1000
            #partial Power
	    data = updateData(phases_part[i])
	    current_part[i]=data[0]/1000	
            power_consumption_part[i] = (current_part[i]*230)
            maximum_part[i] = data[1]*230/1000


def threaded_function(arg):
    global power_consumption, current, maximum, current_part, power_consumption_part, maximum_part
    while not exitapp:
        getData()


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(1, 2, 3)

sparkworks.connect(properties.username, properties.password)
for room in properties.the_power_room:
	print '\t%s' % room.decode('utf-8')


#partial power
room = sparkworks.select_rooms(properties.the_power_room)
phases_part=sparkworks.current_phases(room[0])

print "\t%s" % phases_part[0]["uri"]
print "\t%s" % phases_part[1]["uri"]
print "\t%s" % phases_part[2]["uri"]
print "Collecting data, please wait..."

#total Power
sparkworks.connect(properties.username, properties.password)
main_site = sparkworks.main_site()
phases = sparkworks.current_phases(main_site)


print "\t%s" % phases[0]["uri"]
print "\t%s" % phases[1]["uri"]
print "\t%s" % phases[2]["uri"]


getData()

thread = Thread(target=threaded_function, args=(10,))
thread.start()
new_text="Click button to start!"

def map_value_to_leds(m, val, leds_available):
	if val == 0:
        	return 0
    	steap = m / leds_available
    	mod = val / steap + 1
  	#print "led number:"+str(math.floor(mod))+"Val"+str(val)	
    	return math.floor(mod)


def main():
    	global text, new_text,dev, ph	
   	time.sleep(1)
    	led=[0,0,0]
   	led_part=[0,0,0]
    	while not exitapp:
		print "Dev"+str(dev)
		print "ph:"+str(ph)
		#detect Button that choose device
		try:
        		if (grovepi.digitalRead(ButtonDev)):
				if dev==1:
		       			setText("School...")
					dev=0
				else:
					setText("Floor...")
					dev=1
				print "Dev" + str(dev)
	           		time.sleep(.5)
    		except IOError:
      			print "Button Error"
		#detect button that choose phase
		try:
        		if (grovepi.digitalRead(ButtonPh)):
	       			setText("click...")

				ph=ph+1
				if ph>=4:
					ph=0
				print "Ph"+ str(ph)
          			time.sleep(.5)
   		except IOError:
        		print "Button Error"

	
		#Show Total Power (dev=0)	
		if dev==0:
			p=power_consumption[0]+power_consumption[1]+power_consumption[2]
        		basemax = max(maximum[0], maximum[1], maximum[2])
			for i in [0, 1, 2]:
            			led[i]=	map_value_to_leds(basemax, power_consumption[i], 11)

			arduinoGauge.write(led[0],led[1],led[2])
        		if ph==0:
				new_text="School P   TOTAL:" + str(p) + "      W"
        			setRGB(60, 60, 60)
			else:
            			new_text="School P    Ph" + str(ph) +":"+ str(power_consumption[ph-1]) + "        W"
            			setRGB(R[ph-1], G[ph-1], B[ph-1])


		if dev==1:
			p_part=power_consumption_part[0]+power_consumption_part[1]+power_consumption_part[2]
        		basemax = max(maximum_part[0], maximum_part[1], maximum_part[2])
        		for i in [0, 1, 2]:
            			led_part[i]=	map_value_to_leds(basemax, power_consumption_part[i], 11)
			arduinoGauge.write(led_part[0],led_part[1],led_part[2])
			if ph==0: 
        			new_text="Floor P      TOTAL" + str(p_part) + "       W"
        			setRGB(60, 60, 60)

            		else:
				new_text="Floor P     Ph" + str(ph) +":"+ str(power_consumption_part[ph-1]) + "        W"
            			setRGB(R[ph-1], G[ph-1], B[ph-1])

		if text != new_text:
            		text = new_text
            		print "LCD show:", text
       			setText(text)




try:
    	main()
except KeyboardInterrupt:
    	exitapp = True
    	raise
