import tkinter as tk
from tkinter import ttk
from typing import Dict

import blinker as bl

from .. import app_settings

_font = app_settings.gui["font"]["family"]
_fontsize = app_settings.gui["font"]["size"]

on_save_sample = bl.signal("save sample")
on_reset_sample = bl.signal("reset sample")
on_save_all = bl.signal("save all")


class Infobar(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, variables: Dict, widgets: Dict, *args, **kwargs
    ):

        super().__init__(parent, name="infobar", *args, **kwargs)

        self.variables = {}
        variables["infobar"] = self.variables

        self.widgets = {}
        widgets["infobar"] = self.widgets

        self.create_save_buttons(self, row=0, col=2)
        self.create_label(self, name="xy", row=0, col=1, sticky="se")
        self.create_label(self, name="info", row=0, col=0, width=50, sticky="sw")

        self.columnconfigure(1, weight=1)

        for widget in self.winfo_children():
            widget.grid_configure(padx=3, pady=5)

    def create_label(self, frame, name, row, col, sticky="nse", width=20):

        var = tk.StringVar(name=name)
        widget = ttk.Label(
            frame,
            name=name,
            textvariable=var,
            anchor="e",
            width=width,
            font="TkFixedFont",  # (_font, _fontsize),
        )
        widget.grid(row=row, column=col, sticky=sticky)

        self.variables[name] = var

    def create_save_buttons(self, frame, row, col):

        reset = ttk.Button(
            frame,
            text="reset sample",
            state=tk.DISABLED,
            name="reset_sample",
            command=lambda: on_reset_sample.send(),
        )
        reset.grid(row=row, column=col, sticky="nes")

        save = ttk.Button(
            frame,
            text="save sample",
            state=tk.DISABLED,
            name="save_sample",
            command=lambda: on_save_sample.send(),
        )
        save.grid(row=row, column=col + 1, sticky="nesw")

        save_all = ttk.Button(
            frame,
            text="save all",
            state=tk.DISABLED,
            name="save_all",
            command=lambda: on_save_all.send(),
        )
        save_all.grid(row=row, column=col + 2, sticky="nesw")

        for i in range(2):
            frame.columnconfigure(i, weight=1)

        names = ["reset_sample", "save_sample", "save_all"]
        widgets = [reset, save, save_all]
        for name, widget in zip(names, widgets):
            self.widgets[name] = widget

    # def update_XY(self, XY_message: str):
    #     var = self.variables["xy"]
    #     var.set(XY_message)
