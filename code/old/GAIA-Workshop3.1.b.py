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
import gaia_text
import properties
from sparkworks import SparkWorks

# Select pins for the leds and buttons
pin1 = [2, 4, 6]
pin2 = [3, 5, 7]
button = 8

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

# Variables for the sensors
rooms = None
temperature = [0, 0, 0]
humidity = [0, 0, 0]
timestamp = None
hours = 5

# Other global variables
thread = None
exitapp = False
sparkworks = None


# Update values from the database
def updateDataAvg(group, param):
    global timestamp
    resource = sparkworks.groupAggResource(group["uuid"], param["uuid"])
    summary = sparkworks.summary(resource["uuid"])
    timestamp = summary["latestTime"]
    values = summary["minutes60"]
    average = sum(values[:hours])/hours
    return round(average, 1)


# Get data from database
def getData():
    for i in [0, 1, 2]:
        if not exitapp:
            temperature[i] = updateDataAvg(rooms[i], sparkworks.phenomenon("Temperature"))
            humidity[i] = updateDataAvg(rooms[i], sparkworks.phenomenon("Relative Humidity"))


def threaded_function(sleep):
    i = sleep * 10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep*10
        time.sleep(0.1)
        i -= 1


# Sleep that breaks on click
def breakSleep(interval):
    i = 0
    while (i < interval*10):
        i += 1
        try:
            if (grovepi.digitalRead(button)):
                time.sleep(.5)
                break
        except IOError:
            print("Button Error")
        time.sleep(.1)


# Find out the maximum value
def showMaximum(values):
    max_value = max(values)
    for i in [0, 1, 2]:
        if values[i] == max_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)
    return max_value


# Find out the minimum value
def showMinimum(values):
    min_value = min(values)
    for i in [0, 1, 2]:
        if values[i] == min_value:
            grovepi.digitalWrite(pin1[i], 0)
            grovepi.digitalWrite(pin2[i], 1)
        else:
            grovepi.digitalWrite(pin1[i], 1)
            grovepi.digitalWrite(pin2[i], 0)
    return min_value


# Close all the leds
def closeLeds():
    for i in [0, 1, 2]:
        grovepi.digitalWrite(pin1[i], 0)
        grovepi.digitalWrite(pin2[i], 0)


def setup():
    global sparkworks, rooms, thread
    grovepi.pinMode(button, "INPUT")
    for i in [0, 1, 2]:
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

    print("Συλλογή δεδομένων, παρακαλώ περιμένετε...")
    grovelcd.setRGB(50, 50, 50)
    grovelcd.setText(gaia_text.loading_data)
    getData()
    print("Τελευταία ανανέωση δεδομένων: {0:s}\n"
          .format(datetime.datetime.fromtimestamp((timestamp/1000.0)).strftime('%Y-%m-%d %H:%M:%S')))

    thread = Thread(target=threaded_function, args=(10,))
    thread.start()


def loop():
    # minimum temperature
    minimum = showMinimum(temperature)
    print("Ελάχιστος μέσος όρος θερμοκρασίας [μοβ,πορτοκαλί,πράσινο]")
    print("{0:^33.1f} {1:s}"
          .format(minimum, str(temperature)))
    new_text = "Min {0:s}\n{1:>14.1f}oC".format("Temperature", minimum)
    grovelcd.setRGB(60, 60, 60)
    grovelcd.setText(new_text)
    breakSleep(5)

    for i in [0, 1, 2]:
        print("Μέσος όρος θερμοκρασίας: {0:s}: {1:5.1f} oC"
              .format(properties.the_rooms[i], temperature[i]))
        new_text = "{0:s}\n{1:>14.1f}oC".format("Avg Temperature", temperature[i])
        grovelcd.setRGB(R[i], G[i], B[i])
        grovelcd.setText(new_text)
        breakSleep(5)

    # maximum humidity
    maximum = showMaximum(humidity)
    print("Μέγιστος μέσος όρος υγρασίας [μοβ,πορτοκαλί,πράσινο]")
    print("{0:^28.1f} {1:s}"
          .format(maximum, str(humidity)))
    new_text = "Max {0:s}\n{1:>13s}%RH".format("Humidity", str(maximum))
    grovelcd.setRGB(60, 60, 60)
    grovelcd.setText(new_text)
    breakSleep(5)

    for i in [0, 1, 2]:
        print("Μέσος όρος υγρασίας: {0:s}: {1:5.1f} %RH"
              .format(properties.the_rooms[i], humidity[i]))
        new_text = "{0:s}\n{1:>13.1f}%RH".format("Avg Humidity", humidity[i])
        grovelcd.setRGB(R[i], G[i], B[i])
        grovelcd.setText(new_text)
        breakSleep(5)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
