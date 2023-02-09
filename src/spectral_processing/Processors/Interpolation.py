from typing import Dict

import blinker as bl
import numpy as np
import numpy.typing as npt
import pandas as pd
from ramCOH import RamanProcessing

from .Interpolation_regions import Interpolation_regions

on_display_message = bl.signal("display message")


class Interpolation_processor:
    def __init__(
        self,
        sample: RamanProcessing,
        regions: pd.Series,
        settings: pd.Series,
        add_noise: bool,
    ):
        self.sample = sample
        self.regions = Interpolation_regions(regions)
        self.settings = settings
        self.add_noise = add_noise

    def apply_settings(self, kwargs) -> None:

        for name in ("smoothing", "use"):
            val = kwargs.pop(name, None)
            if val is None:
                continue
            self.settings[name] = val

        self.regions.set_regions(**kwargs)

    def get_settings(self) -> Dict:
        settings = {
            "smoothing": self.settings["smoothing"],
            "use": self.settings["use"],
        }
        regions = self.regions.dictionary

        return {**settings, **regions}

    def calculate(self, spectrum, add_noise) -> npt.NDArray:

        settings = self._get_parameters()

        return self.data.interpolate(
            **settings,
            add_noise=add_noise,
            y=spectrum,
            output=True,
        )

    def _get_parameters(self):

        return {
            "interpolate": self.regions.nested_array,
            "smooth_factor": self.settings["smoothing"],
            "add_noise": self.add_noise,
            "use": self.settings["use"],
        }
