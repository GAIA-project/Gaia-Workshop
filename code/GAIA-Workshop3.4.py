#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import datetime
import forecastio
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaia_text
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
pin1 = [2, 4]
pin2 = [3, 5]
button = 8
button2 = 7

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
rooms = None
in_temp = [0, 0]
in_humi = [0, 0]
out_temp = [0 for x in range(16)]
out_humi = [0 for x in range(16)]
timestamp = None

# Other global variables
time_idx = None
time_idx_changed = False
room_idx = 0
room_idx_changed = False
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateData(group, param):
    global timestamp
    resource = sparkworks.groupAggResource(group["uuid"], param["uuid"])
    summary = sparkworks.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    values = summary["minutes60"]
    return values


# Get data from database
def getSensorData():
    for i in [0, 1]:
        if not exitapp:
            in_temp[i] = updateData(rooms[i], sparkworks.phenomenon("Temperature"))
            in_humi[i] = updateData(rooms[i], sparkworks.phenomenon("Relative Humidity"))


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


# Find out the minimum value
def showMinimum(values):
    min_value = min(values)
    for i in [0, 1]:
        if values[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)
    return min_value


# Close all the leds
def closeLeds():
    for i in [0, 1]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def getOutsideData():
    # Outside weather necessary variables
    api_key = "a96063dd6aacda945d68bb05209e848f"
    current_time = datetime.datetime.now()
    print("forecast.io: " + str(current_time))
    forecast = forecastio.load_forecast(api_key,
                                        properties.GPSposition[0],
                                        properties.GPSposition[1],
                                        time=current_time)

    by_hour = forecast.hourly()
    i = 0
    hour = [0 for x in range(16)]
    for hourly_data in by_hour.data:
        if i < 16:
            hour[15 - i] = hourly_data.time
            out_temp[15 - i] = hourly_data.temperature
            out_humi[15 - i] = hourly_data.humidity * 100
            i += 1


def setup():
    global sparkworks, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for i in [0, 1]:
        grovepi.pinMode(pin1[i], "OUTPUT")
        grovepi.pinMode(pin2[i], "OUTPUT")
    closeLeds()
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    print("Όνομα χρήστη:\n\t{0:s}"
          .format(properties.username))
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    group = sparkworks.group(properties.uuid)
    print("\t{0:s}\n"
          .format(group["name"].encode("utf-8")))
    print("Επιλεγμένες αίθουσες:")
    rooms = sparkworks.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}"
              .format(room["name"].encode("utf-8")))
    print("\n")


def loop():
    global time_idx, room_idx, time_idx_changed, room_idx_changed
    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaia_text.loading_data)
        getSensorData()
        print("Τελευταία ανανέωση δεδομένων: {0:s}\n"
              .format(datetime.datetime.fromtimestamp((timestamp/1000.0)).strftime('%Y-%m-%d %H:%M:%S')))
        getOutsideData()
        time_idx = 0
        time_idx_changed = True

    # Έναρξη διαδικασίας εμφάνισης αποτελεσμάτων
    if time_idx_changed or room_idx_changed:
        room_idx_changed = False
        time_idx_changed = False

        timevalue = datetime.datetime.fromtimestamp((timestamp/1000.0)-3600*(time_idx))
        strdate = timevalue.strftime('%Y-%m-%d %H:%M:%S')
        strtime = timevalue.strftime('%H:%M')

        # Print to terminal
        print(" Ημερομηνία: {0:s}"
              .format(strdate))
        print("Θερμοκρασία: {0:s}: {1:5.1f}"
              .format("Εξωτερική", out_temp[time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}"
              .format("Εξωτερική", out_humi[time_idx]))
        print("Θερμοκρασία: {0:s}: {1:5.1f}"
              .format(properties.the_rooms[room_idx], in_temp[room_idx][time_idx]))
        print("    Υγρασία: {0:s}: {1:5.1f}"
              .format(properties.the_rooms[room_idx], in_humi[room_idx][time_idx]))

        # Print to LCD
        str_in_temp = "Ti:{0:.1f}".format(in_temp[room_idx][time_idx])
        str_in_humi = "Hi:{0:.1f}".format(in_humi[room_idx][time_idx])
        str_out_temp = "To:{0:.1f}".format(out_temp[time_idx]).rjust(16 - len(str_in_temp))
        str_out_humi = "Ho:{0:.1f}".format(out_humi[time_idx]).rjust(16 - len(str_in_humi))
        new_text = str_in_temp + str_out_temp + str_in_humi + str_out_humi
        grovelcd.setRGB(R[room_idx], G[room_idx], B[room_idx])
        grovelcd.setText(new_text)

        # Show with red the classroom with minimum temperature
        showMinimum([temp[time_idx] for temp in in_temp])
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = checkButton(button, time_idx, None, 16)
    room_idx, room_idx_changed = checkButton(button2, room_idx, 0, 2)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
