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
import gaiapi
import properties
from sparkworks import SparkWorks

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
rooms = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]
out_temp = [0 for x in range(16)]
out_humi = [0 for x in range(16)]
timestamp = None

# Other global variables
time_idx = None
time_idx_changed = False
room_idx = 0
room_idx_changed = False
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

    print("Επιλεγμένες αίθουσες:")
    rooms = sw.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}".format(room["name"].encode("utf-8")))
    print("\n")
    return sw, rooms


# Update values from the database
def updateData(sw, group, param):
    resource = sw.groupAggResource(group["uuid"], sw.phenomenon(param)["uuid"])
    summary = sw.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    values = summary["minutes60"]
    return timestamp, [round(value, 1) for value in values]


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(led_pins)):
        if verbose:
            print("{0:s}".format(rooms[i]["name"].encode('utf-8')))
        if not exitapp:
            timestamp, temperature[i] = updateData(api, rooms[i], "Temperature")
            if verbose:
                print("\tΘερμοκρασία: {0:.1f}".format(temperature[i]))
        if not exitapp:
            timestamp, humidity[i] = updateData(api, rooms[i], "Relative Humidity")
            if verbose:
                print("\tΥγρασία: {0:.1f}".format(humidity[i]))


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
    global api, rooms
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(button2, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    api, rooms = initData()


def loop():
    global time_idx, room_idx, time_idx_changed, room_idx_changed
    if time_idx is None:
        print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
        grovelcd.setRGB(50, 50, 50)
        grovelcd.setText(gaiapi.loading_data)
        getData()
        gaiapi.printLastUpdate(timestamp)
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
        gaiapi.printDate(strdate)
        gaiapi.printRoom(temperature[room_idx][time_idx],
                         properties.the_rooms[room_idx],
                         "Θερμοκρασία", "oC")
        gaiapi.printRoom(humidity[room_idx][time_idx],
                         properties.the_rooms[room_idx],
                         "    Υγρασία", "%RH")
        gaiapi.printRoom(out_temp[time_idx],
                         "Εξωτερική",
                         "Θερμοκρασία", "oC")
        gaiapi.printRoom(out_humi[time_idx],
                         "Εξωτερική",
                         "    Υγρασία", "%RH")

        # Print to LCD
        str_in_temp = "iT:{0:.1f}".format(temperature[room_idx][time_idx])
        str_in_humi = "iH:{0:.1f}".format(humidity[room_idx][time_idx])
        str_out_temp = "oT:{0:.1f}".format(out_temp[time_idx]).rjust(16 - len(str_in_temp))
        str_out_humi = "oH:{0:.1f}".format(out_humi[time_idx]).rjust(16 - len(str_in_humi))
        new_text = str_in_temp + str_out_temp + str_in_humi + str_out_humi
        grovelcd.setRGB(*lcd_rgbs[room_idx])
        grovelcd.setText(new_text)

        # Show with red the classroom with minimum temperature
        val, idx = gaiapi.showMinimum(led_pins, [temp[time_idx] for temp in temperature[:len(led_pins)]])
    # Τέλος διαδικασίας εμφάνισης αποτελεσμάτων

    # Detect button presses
    time_idx, time_idx_changed = gaiapi.checkButton(button, time_idx, None, 15)
    room_idx, room_idx_changed = gaiapi.checkButton(button2, room_idx, 0, len(led_pins)-1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
