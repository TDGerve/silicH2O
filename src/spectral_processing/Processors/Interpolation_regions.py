from typing import Dict

import blinker as bl
import numpy as np
import numpy.typing as npt
import pandas as pd

on_display_message = bl.signal("display message")


class Interpolation_regions:
    def __init__(self, regions: pd.Series):
        self._regions = regions

    @property
    def amount(self) -> int:
        len(self._regions) // 2

    @property
    def dictionary(self) -> Dict:
        return {
            f"bir_{idx:02d}": int(value)
            for idx, value in enumerate(self._regions.values())
        }

    @property
    def series(self) -> pd.Series:
        return self._regions

    @property
    def nested_array(self) -> npt.NDArray:
        return np.reshape(self._regions.values, (self.amount, 2))

    def set_regions(self, **kwargs):
        for bir, new_value in kwargs.items():
            if "bir" not in bir:
                continue
            index = int(bir[-2:])
            i = index // 2
            j = ["from", "to"][index % 2]
            self._regions.loc[(str(i), j)] = int(new_value)

    def add_region(self, index: int, max_width: int = 30) -> None:
        min_value = self._regions.loc[str(index)].values[1]
        max_value = self._regions.loc[str(index + 1)].values[0]

        max_allowed_width = (max_value - 5) - (min_value + 5)
        if max_allowed_width < 0:
            on_display_message(message="new bir does not fit!")
            return
        set_width = min(max_width, max_allowed_width)
        center = np.mean([max_value, min_value])

        left_boundary = center - (set_width / 2)
        right_boundary = center + (set_width / 2)

        for i in reversed(range(index + 1, self.amount)):
            values = self._regions.loc[str(i)].values
            self._regions.loc[(str(i + 1), "from")] = values[0]
            self._regions.loc[(str(i + 1), "to")] = values[1]

        self._regions.loc[(str(index + 1))] = (
            int(left_boundary),
            int(right_boundary),
        )

    def remove_region(self, index: int) -> None:

        for i in range(index, self.amount - 1):
            values = self._regions.loc[str(i + 1)].values
            self._regions.loc[(str(i), ["from", "to"])] = values

        # drop unused region
        self._regions.drop(self._regions.index[-2:], inplace=True)
