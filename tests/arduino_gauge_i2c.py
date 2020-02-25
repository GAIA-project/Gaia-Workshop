# -*- coding: utf-8 -*-
import sys
import time
import Tkinter as tk

num_rings = 3
num_leds = 12
ring_colors = [[255, 0, 255],
               [255, 127, 0],
               [0, 255, 0]]

arduinoGauge = tk.Tk()
arduinoGauge.attributes('-type', 'dialog')
arduinoGauge.title("Arduino Gauge")

arduinoGauge_frames = []

for r in range(num_rings):
    ring = []
    for l in range(num_leds):
        ring.append(tk.Frame(arduinoGauge, width=24, height=24))
        ring[l]['borderwidth'] = 2
        ring[l]['relief'] = 'sunken'
        ring[l].grid(row=r, column=l)
    arduinoGauge_frames.append(ring)

arduinoGauge.update()


def connect():
    print("connect")
    time.sleep(1)


def write(*args):
    if len(args) != num_rings:
        print("Wrong number of arguments to " + __name__ + "." + sys._getframe().f_code.co_name)
        return 1
    for ring in range(num_rings):
        color = '#{0:02x}{1:02x}{2:02x}'.format(*ring_colors[ring])
        for led in range(num_leds):
            if led < args[ring]:
                arduinoGauge_frames[ring][led].config(bg=color)
            else:
                arduinoGauge_frames[ring][led].config(bg='black')
    arduinoGauge.update()

