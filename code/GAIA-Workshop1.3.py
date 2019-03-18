#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
from threading import Thread
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi
import grove_rgb_lcd as grovelcd
import gaiapi
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
led_pins = [[2, 3],
            [4, 5],
            [6, 7]]
button = 8
switch = 0

# Colors for the rooms
lcd_rgbs = [[255, 0, 255],
            [255, 128, 0],
            [0, 255, 0]]

# Variables for the sensors
rooms = None
luminosity = [0, 0, 0]
temperature = [0, 0, 0]
humidity = [0, 0, 0]
noise = [0, 0, 0]
timestamp = None

# Other global variables
option_idx = 0
option_idx_changed = True
option_idx_limit = 1
mode_idx = 0
mode_idx_changed = True
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
    resource = sw.groupDeviceResource(group["uuid"], sw.phenomenon(param)["uuid"])
    latest = sw.latest(resource["uuid"])
    timestamp = latest["latestTime"]
    value = latest["latest"]
    return timestamp, round(value, 1)


# Get data from database
def getData():
    global timestamp
    if verbose:
        print("Νέα δεδομένα:")
    for i in range(len(rooms)):
        if verbose:
            print("{0:s}".format(rooms[i]["name"].encode('utf-8')))
        if not exitapp:
            timestamp, luminosity[i] = updateData(api, rooms[i], "Luminosity")
            if verbose:
                print("\tΦωτεινότητα: {0:.1f}".format(luminosity[i]))
        if not exitapp:
            timestamp, temperature[i] = updateData(api, rooms[i], "Temperature")
            if verbose:
                print("\tΘερμοκρασία: {0:.1f}".format(temperature[i]))
        if not exitapp:
            timestamp, humidity[i] = updateData(api, rooms[i], "Relative Humidity")
            if verbose:
                print("\tΥγρασία: {0:.1f}".format(humidity[i]))
        if not exitapp:
            timestamp, noise[i] = updateData(api, rooms[i], "Noise")
            if verbose:
                print("\tΘόρυβος: {0:.1f}".format(noise[i]))


def threadedFunction(sleep):
    global data_updated
    i = sleep*10
    while not exitapp:
        if i == 0:
            getData()
            data_updated = True
            i = sleep*10
        time.sleep(0.1)
        i -= 1


def setup():
    global api, rooms, thread
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(switch, "INPUT")
    for pair in led_pins:
        for pin in pair:
            grovepi.pinMode(pin, "OUTPUT")
    gaiapi.closeLeds(led_pins)
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    api, rooms = initData()

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaiapi.loading_data)
    getData()
    gaiapi.printLastUpdate(timestamp)

    thread = Thread(target=threadedFunction, args=(10,))
    thread.start()


def loop():
    global option_idx, option_idx_changed, mode_idx, mode_idx_changed, option_idx_limit, data_updated
    if option_idx_changed or mode_idx_changed:

        if mode_idx_changed or not option_idx:
            mode_idx_changed = False
            option_idx_changed = False

            if mode_idx == 0:
                print("Λειτουργία 1: Πατήστε το κουμπί για να ξεκινήσετε")
                grovelcd.setText("Mode 1:\nClick to continue")
                grovelcd.setRGB(50, 50, 50)
                gaiapi.closeLeds(led_pins)
                option_idx = 1
                option_idx_limit = 5
            if mode_idx == 1:
                print("Λειτουργία 2: Πατήστε το κουμπί για να ξεκινήσετε")
                grovelcd.setText("Mode 2:\nClick to continue")
                grovelcd.setRGB(50, 50, 50)
                gaiapi.closeLeds(led_pins)
                option_idx = 6
                option_idx_limit = 14

        if option_idx_changed:
            option_idx_changed = False
            mode_idx_changed = False

            if option_idx == 2:
                gaiapi.closeLeds(led_pins)
                gaiapi.printRooms(luminosity, "Φωτεινότητα")
                for i in range(len(rooms)):
                    gaiapi.showLuminosity(luminosity[i], *led_pins[i])
                for i in range(len(rooms)):
                    grovelcd.setRGB(*lcd_rgbs[i])
                    grovelcd.setText("Light\n{0:.1f}".format(luminosity[i]))
                    time.sleep(2)
                grovelcd.setRGB(60, 60, 60)
                grovelcd.setText("LIGHT\n{0:s}"
                                 .format(gaiapi.click_to_continue))

            if option_idx == 3:
                gaiapi.closeLeds(led_pins)
                gaiapi.printRooms(temperature, "Θερμοκρασία")
                for i in range(len(rooms)):
                    gaiapi.showTemperature(temperature[i], *led_pins[i])
                for i in range(len(rooms)):
                    grovelcd.setRGB(*lcd_rgbs[i])
                    grovelcd.setText("Temperature\n{0:.1f} Cdeg".format(temperature[i]))
                    time.sleep(2)
                grovelcd.setRGB(60, 60, 60)
                grovelcd.setText("TEMPERATURE\n{0:s}"
                                 .format(gaiapi.click_to_continue))

            if option_idx == 4:
                gaiapi.closeLeds(led_pins)
                gaiapi.printRooms(humidity, "Υγρασία")
                for i in range(len(rooms)):
                    gaiapi.showHumidity(humidity[i], *led_pins[i])
                for i in range(len(rooms)):
                    grovelcd.setRGB(*lcd_rgbs[i])
                    grovelcd.setText("Humidity\n{0:.1f} %RH".format(humidity[i]))
                    time.sleep(2)
                grovelcd.setRGB(60, 60, 60)
                grovelcd.setText("HUMIDITY\n{0:s}"
                                 .format(gaiapi.click_to_continue))

            if option_idx == 5:
                gaiapi.closeLeds(led_pins)
                gaiapi.printRooms(noise, "Θόρυβος")
                for i in range(len(rooms)):
                    gaiapi.showNoise(noise[i], *led_pins[i])
                for i in range(len(rooms)):
                    grovelcd.setRGB(*lcd_rgbs[i])
                    grovelcd.setText("Noise\n{0:.1f} dB".format(noise[i]))
                    time.sleep(2)
                grovelcd.setRGB(60, 60, 60)
                grovelcd.setText("NOISE\n{0:s}"
                                 .format(gaiapi.click_to_continue))

            # maximum light
            if option_idx == 7:
                val, idx = gaiapi.showMaximum(led_pins, luminosity[:len(rooms)])
                gaiapi.printRoomsMinMax(luminosity, val,
                                        "Φωτεινότητα", "Μέγιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MAX LUMINOSITY\n{0:.1f}".format(val))
                time.sleep(.1)
            # minimum light
            if option_idx == 8:
                val, idx = gaiapi.showMinimum(led_pins, luminosity[:len(rooms)])
                gaiapi.printRoomsMinMax(luminosity, val,
                                        "Φωτεινότητα", "Ελάχιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MIN LUMINOSITY\n{0:.1f}".format(val))
                time.sleep(.1)

            # maximum temperature
            if option_idx == 9:
                val, idx = gaiapi.showMaximum(led_pins, temperature[:len(rooms)])
                gaiapi.printRoomsMinMax(temperature, val,
                                        "Θερμοκρασία", "Μέγιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MAX TEMPERATURE\n{0:.1f}".format(val))
                time.sleep(.1)
            # minimum temperature
            if option_idx == 10:
                val, idx = gaiapi.showMinimum(led_pins, temperature[:len(rooms)])
                gaiapi.printRoomsMinMax(temperature, val,
                                        "Θερμοκρασία", "Ελάχιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MIN TEMPERATURE\n{0:.1f}".format(val))
                time.sleep(.1)

            # maximum humidity
            if option_idx == 11:
                val, idx = gaiapi.showMaximum(led_pins, humidity[:len(rooms)])
                gaiapi.printRoomsMinMax(humidity, val,
                                        "Υγρασία", "Μέγιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MAX HUMIDITY\n{0:.1f}".format(val))
                time.sleep(.1)
            # minimum humidity
            if option_idx == 12:
                val, idx = gaiapi.showMinimum(led_pins, humidity[:len(rooms)])
                gaiapi.printRoomsMinMax(humidity, val,
                                        "Υγρασία", "Ελάχιστη")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MIN HUMIDITY\n{0:.1f}".format(val))
                time.sleep(.1)

            # maximum noise
            if option_idx == 13:
                val, idx = gaiapi.showMaximum(led_pins, noise[:len(rooms)])
                gaiapi.printRoomsMinMax(noise, val,
                                        "Θόρυβος", "Μέγιστος")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MAX NOISE\n{0:.1f}".format(val))
                time.sleep(.1)
            # minimum noise
            if option_idx == 14:
                val, idx = gaiapi.showMinimum(led_pins, noise[:len(rooms)])
                gaiapi.printRoomsMinMax(noise, val,
                                        "Θόρυβος", "Ελάχιστος")
                grovelcd.setRGB(*lcd_rgbs[idx])
                grovelcd.setText("MIN NOISE\n{0:.1f}".format(val))
                time.sleep(.1)

    option_idx, option_idx_changed = gaiapi.checkButton(button, option_idx, 0, option_idx_limit)
    mode_idx, mode_idx_changed = gaiapi.checkSwitch(switch, mode_idx, 0, 1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
