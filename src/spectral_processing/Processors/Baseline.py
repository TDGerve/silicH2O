from typing import Dict

import blinker as bl
import pandas as pd
from ramCOH import RamanProcessing

from .Interpolation_regions import Interpolation_regions

on_display_message = bl.signal("display message")


class Baseline_processor:
    def __init__(
        self,
        sample: RamanProcessing,
        interpolation_regions: pd.Series,
        smoothing: float,
    ):
        self.sample = sample
        self.smoothing = smoothing
        self.interpolation_regions = Interpolation_regions(interpolation_regions)

    def apply_settings(self, kwargs) -> None:

        smoothing = kwargs.pop("smoothing", None)
        if smoothing:
            self.smoothing = smoothing

        self.interpolation_regions.set_regions(**kwargs)

    def get_settings(self) -> Dict:

        birs = self.interpolation_regions.dictionary
        return {"smoothing": self.smoothing, **birs}

    def calculate(self) -> None:
        birs = self.interpolation_regions.nested_array
        smooth_factor = self.smoothing

        self.sample.baselineCorrect(baseline_regions=birs, smooth_factor=smooth_factor)
