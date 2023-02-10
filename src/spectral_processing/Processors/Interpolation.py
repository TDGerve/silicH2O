from typing import Dict, Optional

import blinker as bl
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
    ):
        self.sample = sample
        self.regions = Interpolation_regions(regions)
        self.settings = settings

        self.results = None

    def apply_settings(self, kwargs) -> None:

        for name in ("smoothing", "use"):
            val = kwargs.pop(name, None)
            if val is None:
                continue
            self.settings[name] = val

        self.regions.set(**kwargs)

    def get_settings(self) -> Dict:
        settings = {
            "smoothing": self.settings["smoothing"],
            "use": self.settings["use"],
        }
        regions = self.regions.dictionary

        return {**settings, **regions}

    def calculate(
        self,
        spectrum: str,
        add_noise: bool = True,
        regions: Optional[npt.NDArray] = None,
        **kwargs
    ) -> None:

        settings = self._get_parameters(regions=regions)
        smoothing = kwargs.pop("smoothing", settings.pop("smooth_factor"))

        self.results = self.sample.interpolate(
            **settings,
            add_noise=add_noise,
            smooth_factor=smoothing,
            y=spectrum,
            output=True,
        )

    def _get_parameters(self, regions: Optional[npt.NDArray] = None) -> Dict:

        return {
            "interpolate": self.regions.nested_array if regions is None else regions,
            "smooth_factor": self.settings["smoothing"],
            "use": self.settings["use"],
        }
