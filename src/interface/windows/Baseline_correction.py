import tkinter as tk
from tkinter import ttk
from typing import List

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ...plots import Baseline_correction_plot
from ..frames.Baseline_interpolation import Baseline_interpolation_frame
from ..frames.vertical_toolbar import vertical_toolbar
from ..widgets import make_label_widgets

on_settings_change = bl.signal("settings change")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.baseline_widgets = {}

        widgets["baseline"] = self.baseline_widgets

        self.baseline_variables = {}
        self.areas_variables = {}
        self.signal_variables = {}

        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables
        variables["baseline"] = self.baseline_variables

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize="8c")

        self.rowconfigure(0, weight=1)

        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(row=0, column=0, sticky="nesw")

        self.settings_frame = ttk.Frame(self)
        self.settings_frame.grid(row=0, column=1, sticky="nesw")

        self.populate_settings_frame(self.settings_frame)

        for child in self.winfo_children():
            # child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def populate_settings_frame(self, parent):

        parent.rowconfigure(7, weight=1)
        parent.columnconfigure(1, weight=1)

        tk.Label(parent, text="Baseline", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=1, sticky=("nw")
        )

        self.baseline_interpolation = Baseline_interpolation_frame(
            parent=parent,
            name="baseline",
            widgets=self.baseline_widgets,
            variables=self.baseline_variables,
            bir_amount=5,
            min_regions=3,
            width="7c",
        )
        self.baseline_interpolation.grid(row=1, column=1, sticky="nesw")

        self.make_signal_frame(parent, row=3, col=1)
        self.make_areas_frame(parent, row=5, col=1)

        self.make_vertical_divider(parent, col=0)
        self.make_horizontal_dividers(parent, rows=[2, 4, 6], col=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def reset_baseline_widgets(self, bir_amount):
        widget = self.settings_frame.nametowidget("baseline")
        widget.make_bir_widgets(bir_amount)

    def make_vertical_divider(self, parent, col):
        rows = parent.grid_size()[1]
        ttk.Separator(parent, orient=tk.VERTICAL).grid(
            row=0, column=col, rowspan=rows, sticky=("ns")
        )

    def make_horizontal_dividers(self, parent, rows: List[int], col: int):
        for row in rows:
            ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
                row=row, column=col, sticky=("new")
            )

    def draw_plot(self, plot: Baseline_correction_plot):
        fig = plot.fig
        rows = self.grid_size()[1]
        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=rows, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self.plot_frame)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

    def make_areas_frame(self, parent, row: int, col: int):

        frame = ttk.Frame(parent, name="areas")
        frame.grid(row=row, column=col, sticky=("nesw"))

        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Areas",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=("nsw"))

        labels = ["Silicate", "H\u2082O", "H\u2082O:silicate"]
        names = ["silicate", "H2O", "H2OSi"]

        make_label_widgets(
            parent=frame,
            labels=labels,
            names=names,
            start_indeces=[1, 0],
            variables=self.areas_variables,
        )

    def make_signal_frame(self, parent, row, col):

        frame = ttk.Frame(parent, name="signal")
        frame.grid(row=row, column=col, sticky=("nesw"))

        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Signal",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=("nsw"))

        labels = ["noise", "Silicate S:N", "H\u2082O S:N"]
        names = ["noise", "Si_SNR", "H2O_SNR"]

        make_label_widgets(
            parent=frame,
            labels=labels,
            names=names,
            start_indeces=[1, 0],
            variables=self.signal_variables,
        )
