import pandas as pd
import numpy as np

import os, ast
from typing import List, Protocol, Tuple, Dict
import blinker as bl

import ramCOH as ram

from . import settings


class Sample_proccessor(Protocol):
    name: str
    settings: dict
    results: dict
    data: ram.RamanProcessing

    def calculate(self, **settings):
        ...

    def change_settings(self, **kwargs):
        ...


class h2o_processor:
    def __init__(self, name, x, y):
        self.name = name
        self.settings = settings.process.copy()

        self.results = pd.Series(
            {data: np.nan for data in ["SiArea", "H2Oarea", "rWS"]}
        )
        self.data = ram.H2O(x, y, laser=settings.general["laser_wavelength"])

    def calculate(self) -> None:

        self.calculate_interpolation()
        self.data.baselineCorrect(baseline_regions=self.construct_birs())
        self.data.calculate_SiH2Oareas()
        self.results[["SiArea", "H2Oarea"]] = self.data.SiH2Oareas
        self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]

    def calculate_interpolation(self):

        if not self.settings[("interpolate", "use")]:
            return
        region = self.settings[("interpolate", "region")]
        smoothing = self.settings[("interpolate", "smoothing")]
        self.data.interpolate(interpolate=region, smooth_factor=smoothing)

    def construct_birs(self) -> List[List[int]]:
        return [bir for bir in self.settings["birs"]]

    def set_birs(self, **kwargs) -> None:
        for bir, (position, new_value) in kwargs.items():
            old_values = self.settings[("birs", bir)]
            old_values[position] = new_value

    def set_interpolation(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self.settings[("interpolate", key)] = value

    def change_settings(self, birs: dict = None, interpolate: dict = None) -> None:
        if birs is not None:

            self.set_birs(**birs)
        if interpolate is None:
            return
        self.set_interpolation(interpolate)

    def retrieve_plot_data(self) -> Tuple[str, np.ndarray, Dict[str, np.ndarray], str]:
        """
        Returns
        -------
        str
            Sample name
        np.ndarray
            x axis
        dict
            Dictionary with all caclulated spectra
        str
            Name of the spectrum used for baseline correction
        """
        return self.name, self.data.x, self.data.signal.all, self.data._spectrumSelect
