# -*- coding: utf-8 -*-
import Tkinter as tk
from binascii import hexlify

grove_rgb_lcd = tk.Tk()
grove_rgb_lcd.attributes('-type', 'dialog')
grove_rgb_lcd.title("Grove LCD Screen")

grove_rgb_lcd_frame = tk.Frame(grove_rgb_lcd)
grove_rgb_lcd_frame['borderwidth'] = 2
grove_rgb_lcd_frame['relief'] = 'sunken'

grove_rgb_lcd_labels = []
for r in range(2):
    row = []
    for c in range(16):
        row.append(tk.Label(grove_rgb_lcd_frame, text='_', font='TkFixedFont'))
        row[c].grid(row=r, column=c)
    grove_rgb_lcd_labels.append(row)

grove_rgb_lcd_frame.grid()
grove_rgb_lcd.update()


def setRGB(r, g, b):
    color = '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)
    for r in grove_rgb_lcd_labels:
        for l in r:
            l.config(bg=color)
    grove_rgb_lcd_frame.config(bg=color)
    grove_rgb_lcd.update()


def setText(text):
    for r in grove_rgb_lcd_labels:
        for l in r:
            l.config(text='_')
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            if c == '\n':
                continue
        grove_rgb_lcd_labels[row][count].config(text=c)
        count += 1
    grove_rgb_lcd.update()

