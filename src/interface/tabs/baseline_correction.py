import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import List, Optional

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_settings
from ...plots import Baseline_correction_plot
from ..scrollframes import ScrollFrame
from ..validate_input import validate_numerical_input
from ..vertical_toolbar import vertical_toolbar

on_settings_change = bl.signal("settings change")

_font = app_settings.gui["font"]["family"]
_fontsize = app_settings.gui["font"]["size"]
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
        variables["baseline"] = self.baseline_variables
        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables

        self.make_baseline_frame(0, 3, width="7c")
        self.make_signal_frame(2, 3)
        self.make_areas_frame(4, 3)
        # self.make_save_frame(7, 3)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(3, minsize="6c")

        self.rowconfigure(6, weight=1)

        self.make_vertical_divider(self, col=2)
        self.make_horizontal_dividers(self, rows=[1, 3, 5], col=3)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=3)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=padding, pady=padding)

    def make_vertical_divider(self, frame, col):
        rows = frame.grid_size()[1]
        ttk.Separator(self, orient=tk.VERTICAL).grid(
            row=0, column=col, rowspan=rows, sticky=("ns")
        )

    def make_horizontal_dividers(self, frame, rows: List[int], col: int):
        for row in rows:
            ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
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

    def make_baseline_frame(self, row: int, col: int, width):

        frame = ttk.Frame(self, name="baseline")
        frame.grid(row=row, column=col, sticky=("nesw"))
        # frame.grid_propagate(0)

        tk.Label(frame, text="Baseline", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=("nsw")
        )

        tk.Label(
            frame,
            text="Interpolation regions",
            font=(_font, _fontsize_head),
        ).grid(row=1, column=0, columnspan=2, sticky=("nsw"))

        self.make_bir_scrollframe(frame, width=width)
        self.make_smoothing_widgets(frame, rowstart=9)

        for i in range(2):
            frame.columnconfigure(i, weight=1)

    def make_bir_scrollframe(self, frame, width):
        background_color = app_settings.background_color

        scrollframe = ScrollFrame(
            frame,
            name="bir_scrollframe",
            width=width,
            background_color=background_color,
        )
        scrollframe.grid(row=3, column=0, columnspan=2, sticky="nesw")
        for k, name in zip(range(3), ["No.", "From", "to"]):
            tk.Label(
                scrollframe.headers, text=name, font=(_font, _fontsize, "italic")
            ).grid(row=0, column=k, sticky=("nsw"))
        self.make_bir_widgets(scrollframe.inner_frame, bir_amount=5)

    def make_bir_widgets(self, bir_frame, bir_amount: int):

        for widget in bir_frame.winfo_children():
            widget.destroy()

        for i in range(bir_amount):
            label = ttk.Label(
                bir_frame,
                text=f"{i + 1: <4} ",
                font=(_font, _fontsize),
            )
            label.grid(row=i, column=0, sticky=("nsw"))

            for j in range(2):
                name = f"bir_{i * 2 + j}"
                var = tk.StringVar(name=name)

                entry = ttk.Entry(
                    bir_frame,
                    validate="focusout",
                    validatecommand=(
                        self.register(
                            partial(self.validate_bir_input, index=i * 2 + j)
                        ),
                        r"%P %s %W",
                    ),
                    invalidcommand=(
                        self.register(partial(self.invalid_bir_input, index=i * 2 + j)),
                        r"%s %P",
                    ),
                    width=4,
                    background="white",
                    font=(_font, _fontsize),
                    state=tk.DISABLED,
                    name=name,
                )
                entry.grid(row=i, column=j + 1, sticky=("nesw"))

                self.baseline_widgets[name] = entry
                self.baseline_variables[name] = var

        for i in (1, 2):
            bir_frame.columnconfigure(i, weight=1)

        self.make_delete_add_buttons(bir_frame, start_column=3)

    def make_delete_add_buttons(self, frame, start_column: int, width=2):

        rows = frame.grid_size()[1]
        for i in range(rows - 1):
            button = ttk.Button(
                frame,
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
                frame,
                text="\uff0d",
                state=tk.DISABLED,
                name=f"delete_bir_{i + 1}",
                style="clean.TButton",
                width=width,
                # command=func,
            )
            button.grid(row=i + 1, column=start_column + 1)

    def make_smoothing_widgets(self, frame, rowstart):

        name = "smoothing"

        ttk.Label(frame).grid(row=rowstart, column=0)  # empty row

        ttk.Label(
            frame,
            text="smoothing",
            font=(_font, _fontsize_head),
        ).grid(row=rowstart + 1, column=0, sticky=("nsw"))

        var = tk.StringVar(name=name)
        entry = ttk.Spinbox(
            frame,
            from_=0.1,
            to=100,
            increment=0.1,
            # textvariable=var,
            validate="focusout",
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
            name=name,
        )
        entry.grid(row=rowstart + 1, column=1, sticky=("nesw"))

        self.baseline_widgets[name] = entry
        self.baseline_variables[name] = var

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
        names = ["silicate", "H2O", "H2OSi"]

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

    def validate_bir_input(self, values: str, index: int):

        new_value = values[: values.index(" ")]
        widget = self.baseline_widgets[f"bir_{index}"]
        variable = self.baseline_variables[f"bir_{index}"]

        accepted_range = self.get_bir_range(index)

        valid, new_value = validate_numerical_input(
            new_value,
            accepted_range=accepted_range,
            widget=widget,
            variable=variable,
            dtype=int,
        )

        if valid:
            self.change_bir(index=index, value=new_value)

        return valid

    def invalid_bir_input(self, values: str, index: int):

        # old_value = values[: values.index(" ")]
        variable = self.baseline_variables[f"bir_{index}"]
        old_value = variable.get()

        widget = self.baseline_widgets[f"bir_{index}"]
        widget.delete(0, tk.END)
        widget.insert(0, f"{int(old_value)}")

        # return partial(invalid_input, variable=variable)(old_value)

    def get_bir_range(self, index: int, buffer=5):

        if index == 0:
            lower_boundary = 0
        else:
            lower_boundary = (
                int(self.baseline_variables[f"bir_{index - 1}"].get()) + buffer
            )

        try:
            upper_boundary = (
                int(self.baseline_variables[f"bir_{index + 1}"].get()) - buffer
            )
        except (ValueError, KeyError):
            upper_boundary = 4000

        return [lower_boundary, upper_boundary]

    def change_bir(self, *args, index, value, **kwargs):

        on_settings_change.send("widget", baseline={f"bir_{index}": value})

    def change_baseline_smoothing(self, new_value):

        on_settings_change.send("widget", baseline={"smoothing": new_value})

    def validate_smoothing(self, new_value):
        """
        Return False if the value is not numeric and reset the validate command if not.
        Resetting validate is neccessary, because tkinter disables validation after changing
        the variable through the invalidate command in order to stop an infinte loop.

        If the value is numerical clip it to 0, 100
        """

        new_value = new_value
        widget = self.baseline_widgets["smoothing"]
        variable = self.baseline_variables["smoothing"]

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
        # old_value = old_value[: old_value.index(" ")]

        # var = self.baseline_smoothing_variables[-1]
        # var.set(old_value)

        variable = self.baseline_variables["smoothing"]
        old_value = variable.get()

        widget = self.baseline_widgets["smoothing"]
        widget.delete(0, tk.END)
        widget.insert(0, f"{old_value}")


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
