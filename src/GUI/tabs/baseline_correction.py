import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl

from ..plots import Double_plot
from ... import settings

on_settings_change = bl.signal("settings change")


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, plots, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.setup_plot(plots)

        self.make_buttons()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def draw_plot(self, fig: plt.figure):
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

    def setup_plot(self, plots):

        baseline_correction_plot = Double_plot(dpi=settings.gui["geometry"]["dpi"])
        baseline_correction_plot.setup_ax1(
            title="Silicate region",
            ylabel="Intensity (arbitr. units",
            limits=(200, 1400),
        )
        baseline_correction_plot.setup_ax2(
            title="H$_2$O region", xlabel="Raman shift cm$^{-1}$", limits=(2000, 4000)
        )

        plots["baseline_correction"] = baseline_correction_plot
        self.draw_plot(baseline_correction_plot.fig)

    def make_buttons(self):
        pass
