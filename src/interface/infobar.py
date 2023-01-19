import tkinter as tk
from tkinter import ttk
from typing import Dict

from .. import app_settings

_font = app_settings.gui["font"]["family"]
_fontsize = app_settings.gui["font"]["size"]


class Infobar(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, variables: Dict, widgets: Dict, *args, **kwargs
    ):

        super().__init__(parent, name="infobar", *args, **kwargs)

        self.variables = {}
        variables["infobar"] = self.variables

        self.widgets = {}
        widgets["infobar"] = self.widgets

        self.create_label(self, name="xy", row=0, col=1, sticky="nsw")
        self.create_label(self, name="info", row=0, col=2, width=50)

        self.columnconfigure(1, weight=1)

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

    # def update_XY(self, XY_message: str):
    #     var = self.variables["xy"]
    #     var.set(XY_message)
