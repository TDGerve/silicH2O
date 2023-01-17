import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from .. import app_settings

_font = app_settings.gui["font"]["family"]


class vertical_toolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)
        self._message = tk.StringVar(master=self)
        self._message_label = tk.Label(
            master=self, font=(_font, 6), width=5, height=2, textvariable=self._message
        )
        self._message_label.pack(side=tk.BOTTOM)

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
        pass

    @staticmethod
    def _mouse_event_to_message(event):
        if event.inaxes and event.inaxes.get_navigate():
            try:
                s = f"{int(event.xdata): >5}\n{int(event.ydata):>5}"
            except (ValueError, OverflowError):
                pass
            else:
                return s
        return ""
