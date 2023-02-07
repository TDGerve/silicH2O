import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import List, Optional

import blinker as bl

from ... import app_configuration

on_settings_change = bl.signal("settings change")

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


def set_value_from_widget(variable, group: str, name: str):
    value = variable.get()
    on_settings_change.send("widget", **{group: {name: value}})


def make_label_widgets(
    parent,
    labels: List[str],
    names: List[str],
    start_indeces: List[int],
    variables,
    trace: Optional[callable] = None,
):

    row, column = start_indeces

    for i, (name, label) in enumerate(zip(names, labels)):
        text_label = ttk.Label(parent, text=label, width=7, font=(_font, _fontsize))
        text_label.grid(row=i + 1, column=column, sticky="esw")

        var = tk.StringVar(name=name)
        if trace is not None:
            var.trace("w", partial(trace, var=var))
        widget = ttk.Label(
            parent,
            textvariable=var,
            anchor="e",
            background="white",
            width=7,
            font=(_font, _fontsize),
            style="TButton",
            # borderwidth=1,
        )
        widget.grid(
            row=i + row,
            column=column + 1,
            sticky=("nse"),  # , padx=padding, pady=padding
        )

        variables[name] = var
