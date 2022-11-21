import numpy as np
from typing import Union, List


def validate_numerical_input(
    new_value: Union[str, float], accepted_range: List[int], widget, variable
) -> bool:
    """
    Return False if the value is not numeric and reset the validate command if not.
    Resetting validate is neccessary, because tkinter disables validation after changing
    the variable through the invalidate command in order to stop an infinte loop.

    If the value is numerical clip it to range
    """

    try:
        value_clipped = np.clip(float(new_value), *accepted_range)

        variable.set(int(value_clipped))
        valid = True

    except ValueError:
        valid = False

        widget.after_idle(lambda: widget.config(validate="focus"))

    return valid, value_clipped


def invalid_input(old_value: Union[str, float], variable) -> None:

    variable.set(int(old_value))
