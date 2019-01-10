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
    _a = hex(int(a))[-1]
    _b = hex(int(b))[-1]
    _c = hex(int(c))[-1]
    if __name__ == '__main__':
        print(_a, _b, _c)
    data = [ord(_a), ord(_b), ord(_c), ord('\n')]
    bus.write_i2c_block_data(ARDUINO_GAUGE_ADDR, 0x20, data)


if __name__ == '__main__':
    while True:
        for x in range(13):
            time.sleep(1)
            write(x, x, x)
