# -*- coding: utf-8 -*-
import time,sys

if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

ARDUINO_GAUGE_ADDR = 0x2D


def connect():
    time.sleep(3)
    return True


def write(a, b, c):
    _a = ord(str(int(a)))
    _b = ord(str(int(b)))
    _c = ord(str(int(c)))
    data = [_a, _b, _c, ord('\n')]
    bus.write_i2c_block_data(ARDUINO_GAUGE_ADDR, 0x20, data)


if __name__ == '__main__':
    while True:
        write(5, 4, 3)
        time.sleep(1)
        write('c', 'c', 'c')
        time.sleep(1)
        write(1, 2, 3)
        time.sleep(1)
