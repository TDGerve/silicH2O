import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import List

import blinker as bl
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ..frames.Baseline_interpolation import (
    Baseline_interpolation_frame,
    Baseline_interpolation_regions,
)
from ..frames.vertical_toolbar import vertical_toolbar
from ..widgets import set_value_from_widget
from ..widgets.validate_input import invalid_widget_input, validate_widget_input

on_load_interference = bl.signal("load interference")
on_remove_interference = bl.signal("remove interference")


on_deconvolve_interference = bl.signal("deconvolve interference")
on_subtract_interference = bl.signal("subtract interference")
on_set_processing = bl.signal("set processing")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Interference_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.interference_widgets = {}
        self.deconvolution_widgets = {}
        self.subtraction_widgets = {}
        widgets["interference"] = self.interference_widgets
        widgets["deconvolution"] = self.deconvolution_widgets
        widgets["subtraction"] = self.subtraction_widgets

        self.interference_variables = {}
        self.deconvolution_variables = {}
        self.subtraction_variables = {}
        variables["interference"] = self.interference_variables
        variables["deconvolution"] = self.deconvolution_variables
        variables["subtraction"] = self.subtraction_variables

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, minsize="7c")
        self.rowconfigure(6, weight=1)

        self.make_interference_frame(
            parent=self,
            name="interference",
            widgets=self.interference_widgets,
            variables=self.interference_variables,
            row=0,
            col=3,
        )
        self.make_deconvolution_frame(
            parent=self,
            name="deconvolution",
            widgets=self.deconvolution_widgets,
            variables=self.deconvolution_variables,
            row=2,
            col=3,
        )
        self.make_subtraction_frame(
            parent=self,
            name="subtraction",
            widgets=self.subtraction_widgets,
            variables=self.subtraction_variables,
            row=4,
            col=3,
        )

        self.make_horizontal_dividers(self, rows=[1, 3, 5], col=3)
        self.make_vertical_divider(self, col=2)

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

    def make_interference_frame(
        self, parent, name, widgets, variables, row: int, col: int
    ):

        frame = ttk.Frame(parent, name=name)
        frame.grid(row=row, column=col, sticky="nesw")
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        tk.Label(frame, text="Interference", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=("nsw")
        )

        load_button = ttk.Button(
            frame,
            text="load",
            state=tk.DISABLED,
            name="load_interference",
            command=on_load_interference.send,
        )
        load_button.grid(row=1, column=0, sticky="nesw")

        remove_button = ttk.Button(
            frame,
            text="remove",
            state=tk.DISABLED,
            name="remove_interference",
            command=on_remove_interference.send,
        )
        remove_button.grid(row=1, column=1, sticky="nesw")

        widgets["load_spectrum"] = load_button
        widgets["remove_spectrum"] = remove_button

        baseline_interpolation = Baseline_interpolation_frame(
            parent=frame,
            name=name,
            widgets=widgets,
            variables=variables,
            bir_amount=5,
            width="7c",
        )
        baseline_interpolation.grid(row=2, column=0, columnspan=2, sticky="nesw")

    def make_deconvolution_frame(
        self, name, parent, widgets, variables, row: int, col: int
    ):

        frame = ttk.Frame(parent, name=name)
        frame.grid(row=row, column=col, sticky="nesw")

        tk.Label(
            frame, text="Deconvolution", font=(_font, _fontsize_head, "bold")
        ).grid(row=0, column=0, sticky=("nsw"))

        labels = [
            "min. peak height",
            "fit window",
            "residuals threshold (%)",
            "max iterations",
        ]
        names = ["peak_height", "fit_window", "residuals_threshold", "max_iterations"]
        limits = [[1, np.Inf], [1, 50], [1, 100], [1, 20]]
        dtypes = [int, int, float, int]

        for i, (label, var_name, limit, dtype) in enumerate(
            zip(labels, names, limits, dtypes)
        ):
            text_label = ttk.Label(frame, text=label, width=20, font=(_font, _fontsize))
            text_label.grid(row=i + 1, column=0, sticky="esw")

            validate_func = partial(
                validate_widget_input,
                accepted_range=limit,
                group="deconvolution",
                name=var_name,
                widgets=widgets,
                variables=variables,
                dtype=dtype,
            )
            invalid_func = partial(
                invalid_widget_input,
                name=var_name,
                widgets=widgets,
                variables=variables,
            )
            var = tk.StringVar()
            entry = ttk.Entry(
                frame,
                validate="focusout",
                validatecommand=(frame.register(validate_func), "%P"),
                invalidcommand=(frame.register(invalid_func), r"%s"),
                width=4,
                background="white",
                font=(_font, _fontsize),
                state=tk.DISABLED,
            )
            entry.grid(row=i + 1, column=1, sticky="nesw")

            widgets[var_name] = entry
            variables[var_name] = var

        deconvolve_button = ttk.Button(
            frame,
            text="deconvolve",
            state=tk.DISABLED,
            name="deconvolve",
            command=on_deconvolve_interference.send,
        )
        deconvolve_button.grid(row=5, column=0, columnspan=2, sticky="ns")

        self.deconvolution_widgets["deconvolve_spectrum"] = deconvolve_button

        for i in range(2):
            frame.columnconfigure(i, weight=1)

    def make_subtraction_frame(
        self, parent, name, widgets, variables, row: int, col: int
    ):
        self.subtraction_regions = Baseline_interpolation_regions(
            widgets, variables, name="subtraction"
        )

        frame = ttk.Frame(parent, name=name)
        frame.grid(row=row, column=col, sticky="nesw")
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        tk.Label(frame, text="Subtract", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=("nsw")
        )

        tk.Label(
            frame,
            text="minimisation interval",
            font=(_font, _fontsize_head),
        ).grid(row=1, column=0, columnspan=2, sticky=("nsw"))

        for i in range(2):
            var = tk.StringVar()

            entry = ttk.Entry(
                frame,
                validate="focusout",
                validatecommand=(
                    parent.register(
                        partial(self.subtraction_regions.validate_bir_input, index=i)
                    ),
                    r"%P %s %W",
                ),
                invalidcommand=(
                    parent.register(
                        partial(self.subtraction_regions.invalid_bir_input, index=i)
                    ),
                    r"%s %P",
                ),
                width=4,
                background="white",
                font=(_font, _fontsize),
                state=tk.DISABLED,
            )
            entry.grid(row=2, column=i, sticky=("nesw"))

            self.subtraction_regions.add_bir(index=i, widget=entry, variable=var)

        ttk.Label(
            frame,
            text="smoothing",
            font=(_font, _fontsize_head),
        ).grid(row=3, column=0, sticky=("nsw"))

        var = tk.StringVar(name="smoothing")
        entry = ttk.Spinbox(
            frame,
            from_=0.1,
            to=100,
            increment=0.1,
            # textvariable=var,
            validate="focusout",
            validatecommand=(
                parent.register(self.subtraction_regions.validate_smoothing),
                "%P",
            ),
            invalidcommand=(
                parent.register(self.subtraction_regions.invalid_smoothing),
                r"%s",
            ),
            width=5,
            background="white",
            font=(_font, _fontsize),
            state=tk.DISABLED,
            name=name,
        )
        entry.grid(row=3, column=1, sticky=("nesw"))

        self.subtraction_regions.add_smoothing(widget=entry, variable=var)

        spectrum_selection = tk.StringVar(value="baseline_corrected")
        spectra = ("baseline_corrected", "deconvoluted")
        names = ("baseline*", "deconvoluted")
        for i, (spectrum, name) in enumerate(zip(spectra, names)):
            radio = ttk.Radiobutton(
                frame,
                text=name,
                variable=spectrum_selection,
                value=spectrum,
                command=partial(
                    set_value_from_widget,
                    variable=spectrum_selection,
                    group="subtraction",
                    name="spectrum",
                ),
                state=tk.DISABLED,
            )
            radio.grid(row=4, column=i)
            widgets[spectrum] = radio
        variables["spectrum"] = spectrum_selection

        subtract_button = ttk.Button(
            frame,
            text="subtract",
            state=tk.DISABLED,
            name="subtract",
            command=on_subtract_interference.send,
        )
        subtract_button.grid(row=5, column=0, sticky="ns")

        widgets["subtract_interference"] = subtract_button

        self.make_use_checkbutton(
            parent=frame, variables=variables, widgets=widgets, row=5, col=1
        )

    def make_use_checkbutton(self, parent, variables, widgets, row, col):
        var = tk.BooleanVar(value=False)
        checkbutton = ttk.Checkbutton(
            parent,
            text="use",
            variable=var,
            onvalue=True,
            offvalue=False,
            command=lambda: on_set_processing.send(
                type="interference_corrected", value=var.get()
            ),
            state=tk.DISABLED,
        )

        checkbutton.grid(row=row, column=col, sticky="ns")

        variables["use"] = var
        widgets["use"] = checkbutton

    def send_spectrum_processing(self, variable, type: str):
        value = eval(variable.get())
        on_set_processing.send(type=type, value=value)
