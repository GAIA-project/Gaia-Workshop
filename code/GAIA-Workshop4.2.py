
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
current = [0, 0, 0]
power_consumption = [0, 0, 0]
maximum = [0, 0, 0, 0]
timestamp = 0

main_site = None
phases = []
total_power = None

R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]
text = ""
new_text = ""

ButtonH = 8
ButtonPh = 7
grovepi.pinMode(ButtonH, "INPUT")
grovepi.pinMode(ButtonPh, "INPUT")

text = gaia_text.loading_data
setText(text)

setRGB(60, 60, 60)


def updateData(resource):
    global timestamp
    summary = sparkworks.summary(resource)
    global maximum
    val = summary["minutes60"]
    timestamp = summary["latestTime"]
    #print time
    val_max = max(summary["minutes60"])
    return (val, float("{0:.1f}".format(float(val_max))))


def getData():
    global phases, maximum, current, power_consumption
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            maximum[i] = data[1] * 230 / 1000
            current[i] = data[0]
            power_consumption[i] = current[i]


print ("Username: \n\t%s\n" % properties.username).encode("utf8", "replace")
print "Sensors:"

arduinoGauge.connect()
arduinoGauge.write(1, 2, 3)

#sparkworks.connect(properties.username, properties.password)
# for room in properties.the_power_room:
#    print '\t%s' % room.decode('utf-8')


# total Power
sparkworks.connect(properties.username, properties.password)
main_site = sparkworks.main_site()
phases = sparkworks.current_phases(main_site)


print "\t%s" % phases[0]["uri"]
print "\t%s" % phases[1]["uri"]
print "\t%s" % phases[2]["uri"]


new_text = "Click button to start!"


def map_value_to_leds(m, val, leds_available):
    if val == 0:
        return 0
    steap = m / leds_available
    mod = val / steap + 1
    return math.floor(mod)


def main():
    global text, new_text, dev, ph, timestamp, power_consumption
    time.sleep(1)
    led = [0, 0, 0]
    led_part = [0, 0, 0]
    t = 0
    ph = 0
    new_t = 0
    while not exitapp:
        # detect Button that choose houre
        try:
            if (grovepi.digitalRead(ButtonH)):
                setText("New Hour")
                t = t + 1
                if t == 47:
                    setText("Take new data")
                    t = 0
                time.sleep(.5)
                print "hour" + str(t)
        except IOError:
            print "Button Error"
        # detect button that choose phase
        try:
            if (grovepi.digitalRead(ButtonPh)):
                setText("click...")
                ph = ph + 1
                if ph >= 4:
                    ph = 0
                print "Ph" + str(ph)
                time.sleep(.5)
        except IOError:
            print "Button Error"

        # Show Total Power (dev=0)
        if t == 0:
            getData()
            basemax = max(maximum[0], maximum[1], maximum[2])
            new_text = "Getting data..."
            t = 1
        else:
            # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
            if new_t != t:
                new_t = t
                p = power_consumption[0][t - 1] + power_consumption[1][t - 1] + power_consumption[2][t - 1]

                timevalue = datetime.datetime.fromtimestamp((timestamp / 1000.0) - 3600 * (t - 1))
                strtime = timevalue.strftime('%Y-%m-%d %H:%M:%S')
                print strtime

                for i in [0, 1, 2]:
                    print phases[i]["uri"], " Current: " + str(float("{0:.2f}".format(current[i][t - 1] / 1000))) + \
                        " A  " + "Power: " + str(float("{0:.2f}".format(power_consumption[i][t - 1] * 230 / 1000))) + " W"
                    led[i] = map_value_to_leds(basemax, power_consumption[i][t - 1] * 230 / 1000, 11)
                    print led[i]
                    time.sleep(.1)
                arduinoGauge.write(led[0], led[1], led[2])

            if ph == 0:
                new_text = strtime + ": " + str(float("{0:.2f}".format(p))) + "W"
                setRGB(60, 60, 60)
            else:
                new_text = "ph" + str(ph) + ":" + str(float("{0:.2f}".format(power_consumption[ph - 1][t - 1] * 230 / 1000))) + "W"
                setRGB(R[ph - 1], G[ph - 1], B[ph - 1])
            # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

        if text != new_text:
            text = new_text
            print "LCD show:", text
            setText(text)


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
