import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import blinker as bl
from functools import partial

from ..vertical_toolbar import vertical_toolbar
from ...plots import Plot
from ..validate_input import validate_numerical_input, invalid_input


from ... import settings

on_settings_change = bl.signal("settings change")

_font = settings.gui["font"]["family"]
_fontsize = settings.gui["font"]["size"]


class Baseline_correction_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        super().__init__(parent, name=name, **kwargs)

        self.canvas = None

        self.bir_variables = []
        self.bir_widgets = []
        variables["birs"] = self.bir_variables
        widgets["birs"] = self.bir_widgets

        self.make_settings_frame()
        self.make_widgets()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=2, pady=2)

    def draw_plot(self, plot: Plot):
        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")

    def make_settings_frame(self):
        baseline_label = ttk.Label(
            text="Baseline interpolation regions", font=(_font, _fontsize + 2, "bold")
        )
        frame = ttk.Labelframe(self, labelwidget=baseline_label, name="settings")
        frame.grid(row=0, column=2, sticky=("nesw"))

        frame.rowconfigure(0, weight=0)
        frame.columnconfigure(0, weight=0)
        for i in [1, 2]:
            frame.columnconfigure(i, weight=2)

    def make_widgets(self):
        frame = self.nametowidget("settings")

        for k, name in zip([1, 2], ["From", "to"]):
            ttk.Label(frame, text=name, font=(_font, _fontsize)).grid(
                row=0, column=k, sticky=("sw")
            )

        for i in range(5):
            label = ttk.Label(frame, text=f"{i + 1}. ", font=(_font, _fontsize))
            label.grid(row=i + 1, column=0, sticky=("nse"))

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
                )
                entry.grid(row=i + 1, column=j + 1, sticky=("nesw"))

                self.bir_widgets.append(entry)
                self.bir_variables.append(var)

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
        variable = self.variables[index]

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

        return lower_boundary, upper_boundary

    def change_bir(self, *args, index, **kwargs):

        new_value = int(self.bir_variables[index].get())

        on_settings_change.send("bir change", birs={str(index): new_value})
