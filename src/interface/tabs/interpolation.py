import tkinter as tk
from tkinter import ttk
from typing import List

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ..frames.Baseline_interpolation import Baseline_interpolation_frame
from ..frames.vertical_toolbar import vertical_toolbar

on_settings_change = bl.signal("settings change")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2

on_set_processing = bl.signal("set processing")


class Interpolation_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.widgets = {}
        self.variables = {}

        variables["interpolation"] = self.variables
        widgets["interpolation"] = self.widgets

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize="7c")

        self.rowconfigure(0, weight=1)

        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(row=0, column=0, sticky="nesw")

        self.settings_frame = ttk.Frame(self)
        self.settings_frame.grid(row=0, column=1, sticky="nesw")

        # self.columnconfigure(0, weight=1)
        # self.columnconfigure(3, minsize="7c")
        # self.rowconfigure(6, weight=1)

        # self.make_interpolation_frame(
        #     parent=self,
        #     name="interpolation",
        #     widgets=self.widgets,
        #     variables=self.variables,
        #     row=0,
        #     col=3,
        # )

        # self.make_horizontal_dividers(self, rows=[1], col=3)
        # self.make_vertical_divider(self, col=2)

        self.populate_settings_frame(
            self.settings_frame, widgets=self.widgets, variables=self.variables
        )

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def populate_settings_frame(self, parent, widgets, variables):

        parent.rowconfigure(7, weight=1)
        parent.columnconfigure(1, weight=1)

        self.make_interpolation_frame(
            parent=parent,
            name="interpolation",
            widgets=widgets,
            variables=variables,
            row=0,
            col=1,
        )

        self.make_use_checkbutton(
            parent=parent, variables=variables, widgets=widgets, row=2, col=1
        )

        self.make_horizontal_dividers(parent, rows=[1], col=1)
        self.make_vertical_divider(parent, col=0)

    def draw_plot(self, plot):
        fig = plot.fig
        rows = self.grid_size()[1]
        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=rows, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self.plot_frame)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        # toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

    def reset_baseline_widgets(self, bir_amount):
        widget = self.settings_frame.nametowidget("interpolation").nametowidget(
            "baseline"
        )
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

    def make_interpolation_frame(
        self, parent, name, widgets, variables, row: int, col: int
    ):

        frame = ttk.Frame(parent, name=name)
        frame.grid(row=row, column=col, sticky="nesw")
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        baseline_interpolation = Baseline_interpolation_frame(
            parent=frame,
            name=name,
            widgets=widgets,
            variables=variables,
            bir_amount=5,
            min_regions=1,
            width="7c",
        )
        baseline_interpolation.grid(row=0, column=0, columnspan=2, sticky="nesw")

    def make_use_checkbutton(self, parent, variables, widgets, row, col):
        var = tk.BooleanVar(value=False)
        checkbutton = ttk.Checkbutton(
            parent,
            text="use",
            variable=var,
            onvalue=True,
            offvalue=False,
            command=lambda: on_set_processing.send(
                type="interpolated", value=var.get()
            ),
            state=tk.DISABLED,
        )

        checkbutton.grid(row=row, column=col, sticky="nw")

        variables["use"] = var
        widgets["use"] = checkbutton
