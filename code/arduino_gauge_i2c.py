# -*- coding: utf-8 -*-
import sys
import time

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
    time.sleep(1)
    return True


def write(a, b, c):
    _a = ord('{0:X}'.format(a)[-1])
    _b = ord('{0:X}'.format(b)[-1])
    _c = ord('{0:X}'.format(c)[-1])
    if __name__ == '__main__':
        print(chr(_a), chr(_b), chr(_c))
    data = [_a, _b, _c, ord('\n')]
    bus.write_i2c_block_data(ARDUINO_GAUGE_ADDR, 0x20, data)


if __name__ == '__main__':
    while True:
        for x in range(13):
            time.sleep(.1)
            write(x, x, x)
