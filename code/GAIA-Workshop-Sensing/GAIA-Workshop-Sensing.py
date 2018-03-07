#!/usr/bin/env python
#
# GrovePi Example for using the Grove - Temperature&Humidity Sensor (HDC1000)(http://www.seeedstudio.com/depot/Grove-TemperatureHumidity-Sensor-HDC1000-p-2535.html)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#
# This example is derived from the HDC1000 example by control everyhing here: https://github.com/ControlEverythingCommunity/HDC1000/blob/master/Python/HDC1000.py
## License

from grove_i2c_temp_hum_hdc1000 import HDC1000
import time
import light
import datetime
import grovepi
from grove_rgb_lcd import *
from threading import Thread


hdc = HDC1000()
hdc.Config()
timevalue=" "
tempvalue=0
humvalue=0
lightvalue=0
exitapp = False
click=0
start=0
stop=0
click2=0
Button=8
Button2=7

grovepi.pinMode(Button, "INPUT")
grovepi.pinMode(Button2, "INPUT")
def getSensorValues():
	global timevalue,tempvalue,lightvalue,humvalue
	f = open("SensoValues.txt", "a")
	timevalue= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	time.sleep(2)	
	lightvalue=light.readVisibleLux()
	time.sleep(1)
	tempvalue=hdc.Temperature()
	humvalue=hdc.Humidity()
	time.sleep(1)
	line= timevalue+ "	Temperature: "+str(tempvalue)+" C	Humidity: "+str(humvalue)+" %RH 	Luminosity: "+str(lightvalue)+" Lux\n"
	f.write(line)
	f.close()
def checkButton():
	global click
        try:
                if (grovepi.digitalRead(Button)):
                        click=click+1
                        if click==4:
                                click=0
                        time.sleep(.5)
        except IOError:
		print "Button error"

def threaded_function(arg):
	global timevalue, tempvalue, lightvalue,humvalue
	while not exitapp:
        	getSensorValues()

thread = Thread(target=threaded_function, args=(10,))
thread.start()

def main():
	global timevalue, tempvalue, lightvalue, humvalue, click
	light.init()
	text=" "
	new_text="Start Sensing   Please Wait.."
	setText(new_text)
	setRGB(50,50,50)
	time.sleep(5)
	while (True):
		checkButton()
		if click==0:
			new_text=timevalue+ "   Click.." 
		if click==1:
			new_text="Luminosity:     " + str("{0:.2f}".format(lightvalue))+ " Lux"
		if click==2:
			new_text="Temperature:    "+ str("{0:.2f}".format(tempvalue))+ " C" 
		if click==3:
			new_text="Humidity:       "+ str("{0:.2f}".format(humvalue))+" %RH"
		if new_text!=text:
			text=new_text
			setText(text)

try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise






