import tkinter as tk
from typing import Dict, List, Optional, Union

import blinker as bl
import numpy as np

from ... import app_configuration

on_settings_change = bl.signal("settings change")


def validate_numerical_input(
    value: Union[str, float],
    accepted_range: List[int],
    widget,
    variable,
    dtype: Optional[callable] = None,
) -> bool:
    """
    Return False if the value is not numeric and reset the validate command if not.
    Resetting validate is neccessary, because tkinter disables validation after changing
    the variable through the invalidate command in order to stop an infinte loop.

    If the value is numerical clip it to range
    """

    try:
        new_value = np.clip(float(value), *accepted_range)
        new_value = round(new_value, 2)

        if dtype is not None:
            new_value = dtype(new_value)

        variable.set(new_value)

        widget.delete(0, tk.END)
        widget.insert(0, f"{new_value}")
        valid = True

    except ValueError:

        valid = False
        new_value = None
        widget.after_idle(lambda: widget.config(validate="focusout"))

    return valid, new_value


def validate_widget_input(
    new_value: Union[str, float],
    accepted_range: List[Union[str, float]],
    group: str,
    name: str,
    widgets: Dict,
    variables: Dict,
    dtype=None,
):
    """
    Return False if the value is not numeric and reset the validate command if not.
    Resetting validate is neccessary, because tkinter disables validation after changing
    the variable through the invalidate command in order to stop an infinte loop.

    If the value is numerical clip it to 0, 100
    """

    new_value = new_value
    widget = widgets[name]
    variable = variables[name]

    valid, new_value = validate_numerical_input(
        new_value,
        accepted_range=accepted_range,
        widget=widget,
        variable=variable,
        dtype=dtype,
    )

    if valid:
        send_new_value(new_value, group, name)

    return valid


def invalid_widget_input(self, old_value: str, name, widgets, variables):

    variable = variables[name]
    old_value = variable.get()

    widget = widgets[name]
    widget.delete(0, tk.END)
    widget.insert(0, old_value)


def send_new_value(new_value, group: str, name: str):
    on_settings_change.send("widget", **{group: {name: new_value}})
