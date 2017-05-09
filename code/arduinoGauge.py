# -*- coding: utf-8 -*-
import glob
import serial
import time

ser = None


def connect():
    global ser
    ports = glob.glob('/dev/ttyA[A-Za-z]*')
    ser = serial.Serial(ports[0], 9600, timeout=1)
    ser.close()
    ser.open()
    time.sleep(3)


def write(a, b, c):
    global ser
    text = "%d%d%d" % (a, b, c)
    ser.write(text)
    ser.write("\n")
    time.sleep(0.2)
