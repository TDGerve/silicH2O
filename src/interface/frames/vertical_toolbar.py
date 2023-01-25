import tkinter as tk
from tkinter import ttk

import blinker as bl
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from ... import app_configuration

_font = app_configuration.gui["font"]["family"]

on_mouse_movement = bl.signal("mouse moved")


class vertical_toolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
        s.pack(side=tk.TOP, pady=5)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        # print(s)
        on_mouse_movement.send("mouse moved", infobar={"xy": s})

    @staticmethod
    def _mouse_event_to_message(event):
        if event.inaxes and event.inaxes.get_navigate():
            try:
                s = f"X:{int(event.xdata): >6} Y:{int(event.ydata):>6}"
            except (ValueError, OverflowError):
                pass
            else:
                return s
        return f"X:{'-': >6} Y:{'-':>6}"
