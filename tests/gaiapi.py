# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
sys.path.append(os.getcwd())
sys.dont_write_bytecode = True
import grovepi

click_to_continue = "Click to continue!"
press_to_start = "Press the button to start..."
loading_data = "Loading Data..."
max_message = "Max %s: %d %s"
min_message = "Min %s: %d %s"
max_min_message = "%s(%s): Max:%d;Min:%d"


def checkButton(btn, idx, init, lim, stp=1):
    idx_changed = False
    try:
        if grovepi.digitalRead(btn):
            idx += stp
            if idx > lim:
                idx = init
            idx_changed = True
            time.sleep(0.5)
    except IOError:
        print("Button Error")
    return idx, idx_changed


def checkSwitch(swtch, idx, stt_1, stt_2):
    idx_changed = False
    try:
        reading = grovepi.analogRead(swtch)
        if reading < 500:
            if idx != stt_1:
                idx = stt_1
                idx_changed = True
        else:
            if idx != stt_2:
                idx = stt_2
                idx_changed = True
        time.sleep(0.5)
    except IOError:
        print("Switch Error")
    return idx, idx_changed


def breakSleep(btn, intervl):
    i = 0
    while (i < intervl*10):
        i += 1
        try:
            if (grovepi.digitalRead(btn)):
                time.sleep(.5)
                break
        except IOError:
            print("Button Error")
        time.sleep(0.1)


# Find out the minimum value
def showMinimum(pins, values):
    _min = min(values)
    _idx = values.index(_min)
    for i in range(len(values)):
        if i == _idx:
            grovepi.digitalWrite(pins[i][0], 0)
            grovepi.digitalWrite(pins[i][1], 1)
        else:
            grovepi.digitalWrite(pins[i][0], 1)
            grovepi.digitalWrite(pins[i][1], 0)
    return _min, _idx


# Find out the maximum value
def showMaximum(pins, values):
    _max = max(values)
    _idx = values.index(_max)
    for i in range(len(values)):
        if i == _idx:
            grovepi.digitalWrite(pins[i][0], 0)
            grovepi.digitalWrite(pins[i][1], 1)
        else:
            grovepi.digitalWrite(pins[i][0], 1)
            grovepi.digitalWrite(pins[i][1], 0)
    return _max, _idx


# Close all the leds
def closeLeds(pins):
    for pair in pins:
        for pin in pair:
            grovepi.digitalWrite(pin, 0)


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


def mapToLeds(val, bmx, lds_avail):
    step = bmx/lds_avail
    # num_leds = math.ceil(value/step)
    num_leds = round(val/step)
    return int(num_leds)


def printLastUpdate(ts):
    print("Τελευταία ανανέωση δεδομένων: {0:s}"
          .format(datetime
                  .datetime
                  .fromtimestamp((ts/1000.0))
                  .strftime('%Y-%m-%d %H:%M:%S')))


def printDate(dt):
    print("Ημερομηνία: {0:s}"
          .format(dt))


def printRoom(quantity, room, title, unit=""):
    print("{0:s} {1:s}: {2:5.1f} {3:s}"
          .format(title, room, quantity, unit))


def printMap(quantity):
    print("Mωβ: {0: <6.1f} Πορτοκαλί: {1: <6.1f} Πράσινη: {2: <6.1f}"
          .format(*quantity))


def printRooms(quantity, title):
    print("{0:s}".format(title))
    printMap(quantity)


def printRoomsMinMax(quantity, val, title, word):
    print("{0:s} {1:s}:{2:.1f}".format(word, title, val))
    printMap(quantity)
