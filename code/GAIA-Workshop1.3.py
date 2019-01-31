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
switch = 0

# Colors for the rooms
R = [255, 255, 0]
G = [0, 128, 255]
B = [255, 0, 0]

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
exitapp = False
sparkworks = None


# Update values from the database
def updateSiteData(group, param):
    global timestamp
    resource = sparkworks.groupDeviceResource(group["uuid"], param["uuid"])
    latest = sparkworks.latest(resource["uuid"])
    timestamp = latest["latestTime"]
    value = latest["latest"]
    return round(value, 1)


# Get data from database
def getData():
    print("Νέα δεδομένα:")
    for i in [0, 1, 2]:
        if not exitapp:
            luminosity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Luminosity"))
        if not exitapp:
            temperature[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Temperature"))
        if not exitapp:
            humidity[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Relative Humidity"))
        if not exitapp:
            noise[i] = updateSiteData(rooms[i], sparkworks.phenomenon("Noise"))
        print(("{0:s}\n\t" +
               "Υγρασία: {1:.1f}%RH\n\t" +
               "Φωτεινότητα: {2:.1f}\n\t" +
               "Θερμοκρασία: {3:.1f}C\n\t" +
               "Θόρυβος: {4:.1f}dB")
              .format(rooms[i]["name"].encode('utf-8'),
                      humidity[i],
                      luminosity[i],
                      temperature[i],
                      noise[i]))


def threaded_function(sleep):
    i = sleep*10
    while not exitapp:
        if i == 0:
            getData()
            i = sleep*10
        time.sleep(0.1)
        i -= 1


def checkButton(button, idx, init, limit, step=1):
    idx_changed = False
    try:
        if grovepi.digitalRead(button):
            idx += step
            if idx >= limit:
                idx = init
            idx_changed = True
            time.sleep(0.5)
    except IOError:
        print("Button Error")
    return idx, idx_changed


def checkSwitch(switch, idx, state_1, state_2):
    idx_changed = False
    try:
        reading = grovepi.analogRead(switch)
        if reading < 500:
            if idx != state_1:
                idx = state_1
                idx_changed = True
        else:
            if idx != state_2:
                idx = state_2
                idx_changed = True
        time.sleep(0.5)
    except IOError:
        print("Switch Error")
    return idx, idx_changed


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


# Show luminosity on leds
def showLuminosity(light_value, a, b):
    if light_value < 200:
        # red LED
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)
    else:
        # blue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)


# Show the temperature
def showTemperature(temperature_value, a, b):
    if 18 < temperature_value < 25:
        # BLue LED
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        # red led
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


# Show the humidity
def showHumidity(humidity_value, a, b):
    if 30 < humidity_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


# Show the noise
def showNoise(noise_value, a, b):
    if noise_value < 50:
        grovepi.digitalWrite(a, 1)
        grovepi.digitalWrite(b, 0)
    else:
        grovepi.digitalWrite(a, 0)
        grovepi.digitalWrite(b, 1)


def setup():
    global sparkworks, rooms, thread
    grovepi.pinMode(button, "INPUT")
    grovepi.pinMode(switch, "INPUT")
    for i in [0, 1, 2]:
        grovepi.pinMode(pin1[i], "OUTPUT")
        grovepi.pinMode(pin2[i], "OUTPUT")
    closeLeds()
    grovelcd.setRGB(0, 0, 0)
    grovelcd.setText("")

    print("Όνομα χρήστη:\n\t{0:s}\n"
          .format(properties.username))
    print("Επιλεγμένες αίθουσες:")
    sparkworks = SparkWorks(properties.client_id, properties.client_secret)
    sparkworks.connect(properties.username, properties.password)
    rooms = sparkworks.select_rooms(properties.uuid, properties.the_rooms)
    for room in rooms:
        print("\t{0:s}"
              .format(room['name'].encode('utf-8')))
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
    global option_idx, mode_idx, option_idx_changed, mode_idx_changed, option_idx_limit
    if option_idx_changed or mode_idx_changed:
        if mode_idx_changed:
            option_idx = 0

        option_idx_changed = False
        mode_idx_changed = False

        if option_idx == 0:
            if mode_idx == 0:
                print("Λειτουργία 1: Πατήστε το κουμπί για να ξεκινήσετε")
                grovelcd.setText("Mode 1:\nClick to continue")
                grovelcd.setRGB(50, 50, 50)
                closeLeds()
                option_idx = 2
                option_idx_limit = 5
            if mode_idx == 1:
                print("Λειτουργία 2: Πατήστε το κουμπί για να ξεκινήσετε")
                grovelcd.setText("Mode 2:\nClick to continue")
                grovelcd.setRGB(50, 50, 50)
                closeLeds()
                option_idx = 7
                option_idx_limit = 14

        if option_idx == 2:
            closeLeds()
            print("Φωτεινότητα: [μοβ,πορτοκαλί,πράσινο]")
            print(luminosity)
            for i in [0, 1, 2]:
                grovelcd.setRGB(R[i], G[i], B[i])
                grovelcd.setText("Light:\n{0:.1f}".format(luminosity[i]))
                showLuminosity(luminosity[i], pin1[i], pin2[i])
                time.sleep(2)
            grovelcd.setRGB(60, 60, 60)
            grovelcd.setText("LIGHT\n{0:s}"
                             .format(gaia_text.click_to_continue))

        if option_idx == 3:
            closeLeds()
            print("Υγρασία: [μοβ,πορτοκαλί,πράσινο]")
            print(humidity)
            for i in [0, 1, 2]:
                grovelcd.setRGB(R[i], G[i], B[i])
                grovelcd.setText("Humidity:\n{0:.1f} %RH".format(humidity[i]))
                showHumidity(humidity[i], pin1[i], pin2[i])
                time.sleep(2)
            grovelcd.setRGB(60, 60, 60)
            grovelcd.setText("HUMIDITY\n{0:s}"
                             .format(gaia_text.click_to_continue))

        if option_idx == 4:
            closeLeds()
            print("Θερμοκρασία: [μοβ,πορτοκαλί,πράσινο]")
            print(temperature)
            for i in [0, 1, 2]:
                grovelcd.setRGB(R[i], G[i], B[i])
                grovelcd.setText("Temperature:\n{0:.1f} Cdeg".format(temperature[i]))
                showTemperature(temperature[i], pin1[i], pin2[i])
                time.sleep(2)
            grovelcd.setRGB(60, 60, 60)
            grovelcd.setText("TEMPERATURE\n{0:s}"
                             .format(gaia_text.click_to_continue))

        if option_idx == 5:
            closeLeds()
            print("Θόρυβος: [μοβ,πορτοκαλί,πράσινο]")
            print(noise)
            for i in [0, 1, 2]:
                grovelcd.setRGB(R[i], G[i], B[i])
                grovelcd.setText("Noise:\n{0:.1f} dB".format(noise[i]))
                showNoise(noise[i], pin1[i], pin2[i])
                time.sleep(2)
            grovelcd.setRGB(60, 60, 60)
            grovelcd.setText("NOISE\n{0:s}"
                             .format(gaia_text.click_to_continue))

        if option_idx == 7:
            # maximum light
            print("Μέγιστη Φωτεινότητα [μοβ, πορτοκαλί, πράσινο]")
            print("{0:^19.1f} {1:s}"
                  .format(showMaximum(luminosity), str(luminosity)))
            time.sleep(.1)
        if option_idx == 8:
            # minimum light
            print("Ελάχιστη Φωτεινότητα [μοβ, πορτοκαλί, πράσινο]")
            print("{0:^20.1f} {1:s}"
                  .format(showMinimum(luminosity), str(luminosity)))
            time.sleep(.1)
        if option_idx == 9:
            # maximum humidity
            print("Μέγιστη Υγρασία [μοβ, πορτοκαλί, πράσινο]")
            print("{0:^15.1f} {1:s}"
                  .format(showMaximum(humidity), str(humidity)))
            time.sleep(.1)
        if option_idx == 10:
            # minimum humidity
            print("Ελάχιστη Υγρασία [μοβ, πορτοκαλί, πράσινο] %RH")
            print("{0:^16.1f} {1:s}"
                  .format(showMinimum(humidity), str(humidity)))
            time.sleep(.1)
        if option_idx == 11:
            # maximum temperature
            print("Μέγιστη Θερμοκρασία [μοβ, πορτοκαλί, πράσινο] Cdeg")
            print("{0:^19.1f} {1:s}"
                  .format(showMaximum(temperature), str(temperature)))
            time.sleep(.1)
        if option_idx == 12:
            # minimum temperature
            print("Ελάχιστη Θερμοκρασία [μοβ, πορτοκαλί, πράσινο] Cdeg")
            print("{0:^20.1f} {1:s}"
                  .format(showMinimum(temperature), str(temperature)))
            time.sleep(.1)
        if option_idx == 13:
            # maximum noise
            print("Μέγιστος Θόρυβος [μοβ, πορτοκαλί, πράσινο] dB")
            print("{0:^16.1f} {1:s}"
                  .format(showMaximum(noise), str(noise)))
            time.sleep(.1)
        if option_idx == 14:
            # minimum noise
            print("Ελάχιστος Θόρυβος [μοβ, πορτοκαλί, πράσινο] dB")
            print("{0:^17.1f} {1:s}"
                  .format(showMaximum(noise), str(noise)))
            time.sleep(.1)

    option_idx, option_idx_changed = checkButton(button, option_idx, 0, option_idx_limit)
    mode_idx, mode_idx_changed = checkSwitch(switch, mode_idx, 0, 1)


def main():
    setup()
    while not exitapp:
        loop()


try:
    main()
except KeyboardInterrupt:
    exitapp = True
    raise
