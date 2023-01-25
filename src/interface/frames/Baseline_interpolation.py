import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import Dict

import blinker as bl

from ... import app_configuration
from ..validate_input import validate_numerical_input
from .scrollframes import ScrollFrame

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

on_settings_change = bl.signal("settings change")


class Baseline_interpolation_frame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Frame,
        name: str,
        widgets: Dict,
        variables: Dict,
        bir_amount=5,
        width="7c",
    ):

        self.birs = Baseline_interpolation_regions(
            name=name, widgets=widgets, variables=variables
        )

        super().__init__(parent, name="baseline")
        # frame.grid_propagate(0)

        tk.Label(self, text="Baseline", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=("nsw")
        )

        tk.Label(
            self,
            text="Interpolation regions",
            font=(_font, _fontsize_head),
        ).grid(row=1, column=0, columnspan=2, sticky=("nsw"))

        self.make_bir_scrollframe(self, width=width, bir_amount=bir_amount)
        self.make_smoothing_widgets(self, rowstart=9)

        for i in range(2):
            self.columnconfigure(i, weight=1)

    def make_bir_scrollframe(self, parent, width, bir_amount):
        background_color = app_configuration.background_color

        scrollframe = ScrollFrame(
            parent,
            name="bir_scrollframe",
            width=width,
            background_color=background_color,
        )
        scrollframe.grid(row=3, column=0, columnspan=2, sticky="nesw")
        for k, name in zip(range(3), ["No.", "From", "to"]):
            tk.Label(
                scrollframe.headers, text=name, font=(_font, _fontsize, "italic")
            ).grid(row=0, column=k, sticky=("nsw"))
        self.make_bir_widgets(scrollframe.inner_frame, bir_amount=bir_amount)

    def make_bir_widgets(self, parent, bir_amount: int):

        for widget in parent.winfo_children():
            widget.destroy()

        for i in range(bir_amount):
            label = ttk.Label(
                parent,
                text=f"{i + 1: <4} ",
                font=(_font, _fontsize),
            )
            label.grid(row=i, column=0, sticky=("nsw"))

            for j in range(2):
                index = i * 2 + j
                var = tk.StringVar()

                entry = ttk.Entry(
                    parent,
                    validate="focusout",
                    validatecommand=(
                        parent.register(
                            partial(self.birs.validate_bir_input, index=index)
                        ),
                        r"%P %s %W",
                    ),
                    invalidcommand=(
                        parent.register(
                            partial(self.birs.invalid_bir_input, index=index)
                        ),
                        r"%s %P",
                    ),
                    width=4,
                    background="white",
                    font=(_font, _fontsize),
                    state=tk.DISABLED,
                )
                entry.grid(row=i, column=j + 1, sticky=("nesw"))

                # self.widgets[name] = entry
                # self.variables[name] = var
                self.birs.add_bir(index=index, widget=entry, variable=var)

        for i in (1, 2):
            parent.columnconfigure(i, weight=1)

        self.make_delete_add_buttons(parent, start_column=3)

    def make_delete_add_buttons(self, parent, start_column: int, width=2):

        rows = parent.grid_size()[1]
        for i in range(rows - 1):
            button = ttk.Button(
                parent,
                text="\uff0b",
                state=tk.DISABLED,
                name=f"add_bir_{i}",
                style="clean.TButton",
                width=width,
                # command=func,
            )
            button.grid(row=i, column=start_column)

        for i in range(rows - 2):
            button = ttk.Button(
                parent,
                text="\uff0d",
                state=tk.DISABLED,
                name=f"delete_bir_{i + 1}",
                style="clean.TButton",
                width=width,
                # command=func,
            )
            button.grid(row=i + 1, column=start_column + 1)

    def make_smoothing_widgets(self, parent, rowstart):

        name = "smoothing"

        ttk.Label(parent).grid(row=rowstart, column=0)  # empty row

        ttk.Label(
            parent,
            text="smoothing",
            font=(_font, _fontsize_head),
        ).grid(row=rowstart + 1, column=0, sticky=("nsw"))

        var = tk.StringVar(name=name)
        entry = ttk.Spinbox(
            parent,
            from_=0.1,
            to=100,
            increment=0.1,
            # textvariable=var,
            validate="focusout",
            validatecommand=(
                parent.register(self.birs.validate_smoothing),
                "%P",
            ),
            invalidcommand=(
                parent.register(self.birs.invalid_smoothing),
                r"%s",
            ),
            width=5,
            background="white",
            font=(_font, _fontsize),
            state=tk.DISABLED,
            name=name,
        )
        entry.grid(row=rowstart + 1, column=1, sticky=("nesw"))

        # self.widgets[name] = entry
        # self.variables[name] = var
        self.birs.add_smoothing(widget=entry, variable=var)


class Baseline_interpolation_regions:
    def __init__(self, widgets: Dict, variables: Dict, name: str):
        self.widgets = {}
        self.variables = {}

        widgets[name] = self.widgets
        variables[name] = self.variables

        self.name = name

    def add_bir(self, index: int, widget, variable):
        self.widgets[f"bir_{index}"] = widget
        self.variables[f"bir_{index}"] = variable

    def add_smoothing(self, widget, variable):
        self.widgets["smoothing"] = widget
        self.variables["smoothing"] = variable

    def validate_bir_input(self, values: str, index: int):

        new_value = values[: values.index(" ")]
        widget = self.widgets[f"bir_{index}"]
        variable = self.variables[f"bir_{index}"]

        accepted_range = self.get_bir_range(index)

        valid, new_value = validate_numerical_input(
            new_value,
            accepted_range=accepted_range,
            widget=widget,
            variable=variable,
            dtype=int,
        )

        if valid:
            self.change_bir(index=index, value=int(new_value))

        return valid

    def invalid_bir_input(self, values: str, index: int):

        variable = self.variables[f"bir_{index}"]
        old_value = variable.get()

        widget = self.widgets[f"bir_{index}"]
        widget.delete(0, tk.END)
        widget.insert(0, int(float(old_value)))

    def get_bir_range(self, index: int, buffer=5):

        if index == 0:
            lower_boundary = 0
        else:
            lower_boundary = float(self.variables[f"bir_{index - 1}"].get()) + buffer

        try:
            upper_boundary = float(self.variables[f"bir_{index + 1}"].get()) - buffer
        except (ValueError, KeyError):
            upper_boundary = 4000

        return [lower_boundary, upper_boundary]

    def change_bir(self, *args, index, value, **kwargs):

        on_settings_change.send("widget", **{self.name: {f"bir_{index}": value}})

    def change_baseline_smoothing(self, new_value):

        on_settings_change.send("widget", **{self.name: {"smoothing": new_value}})

    def validate_smoothing(self, new_value):
        """
        Return False if the value is not numeric and reset the validate command if not.
        Resetting validate is neccessary, because tkinter disables validation after changing
        the variable through the invalidate command in order to stop an infinte loop.

        If the value is numerical clip it to 0, 100
        """

        new_value = new_value
        widget = self.widgets["smoothing"]
        variable = self.variables["smoothing"]

        accepted_range = [0, 100]

        valid, new_value = validate_numerical_input(
            new_value,
            accepted_range=accepted_range,
            widget=widget,
            variable=variable,
        )

        if valid:
            self.change_baseline_smoothing(new_value)

        return valid

    def invalid_smoothing(self, old_value: str):

        variable = self.variables["smoothing"]
        old_value = variable.get()

        widget = self.widgets["smoothing"]
        widget.delete(0, tk.END)
        widget.insert(0, old_value)
