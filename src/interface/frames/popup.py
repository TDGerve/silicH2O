import tkinter as tk
from tkinter import ttk

import numpy as np

from .. import app_configuration
from ..widgets.validate_input import validate_numerical_input

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]


class popup_window(object):
    def __init__(self, parent, text: str, init_val: float):
        top = self.top = tk.Toplevel(parent)
        ttk.Label(top, text=text).pack()

        self.var = tk.StringVar(value=init_val)

        self.entry = ttk.Entry(
            top,
            validate="focusout",
            validatecommand=(top.register(self.validate), r"%P %s %W"),
            invalidcommand=(top.register(self.invalid), r"%s %P"),
            width=4,
            background="white",
            font=(_font, _fontsize),
        )
        self.entry.insert(0, self.var.get())
        self.entry.pack()

        ttk.Button(top, text="Ok", command=self.cleanup).pack()

    def cleanup(self):
        self.value = self.entry.get()
        self.top.destroy()

    def validate(self, values: str):
        new_value = values[: values.index(" ")]

        valid, new_value = validate_numerical_input(
            new_value,
            accepted_range=[0, np.inf],
            widget=self.entry,
            variable=self.var,
            dtype=float,
        )

        if valid:
            ...

        return valid

    def invalid(self, values: str):

        old_value = self.var.get()

        self.entry.delete(0, tk.END)
        self.entry.insert(0, int(float(old_value)))
