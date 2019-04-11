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
import gaiapi
import properties
from sparkworks import SparkWorks
import arduino_gauge_i2c as arduino_gauge

# Select pins for the leds and buttons
led_pins = [[2, 3],
            [4, 5]]
button = 8
button2 = 7

# Colors for the rooms
lcd_rgbs = [[255, 0, 255],
            [255, 128, 0],
            [0, 255, 0]]

# Variables for the sensors
phases = None
current = [None, None, None]
power = [None, None, None]
max_power = [None, None, None]
timestamp = None

# Other global variables
time_idx = None
time_idx_changed = False
phase_idx = -1
phase_idx_changed = False
thread = None
data_updated = False
exitapp = False
api = None
verbose = False


# Initialize connection to the database
def initData():
    print("Όνομα χρήστη:\n\t{0:s}".format(properties.username))
    sw = SparkWorks(properties.client_id, properties.client_secret)
    sw.connect(properties.username, properties.password)
    group = sw.group(properties.uuid)
    print("\t{0:s}\n".format(group["name"].encode("utf-8")))

    room, phases = sw.select_power_meter(properties.uuid, properties.lab_room)
    print("Επιλεγμένη αίθουσα:")
    print("\t{0:s}".format(room["name"].encode("utf-8")))
    if not phases:
        sys.exit("Δεν βρέθηκαν αισθητήρες ρεύματος για την επιλεγμένη αίθουσα")
    print("Επιλεγμένοι αισθητήρες:")
    for phase in phases:
        print("\t{0:s}".format(phase["systemName"]))
    print("\n")
    return sw, phases


# Update values from the database
def updateData(sw, resource):
    summary = sw.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    values = summary["minutes60"]
    maximum = max(summary["minutes60"])
    return timestamp, [round(value, 1) for value in values], round(maximum, 1)


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(phases)):
        if verbose:
            print("{0:s}".format(phases[i]["systemName"].encode('utf-8')))
        if not exitapp:
            timestamp, values, maximum = updateData(api, phases[i])
            current[i] = [v/1000 for v in values]
            power[i] = [v*230/1000 for v in values]
            max_power[i] = maximum*230/1000
            if verbose:
                print("\tΙσχύς: {0:.1f} {1:.1f}".format(power[i], max_power[i]))


def setup():
    global api, phases, thread
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")
    arduino_gauge.connect()
    arduino_gauge.write(1, 1, 1)

    api, phases = initData()


def loop():
    global time_idx, phase_idx, time_idx_changed, phase_idx_changed
    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaiapi.loading_data)
        getData()
        gaiapi.printLastUpdate(timestamp)
        time_idx = 0
        time_idx_changed = True

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if time_idx_changed or phase_idx_changed:
        phase_idx_changed = False

        timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        # Print to terminal
        if time_idx_changed:
            time_idx_changed = False
            open_leds = [0, 0, 0]
            basemax = max(max_power)
            gaiapi.printDate(strdate)
            for i in range(len(phases)):
                gaiapi.printRoom(current[i][time_idx],
                                 "Φάση {0:d}".format(i+1),
                                 "     Ρεύμα", "A")
                gaiapi.printRoom(power[i][time_idx],
                                 "Φάση {0:d}".format(i+1),
                                 "Κατανάλωση", "W")
                open_leds[i] = gaiapi.mapToLeds(power[i][time_idx], basemax, 12)
            arduino_gauge.write(*open_leds)

        # Print to LCD
        if phase_idx == -1:
            total = sum(p[time_idx] for p in power if p is not None)
            new_text = "{0:s}\n{1:>15.1f}W".format(strtime, total)
            grovelcd.setRGB(50, 50, 50)
        else:
            new_text = "{0:s}\nPhase {1:d}: {2:>6.1f}W".format(strtime, phase_idx+1, power[phase_idx][time_idx])
            grovelcd.setRGB(*lcd_rgbs[phase_idx])
        grovelcd.setText(new_text)
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = gaiapi.checkButton(button, time_idx, None, 23)
    phase_idx, phase_idx_changed = gaiapi.checkButton(button2, phase_idx, -1, len(phases)-1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise

