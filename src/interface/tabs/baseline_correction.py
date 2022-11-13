import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl
import numpy as np
from typing import Union, List, Tuple
from functools import partial

from ..plots import Plot
from ..validate_input import validate_numerical_input, invalid_input


from ... import settings

on_settings_change = bl.signal("settings change")

_font = settings.gui["font"]["family"]
_fontsize = settings.gui["font"]["size"]


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.variables = []  # MAKE THIS INTO A FLAT LIST, INSTEAD OF A NESTED LIST
        self.widgets = []  # SAMPLE HERE
        variables["bir_settings"] = self.variables
        widgets["bir_settings"] = self.widgets

        self.make_settings_frame()
        self.make_widgets()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=2, pady=2)

    def draw_plot(self, plot: Plot):
        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

    def make_settings_frame(self):
        baseline_label = ttk.Label(
            text="Baseline interpolation regions", font=(_font, _fontsize + 5, "bold")
        )
        frame = ttk.Labelframe(self, labelwidget=baseline_label, name="settings")
        frame.grid(row=0, column=1, sticky=("nesw"))

        frame.rowconfigure(0, weight=0)
        frame.columnconfigure(0, weight=0)
        for i in [1, 2]:
            frame.columnconfigure(i, weight=2)

    def make_widgets(self):
        frame = self.nametowidget("settings")

        for k, name in zip([1, 2], ["From", "to"]):
            ttk.Label(frame, text=name, font=(_font, _fontsize)).grid(
                row=0, column=k, sticky=("sw")
            )

        for i in range(5):
            label = ttk.Label(frame, text=f"{i + 1}", font=(_font, _fontsize))
            label.grid(row=i + 1, column=0, sticky=("nse"))

            _vars = []
            _entries = []
            for j in range(2):
                var = tk.StringVar()
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    validate="focus",
                    validatecommand=(
                        self.register(partial(self.validate_bir_input, index=(i, j))),
                        "%P %W",
                    ),
                    invalidcommand=(
                        self.register(partial(self.invalid_bir_input, index=(i, j))),
                        r"%s",
                    ),
                    width=5,
                    background="white",
                    font=(_font, _fontsize),
                    state=tk.DISABLED,
                    name=f"{i},{j}",
                )
                entry.grid(row=i + 1, column=j + 1, sticky=("nesw"))
                _vars.append(var)
                _entries.append(entry)
            self.widgets.append(_entries)
            self.variables.append(_vars)

    def validate_bir_input(self, new_value, index=Tuple[int, int]):

        i0, i1 = index
        widget = self.widgets[i0][i1]
        variable = self.variables[i0][i1]

        return partial(
            validate_numerical_input,
            widget=widget,
            variable=variable,
            accepted_range=[200, 4000],
        )(new_value)

    def invalid_bir_input(self, old_value, index=Tuple[int, int]):
        i0, i1 = index
        variable = self.variables[i0][i1]

        return partial(invalid_input, variable=variable)(old_value)
