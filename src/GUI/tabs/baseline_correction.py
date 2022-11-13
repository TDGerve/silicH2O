import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl
from typing import Union, List

from ..plots import Plot
from ..screens import Screen

on_settings_change = bl.signal("settings change")


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.make_buttons(variables, widgets)
        self.make_labels(variables, widgets)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def draw_plot(self, plot: Plot):
        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

    def make_buttons(self, variables, widgets):
        pass

    def make_labels(self, variables, widgets):
        pass
