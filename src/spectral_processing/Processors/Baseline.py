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
        settings: pd.Series,
    ):
        self.sample = sample
        self.settings = settings
        self.interpolation_regions = Interpolation_regions(interpolation_regions)

    def apply_settings(self, kwargs) -> None:

        smoothing = kwargs.pop("smoothing", None)
        if smoothing:
            self.settings["smoothing"] = smoothing

        self.interpolation_regions.set(**kwargs)

    def get_settings(self) -> Dict:

        birs = self.interpolation_regions.dictionary
        return {"smoothing": self.settings["smoothing"], **birs}

    def calculate(self) -> None:
        birs = self.interpolation_regions.nested_array
        smooth_factor = self.settings["smoothing"]

        self.sample.baselineCorrect(baseline_regions=birs, smooth_factor=smooth_factor)
