# -*- coding: utf-8 -*-
import Tkinter as tk
from binascii import hexlify

button_1_state = False
button_2_state = False
switch_1_state = False
switch_2_state = False
switch_3_state = False

buffered_switch = 0

room_colors = [[255, 0, 255],
               [255, 128, 0],
               [0, 255, 0]]

grovepi_pin_state = [0 for i in range(18)]
pin_colors = ['red', 'green']
led_colors = ['black', 'blue', 'red']

grovepi = tk.Tk()
grovepi.attributes('-type', 'dialog')
grovepi.title("Grove LEDs and Buttons")

grovepi_pins_frame = tk.Frame(grovepi)
grovepi_pins_frame['borderwidth'] = 2
grovepi_pins_frame['relief'] = 'sunken'

grovepi_pins_labels = []
for l in range(18):
    grovepi_pins_labels.append(tk.Label(grovepi_pins_frame, text='_', font='TkFixedFont'))
    grovepi_pins_labels[l].grid(row=0, column=l)

grovepi_pins_frame.grid()

grovepi_rooms_frame = tk.Frame(grovepi)

grovepi_room_frames = []
grovepi_room_frames_labels = []
for f in range(3):
    grovepi_room_frames.append(tk.Frame(grovepi_rooms_frame, width=24, height=24))
    grovepi_room_frames[f].config(bg='#{0:02x}{1:02x}{2:02x}'.format(*room_colors[f]))
    grovepi_room_frames[f]['borderwidth'] = 5
    grovepi_room_frames[f]['relief'] = 'flat'
    grovepi_room_frames[f].grid(row=1, column=f, padx=5)
    grovepi_room_frames_labels.append(tk.Label(grovepi_room_frames[f], text=chr(ord('A')+f), font='TkFixedFont', width=2))
    grovepi_room_frames_labels[f].config(fg='white')
    grovepi_room_frames_labels[f].grid(row=0, column=0)


grovepi_rooms_frame.grid()


def _z_key(event):
    global button_1_state
    button_1_state = True


def _x_key(event):
    global button_2_state
    button_2_state = True


def _a_key(event):
    global switch_1_state
    switch_1_state = True


def _s_key(event):
    global switch_2_state
    switch_2_state = True


def _d_key(event):
    global switch_3_state
    switch_3_state = True


grovepi.bind("z", _z_key)
grovepi.bind("x", _x_key)
grovepi.bind("a", _a_key)
grovepi.bind("s", _s_key)
grovepi.bind("d", _d_key)

grovepi.update()


def pinMode(p, m):
    grovepi_pins_labels[p].config(text=m[0])
    grovepi.update()


def digitalWrite(p, s):
    grovepi_pins_labels[p].config(bg=pin_colors[s])
    grovepi_pin_state[p] = s
    frame = p/2 - 1
    if (p % 2) == 0:
        color = led_colors[s - grovepi_pin_state[p + 1]]
    elif (p % 2) == 1:
        color = led_colors[grovepi_pin_state[p - 1] - s]
    grovepi_room_frames_labels[frame].config(bg=color)
    grovepi.update()


def digitalRead(p):
    global button_1_state, button_2_state
    grovepi.update()
    if p == 8 and button_1_state:
        button_1_state = False
        return True
    if p == 7 and button_2_state:
        button_2_state = False
        return True
    return False


def analogRead(p):
    global switch_1_state, switch_2_state, switch_3_state, buffered_switch
    grovepi.update()
    if p == 0 and switch_1_state:
        switch_1_state = False
        if buffered_switch != 1023:
            buffered_switch = 1023
    if p == 0 and switch_2_state:
        switch_2_state = False
        if buffered_switch != 512:
            buffered_switch = 512
    if p == 0 and switch_3_state:
        switch_3_state = False
        if buffered_switch != 0:
            buffered_switch = 0
    return buffered_switch

