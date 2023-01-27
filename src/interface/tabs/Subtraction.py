import tkinter as tk
from tkinter import ttk
from typing import List

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ..frames.Baseline_interpolation import Baseline_interpolation_frame
from ..frames.vertical_toolbar import vertical_toolbar

on_settings_change = bl.signal("settings change")
on_load_interference = bl.signal("load interference")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Subtraction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.interference_deconvolution_widgets = {}

        widgets["interference_deconvolution"] = self.interference_deconvolution_widgets

        self.interference_deconvolution_variables = {}

        variables[
            "interference_deconvolution"
        ] = self.interference_deconvolution_variables

        self.make_interference_frame(
            parent=self, widgets=widgets, variables=variables, row=0, col=3
        )

        self.make_horizontal_dividers(self, rows=[1, 3, 5], col=3)
        self.make_vertical_divider(self, col=2)
        # self.make_deconvolution_frame(self, 2, 3)
        # self.make_subtraction_frame(self, 4, 3)

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=0)
        self.columnconfigure(3, minsize="7c")

        self.rowconfigure(6, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def reset_baseline_widgets(self, bir_amount):
        widget = self.nametowidget("interference").nametowidget("baseline")
        widget.make_bir_widgets(bir_amount)

    def draw_plot(self, plot):
        fig = plot.fig
        rows = self.grid_size()[1]
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=rows, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        # toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

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

    def make_interference_frame(self, parent, widgets, variables, row: int, col: int):

        frame = ttk.Frame(parent, name="interference")
        frame.grid(row=row, column=col, sticky="nesw")
        frame.columnconfigure(0, minsize="7c")

        tk.Label(frame, text="Interference", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, sticky=("nsw")
        )

        load_button = ttk.Button(
            frame,
            text="load spectrum",
            state=tk.DISABLED,
            name="load_interference",
            command=on_load_interference.send,
        )
        load_button.grid(row=1, column=0, sticky="ns")

        self.interference_deconvolution_widgets["load_spectrum"] = load_button

        baseline_interpolation = Baseline_interpolation_frame(
            parent=frame,
            name="interference",
            widgets=widgets,
            variables=variables,
            bir_amount=5,
            width="7c",
        )
        baseline_interpolation.grid(row=2, column=0, sticky="nesw")

    def make_deconvolution_frame(self, parent, row: int, col: int):

        deconvolution_frame = ttk.Frame(parent, name="deconvolution")
        deconvolution_frame.grid(row=row, column=col, sticky="nesw")

    def make_subtraction_frame(self, parent, row: int, col: int):

        subtraction_frame = ttk.Frame(parent, name="subtraction")
        subtraction_frame.grid(row=row, column=col, sticky="nesw")
