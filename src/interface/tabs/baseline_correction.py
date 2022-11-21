import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl
from functools import partial

from ..vertical_toolbar import vertical_toolbar
from ...plots import Baseline_correction_plot
from ..validate_input import validate_numerical_input, invalid_input


from ... import settings

on_settings_change = bl.signal("settings change")

_font = settings.gui["font"]["family"]
_fontsize = settings.gui["font"]["size"]
_fontsize_head = _fontsize


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.bir_variables = []
        self.bir_widgets = []

        self.areas_variables = []
        self.signal_variables = []

        variables["birs"] = self.bir_variables
        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables

        widgets["birs"] = self.bir_widgets

        self.make_bir_frame()
        self.make_areas_frame()
        self.make_signal_frame()
        self.make_dividers()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=2)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=3, pady=3)

    def make_dividers(self):

        ttk.Separator(self, orient=tk.VERTICAL).grid(
            row=0, column=2, rowspan=6, sticky=("ns")
        )

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=3, sticky=("nesw"))
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, column=3, sticky=("new"))

    def draw_plot(self, plot: Baseline_correction_plot):
        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=6, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

    def make_bir_frame(self):

        # baseline_label =
        frame = ttk.Frame(self, name="birs")
        frame.grid(row=0, column=3, sticky=("nesw"))

        # frame.rowconfigure(0, weight=0)

        for i in range(7):
            frame.rowconfigure(i, weight=1)
        frame.columnconfigure(0, weight=0)
        for i in [1, 2]:
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Baseline interpolation regions",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky=("nsw"))

        self.make_bir_widgets(frame)

    def make_bir_widgets(self, frame):

        for k, name in zip([1, 2], ["From", "to"]):
            ttk.Label(frame, text=name, font=(_font, _fontsize)).grid(
                row=1, column=k, sticky=("nsw")
            )

        for i in range(5):
            label = ttk.Label(frame, text=f"{i + 1}. ", font=(_font, _fontsize))
            label.grid(row=i + 2, column=0, sticky=("nsw"))

            for j in range(2):
                var = tk.StringVar()
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    validate="focus",
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
                    relief="sunken",
                    borderwidth=1,
                )
                entry.grid(row=i + 2, column=j + 1, sticky=("nesw"))

                self.bir_widgets.append(entry)
                self.bir_variables.append(var)

    def make_areas_frame(self):

        frame = ttk.Frame(self, name="areas")
        frame.grid(row=2, column=3, sticky=("nesw"))

        for i in range(4):
            frame.rowconfigure(i, weight=1)
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Areas",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=("nsw"))

        labels = ["Silicate", "H\u2082O", "H\u2082O:silicate"]
        names = ["Silicate", "H2O", "H2OSi"]

        make_label_widgets(frame, labels, names, self.areas_variables)

    def make_signal_frame(self):

        frame = ttk.Frame(self, name="signal")
        frame.grid(row=4, column=3, sticky=("nesw"))

        for i in range(4):
            frame.rowconfigure(i, weight=1)
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(
            frame,
            text="Signal",
            font=(_font, _fontsize_head, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=("nsw"))

        labels = ["noise", "Silicate S:N", "H\u2082O S:N"]
        names = ["noise", "Si_SNR", "H2O_SNR"]

        make_label_widgets(frame, labels, names, self.signal_variables)

    def validate_bir_input(self, new_value: str, index: int):

        new_value = new_value[: new_value.index(" ")]
        widget = self.bir_widgets[index]
        variable = self.bir_variables[index]

        accepted_range = self.get_bir_range(index)

        if validate_numerical_input(
            new_value,
            accepted_range=accepted_range,
            widget=widget,
            variable=variable,
        ):
            self.change_bir(index=index)
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

    def change_bir(self, *args, index, **kwargs):

        new_value = int(self.bir_variables[index].get())

        on_settings_change.send("bir change", birs={str(index): new_value})


def make_label_widgets(frame, labels, names, variables):

    for i, (name, label) in enumerate(zip(names, labels)):
        text_label = ttk.Label(frame, text=label, width=7, font=(_font, _fontsize))
        text_label.grid(row=i + 1, sticky="nesw")

        var = tk.StringVar(name=name)
        widget = ttk.Label(
            frame,
            textvariable=var,
            anchor="se",
            background="white",
            width=10,
            font=(_font, _fontsize),
            padding=1,
            relief="sunken",
            borderwidth=1,
        )
        widget.grid(row=i + 1, column=1, sticky=("nse"))

        variables.append(var)
