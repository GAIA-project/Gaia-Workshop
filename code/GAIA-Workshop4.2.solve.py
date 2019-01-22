#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaia_text
import properties
from sparkworks import SparkWorks
import arduino_gauge_i2c as arduino_gauge

# Select pins for the leds and buttons
button = 8
button2 = 7

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
phases = None
current = [0, 0, 0]
power = [0, 0, 0]
max_power = [0, 0, 0]
timestamp = None
total = [0 for x in range(48)]

# Other global variables
time_idx = None
time_idx_changed = False
phase_idx = -1
phase_idx_changed = False
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateData(resource):
    global timestamp
    summary = sparkworks.summary(resource['uuid'])
    values = summary["minutes60"]
    timestamp = summary["latestTime"]
    maximum = max(summary["minutes60"])
    return (values, round(maximum, 1))


# Get data from database
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            data = updateData(phases[i])
            current[i] = [d/1000 for d in data[0]]
            power[i] = [d*230/1000 for d in data[0]]
            max_power[i] = data[1] * 230 / 1000


def checkButton(button, idx, init, limit, step=1):
    idx_changed = False
    try:
        if (grovepi.digitalRead(button)):
            idx += step
            if idx >= limit:
                idx = init
            idx_changed = True
            time.sleep(.5)
    except IOError:
        print("Button Error")
    return idx, idx_changed


def mapValueToLeds(value, max, leds_available):
    step = max / leds_available
    # num_leds = math.ceil(value/step)
    num_leds = round(value/step)
    return int(num_leds)


def megisti():
    hour = 0
    maximum = 0
    for i in range(len(total)):
        total[i] = sum(p[i] for p in power)
        if total[i] > maximum:
            maximum = total[i]
            hour = 1
    return maximum, hour


def setup():
    global sparkworks, phases
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

    print("Όνομα χρήστη:\n\t{0:s}\n".format(properties.username))
    print("Επιλεγμένοι αισθητήρες:")
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    phases = sparkworks.current_phases(properties.uuid)
    for phase in phases:
        print("\t{0:s}".format(phase['systemName']))
    print("\n")


def loop():
    global time_idx, phase_idx, time_idx_changed, phase_idx_changed
    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaia_text.loading_data)
        getData()
        time_idx = 0
        time_idx_changed = True

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if time_idx_changed or phase_idx_changed:
        phase_idx_changed = False

        timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        maximum, unused = megisti()

        # Print to terminal
        if time_idx_changed:
            time_idx_changed = False
            open_leds = [0, 0, 0]
            print("Ημερομηνία: {0:s}".format(strdate))
            msg = "{0:s} Ρεύμα: {1:5.2f}A, Κατανάλωση: {2:7.2f}W"
            for i in [0, 1, 2]:
                print(msg.format(phases[i]['systemName'], current[i][time_idx], power[i][time_idx]))
                open_leds[i] = mapValueToLeds(power[i][time_idx], maximum, 12)
            arduino_gauge.write(*open_leds)

        new_text = "{0:s}\n{1:>15.2f}W".format(strtime, maximum)
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(new_text)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = checkButton(button, time_idx, None, 48)
    phase_idx, phase_idx_changed = checkButton(button2, phase_idx, -1, 3)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
