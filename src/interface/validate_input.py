import numpy as np


def validate_numerical_input(new_value, widget, variable, accepted_range):
    """
    Return False if the value is not numeric and reset the validate command if not.
    Resetting validate is neccessary, because tkinter disables validation after changing
    the variable through the invalidate command in order to stop an infinte loop.

    If the value is numerical clip it to range
    """

    new_value = new_value[: new_value.index(" ")]
    try:
        value_clipped = np.clip(
            float(new_value), a_min=accepted_range[0], a_max=accepted_range[1]
        )
        print(value_clipped)
        variable.set(int(value_clipped))
        valid = True
        print("valid")
    except ValueError:
        valid = False
        print("invalid")
    if not valid:
        pass
        # self.bell()
    widget.after_idle(lambda: widget.config(validate="focus"))
    return valid


def invalid_input(old_value, variable):
    old_value = old_value[: old_value.index(" ")]
    print(f"resetting: {old_value}")
    variable.set(int(old_value))
    pass
