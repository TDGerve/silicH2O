import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import List, Optional

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ...plots import Baseline_correction_plot
from ..frames.Baseline_interpolation import Baseline_interpolation_frame
from ..frames.scrollframes import ScrollFrame
from ..frames.vertical_toolbar import vertical_toolbar
from ..validate_input import validate_numerical_input

on_settings_change = bl.signal("settings change")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.areas_variables = {}
        self.signal_variables = {}

        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables

        self.baseline_interpolation = Baseline_interpolation_frame(
            parent=self,
            name="baseline",
            widgets=widgets,
            variables=variables,
            bir_amount=5,
            width="7c",
        )
        self.baseline_interpolation.grid(row=0, column=3, sticky="nesw")
        self.make_signal_frame(self, 2, 3)
        self.make_areas_frame(self, 4, 3)
        # self.make_save_frame(7, 3)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(3, minsize="7c")

        self.rowconfigure(6, weight=1)

        self.make_vertical_divider(self, col=2)
        self.make_horizontal_dividers(self, rows=[1, 3, 5], col=3)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def make_vertical_divider(self, parent, col):
        rows = parent.grid_size()[1]
        ttk.Separator(self, orient=tk.VERTICAL).grid(
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
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=rows, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

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

        make_label_widgets(frame, labels, names, [1, 1], self.areas_variables)

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

        make_label_widgets(frame, labels, names, [1, 1], self.signal_variables)


def make_label_widgets(
    frame,
    labels: List[str],
    names: List[str],
    start_indeces: List[int],
    variables,
    trace: Optional[callable] = None,
):

    row, column = start_indeces

    for i, (name, label) in enumerate(zip(names, labels)):
        text_label = ttk.Label(frame, text=label, width=7, font=(_font, _fontsize))
        text_label.grid(row=i + 1, sticky="nesw")

        var = tk.StringVar(name=name)
        if trace is not None:
            var.trace("w", partial(trace, var=var))
        widget = ttk.Label(
            frame,
            textvariable=var,
            anchor="e",
            background="white",
            width=7,
            font=(_font, _fontsize),
            style="TButton",
            # borderwidth=1,
        )
        widget.grid(
            row=i + row, column=column, sticky=("nse")  # , padx=padding, pady=padding
        )

        variables[name] = var
