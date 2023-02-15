import tkinter as tk
from functools import partial
from tkinter import ttk

import blinker as bl
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ..frames.scrollframes import ScrollFrame
from ..widgets.validate_input import validate_numerical_input

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize + 2

on_set_H2Oreference = bl.signal("set H2O reference")
on_set_calibration_std = bl.signal("set calibration std")


class Calibration_window(tk.Toplevel):
    def __init__(self, parent, title, widgets, variables):

        super().__init__(master=parent)
        self.title = title

        self.widgets = {}
        self.variables = {}

        widgets["calibration"] = self.widgets
        variables["calibration"] = self.variables

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.scrollframe = None

        self.make_sample_frame(parent=self, row=0, col=0, rowspan=2)

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

        self.attributes("-topmost", True)

    def make_sample_frame(self, parent, row: int, col: int, rowspan: int):
        background_color = app_configuration.background_color

        self.scrollframe = ScrollFrame(
            parent,
            name="sample_scrollframe",
            background_color=background_color,
            width="12c",
        )
        self.scrollframe.grid(row=row, column=col, rowspan=rowspan, sticky="nesw")

        header_labels = [
            "Sample  ",
            "H\u2082O:silicate  ",
            "H\u2082O (wt.%)  ",
            "use  ",
        ]

        for k, name in enumerate(header_labels):
            tk.Label(
                self.scrollframe.headers, text=name, font=(_font, _fontsize_head)
            ).grid(row=0, column=k, sticky=("nsw"))

        self.make_sample_widgets(sample_amount=20, state=tk.DISABLED)

    def make_io_frame(self, parent: tk.Frame, row: int, col: int):
        ...

    def make_results_frame(self, parent: tk.Frame, row: int, col: int):
        ...

    def draw_plot(self, plot):

        plot_frame = ttk.Frame(self, name="plot")
        plot_frame.grid(row=0, column=1, sticky="nesw")
        plot_frame.grid_configure(padx=10, pady=10)

        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

    def make_sample_widgets(self, sample_amount, state=tk.NORMAL):

        parent = self.scrollframe.inner_frame

        for widget in parent.winfo_children():
            widget.destroy()

        for i in range(sample_amount):

            label_var = tk.StringVar(value=f"{'':<17}")
            H2OSi_var = tk.DoubleVar()
            h2o_var = tk.DoubleVar()
            use_var = tk.BooleanVar()

            label = ttk.Label(
                parent,
                textvariable=label_var,
                font=(_font, _fontsize),
                width=17,
            )
            h2oSi = ttk.Label(
                parent,
                textvariable=H2OSi_var,
                font=(_font, _fontsize),
                width=8,
            )
            h2o = ttk.Entry(
                parent,
                validate="focusout",
                validatecommand=(
                    parent.register(
                        partial(
                            self.validate_h2o,
                            index=i,
                        )
                    ),
                    r"%P %s %W",
                ),
                invalidcommand=(
                    parent.register(partial(self.invalid_h2o, index=i)),
                    r"%s %P",
                ),
                width=4,
                background="white",
                font=(_font, _fontsize),
                state=state,
            )

            use = ttk.Checkbutton(
                parent,
                text="",
                variable=use_var,
                onvalue=True,
                offvalue=False,
                command=partial(on_set_calibration_std.send, sample_index=i),
            )

            label.grid(row=i, column=0, sticky="nsw")
            h2oSi.grid(row=i, column=1, sticky="nesw")
            h2o.grid(row=i, column=2, sticky="nesw")
            use.grid(row=i, column=3, sticky="nesw")

            self.variables[f"samplename_{i:02d}"] = label_var
            self.variables[f"h2oSi_{i:02d}"] = H2OSi_var

            self.widgets[f"h2o_{i:02d}"] = h2o
            self.variables[f"h2o_{i:02d}"] = h2o_var

            self.variables[f"use_{i:02d}"] = use_var

            for i in range(4):
                parent.columnconfigure(i, weight=1)

    def validate_h2o(self, values: str, index: int):
        new_value = values[: values.index(" ")]
        widget = self.widgets[f"h2o_{index:02d}"]
        variable = self.variables[f"h2o_{index:02d}"]

        valid, new_value = validate_numerical_input(
            value=new_value,
            accepted_range=[0, np.inf],
            widget=widget,
            variable=variable,
            dtype=float,
        )

        if valid:
            on_set_H2Oreference.send(sample_index=index, H2O=new_value)

        return valid

    def invalid_h2o(self, values: str, index: int):

        variable = self.variables[f"h2o_{index:02d}"]
        old_value = variable.get()

        widget = self.widgets[f"h2o_{index:02d}"]
        widget.delete(0, tk.END)
        widget.insert(0, float(old_value))
