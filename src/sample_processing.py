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
    def __init__(self, name, x, y, process_settings):
        self.name = name
        self.settings = process_settings.copy()

        self.results = pd.Series(
            {data: np.nan for data in ["SiArea", "H2Oarea", "rWS"]}
        )
        self.data = ram.H2O(x, y, laser=settings.general["laser_wavelength"])

    @property
    def birs(self) -> List[List[int]]:
        return [list(bir[1]) for bir in self.settings.groupby(level=0)]

    def calculate(self) -> None:
        print("calculating sample")
        print(self.birs)
        self.calculate_interpolation()
        self.data.baselineCorrect(baseline_regions=self.birs)
        self.data.calculate_SiH2Oareas()
        self.results[["SiArea", "H2Oarea"]] = self.data.SiH2Oareas
        self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]
        print("calculated")

    def calculate_interpolation(self):

        if True:  # not self.settings[("interpolate", "use")]:
            return
        region = self.settings[("interpolate", "region")]
        smoothing = self.settings[("interpolate", "smoothing")]
        self.data.interpolate(interpolate=region, smooth_factor=smoothing)

    def set_birs(self, **kwargs) -> None:
        for bir, (position, new_value) in kwargs.items():
            int_index = int(bir) * 2 + position
            self.settings.iloc[int_index] = new_value

    def set_interpolation(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self.settings[("interpolate", key)] = value

    def change_settings(self, birs: dict = None, interpolate: dict = None) -> None:
        if birs is not None:

            self.set_birs(**birs)
        if interpolate is None:
            return
        self.set_interpolation(interpolate)

    def retrieve_plot_data(self) -> Dict[str, any]:
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
        return {
            "sample_name": self.name,
            "x": self.data.x,
            "spectra": self.data.signal.all,
            "baseline_spectrum": self.data._spectrumSelect,
            "birs": self.birs,
        }
