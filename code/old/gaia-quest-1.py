
import time
import grovepi
from grove_rgb_lcd import *

# Connect the Grove Button to digital port D8
# SIG,NC,VCC,GND
button = 8

grovepi.pinMode(button,"INPUT")
new_text=" "
text1="Waiting         for a click..."
text2="YOU HAVE CLICK  THE BUTTON!!"
while True:
    try:
        if new_text!=text1:
                new_text=text1
                setText(new_text)
        setRGB(50,50,50)
        if grovepi.digitalRead(button):
                new_text=text2
                setText(new_text)
                setRGB(0,255,0)
                time.sleep(.5)

    except IOError:
        print ("Error")

