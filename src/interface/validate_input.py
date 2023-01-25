import tkinter as tk
from typing import List, Optional, Union

import numpy as np


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

        if dtype is not None:
            new_value = dtype(new_value)

        variable.set(new_value)

        widget.delete(0, tk.END)
        widget.insert(0, f"{new_value}")
        valid = True

    except ValueError:

        valid = False
        new_value = None
        widget.after_idle(lambda: widget.config(validate="focus"))

    return valid, new_value
