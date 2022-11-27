import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl
import numpy as np

from functools import partial
from typing import List

from ..vertical_toolbar import vertical_toolbar
from ...plots import Baseline_correction_plot
from ..validate_input import validate_numerical_input, invalid_input


from ... import app_settings

on_settings_change = bl.signal("settings change")
on_save_sample = bl.signal("save sample")
on_reset_sample = bl.signal("reset sample")
on_save_all = bl.signal("save all")

_font = app_settings.gui["font"]["family"]
_fontsize = app_settings.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.bir_widgets = []
        self.baseline_smoothing_widgets = []
        self.save_widgets = []

        self.bir_variables = []
        self.baseline_smoothing_variables = []
        self.areas_variables = []
        self.signal_variables = []

        variables["birs"] = self.bir_variables
        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables
        variables["baseline_smoothing"] = self.baseline_smoothing_variables

        widgets["birs"] = self.bir_widgets
        widgets["baseline_smoothing"] = self.baseline_smoothing_widgets
        widgets["baseline_save"] = self.save_widgets

        self.make_bir_frame(0, 3)
        self.make_signal_frame(2, 3)
        self.make_areas_frame(4, 3)
        self.make_save_frame(7, 3)
        self.make_dividers()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, minsize="8cm")

        self.rowconfigure(6, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def make_dividers(self):

        ttk.Separator(self, orient=tk.VERTICAL).grid(
            row=0, column=2, rowspan=8, sticky=("ns")
        )

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=3, sticky=("nesw"))
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, column=3, sticky=("new"))
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=5, column=3, sticky=("new"))

    def draw_plot(self, plot: Baseline_correction_plot):
        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=8, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        # toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

    def make_bir_frame(self, row: int, col: int):

        frame = ttk.Frame(self, name="birs")
        frame.grid(row=row, column=col, sticky=("nesw"))
        # frame.grid_propagate(0)

        tk.Label(frame, text="Baseline", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=("nsw")
        )

        tk.Label(
            frame,
            text="Interpolation regions",
            font=(_font, _fontsize_head),
        ).grid(row=1, column=0, columnspan=3, sticky=("nsw"))

        self.make_bir_widgets(frame)
        self.make_smoothing_widgets(frame, rowstart=8)

        for i in [1, 2]:
            frame.columnconfigure(i, weight=1)

    def make_bir_widgets(self, frame):

        for k, name in zip(range(3), ["No. ", "From", "to"]):
            tk.Label(frame, text=name, font=(_font, _fontsize, "italic")).grid(
                row=2, column=k, sticky=("nsw")
            )

        for i in range(5):
            label = ttk.Label(frame, text=f"{i + 1}. ", font=(_font, _fontsize))
            label.grid(row=i + 3, column=0, sticky=("nsw"))

            for j in range(2):
                var = tk.StringVar()
                entry = ttk.Entry(
                    frame,
                    textvariable=var,
                    validate="focusout",
                    validatecommand=(
                        self.register(
                            partial(self.validate_bir_input, index=i * 2 + j)
                        ),
                        "%P %W",
                    ),
                    invalidcommand=(
                        self.register(partial(self.invalid_bir_input, index=i * 2 + j)),
                        r"%s",
                    ),
                    width=5,
                    background="white",
                    font=(_font, _fontsize),
                    state=tk.DISABLED,
                    name=f"bir_{i * 2 + j}",
                    # relief="sunken",
                    # borderwidth=1,
                )
                entry.grid(row=i + 3, column=j + 1, sticky=("nesw"))

                self.bir_widgets.append(entry)
                self.bir_variables.append(var)

    def make_smoothing_widgets(self, frame, rowstart):

        ttk.Label(frame).grid(row=rowstart, column=0)  # empty row

        ttk.Label(
            frame,
            text="smoothing",
            font=(_font, _fontsize_head),
        ).grid(row=rowstart + 1, column=0, columnspan=3, sticky=("nsw"))

        var = tk.StringVar(name="baseline_smoothing_var")
        entry = ttk.Spinbox(
            frame,
            from_=0.1,
            to=10,
            increment=0.1,
            textvariable=var,
            validate="focus",
            validatecommand=(
                self.register(self.validate_smoothing),
                "%P",
            ),
            invalidcommand=(
                self.register(self.invalid_smoothing),
                r"%s",
            ),
            width=5,
            background="white",
            font=(_font, _fontsize),
            state=tk.DISABLED,
            name="baseline_smoothing",
        )
        entry.grid(row=rowstart + 1, column=2, sticky=("nesw"))

        button = ttk.Button(
            frame,
            text="Optimise smoothing",
            state=tk.DISABLED,
            name="optimise_baseline_smoothing",
        )  # command=func
        button.grid(row=rowstart + 2, column=0, columnspan=3, sticky="s")

        self.baseline_smoothing_widgets.append([entry, button])
        self.baseline_smoothing_variables.append(var)

    def make_areas_frame(self, row: int, col: int):

        frame = ttk.Frame(self, name="areas")
        frame.grid(row=row, column=col, sticky=("nesw"))

        # for i in range(4):
        #     frame.rowconfigure(i, weight=0)
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Areas",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=("nsw"))

        labels = ["Silicate", "H\u2082O", "H\u2082O:silicate"]
        names = ["Silicate", "H2O", "H2OSi"]

        make_label_widgets(frame, labels, names, [1, 1], self.areas_variables)

    def make_signal_frame(self, row, col):

        frame = ttk.Frame(self, name="signal")
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

    def make_save_frame(self, row, col):

        frame = ttk.Frame(self, name="save")
        frame.grid(row=row, column=col, sticky="esw")

        reset = ttk.Button(
            frame,
            text="reset sample",
            state=tk.DISABLED,
            name="reset_sample",
            command=lambda: on_reset_sample.send("baseline"),
        )
        reset.grid(row=0, column=0, sticky="nesw")

        save = ttk.Button(
            frame,
            text="save sample",
            state=tk.DISABLED,
            name="save_sample",
            command=lambda: on_save_sample.send("baseline"),
        )
        save.grid(row=0, column=1, sticky="nesw")

        save_all = ttk.Button(
            frame,
            text="save all",
            state=tk.DISABLED,
            name="save all",
            command=lambda: on_save_all.send("baseline"),
        )
        save_all.grid(row=1, column=1, sticky="nesw")

        for i in range(2):
            frame.columnconfigure(i, weight=1)

        self.save_widgets += [reset, save, save_all]

    def validate_bir_input(self, new_value: str, index: int):

        new_value = new_value[: new_value.index(" ")]
        widget = self.bir_widgets[index]
        variable = self.bir_variables[index]

        accepted_range = self.get_bir_range(index)

        valid, new_value = validate_numerical_input(
            new_value,
            accepted_range=accepted_range,
            widget=widget,
            variable=variable,
        )

        if valid:
            self.change_bir(index=index, value=new_value)
            return True
        else:
            return False

    def invalid_bir_input(self, old_value: str, index: int):
        old_value = old_value[: old_value.index(" ")]
        variable = self.bir_variables[index]

        return partial(invalid_input, variable=variable)(old_value)

    def get_bir_range(self, index: int, buffer=5):

        if index == 0:
            lower_boundary = 0
        else:
            lower_boundary = int(self.bir_variables[index - 1].get()) + buffer

        try:
            upper_boundary = int(self.bir_variables[index + 1].get()) - buffer
        except (ValueError, IndexError):
            upper_boundary = 4000

        return [lower_boundary, upper_boundary]

    def change_bir(self, *args, index, value, **kwargs):

        on_settings_change.send("widget", birs={str(index): value})

    def change_baseline_smoothing(self, new_value):

        on_settings_change.send("widget", baseline_smoothing=[new_value])

    def validate_smoothing(self, value):
        """
        Return False if the value is not numeric and reset the validate command if not.
        Resetting validate is neccessary, because tkinter disables validation after changing
        the variable through the invalidate command in order to stop an infinte loop.

        If the value is numerical clip it to 0, 10
        """

        var = self.baseline_smoothing_variables[-1]

        try:
            value_clipped = np.clip(float(value), 0, 100)
            var.set(value_clipped)
            self.change_baseline_smoothing(value_clipped)
            valid = True
        except ValueError:
            valid = False

        if not valid:
            # widget.after_idle(widget.config(validate="focus"))
            pass
        return valid

    def invalid_smoothing(self, old_value: str):
        old_value = old_value[: old_value.index(" ")]

        var = self.baseline_smoothing_variables[-1]
        var.set(old_value)


def make_label_widgets(
    frame, labels: List[str], names: List[str], start_indeces: List[int], variables
):

    row, column = start_indeces

    for i, (name, label) in enumerate(zip(names, labels)):
        text_label = ttk.Label(frame, text=label, width=7, font=(_font, _fontsize))
        text_label.grid(row=i + 1, sticky="nesw")

        var = tk.StringVar(name=name)
        widget = ttk.Label(
            frame,
            textvariable=var,
            anchor="e",
            background="white",
            width=8,
            font=(_font, _fontsize),
            style="TButton"
            # relief="sunken",
            # borderwidth=1,
        )
        widget.grid(
            row=i + row, column=column, sticky=("nse")  # , padx=padding, pady=padding
        )

        variables.append(var)
