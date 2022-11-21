import pandas as pd
import numpy as np

from typing import List, Protocol, Dict, Any

import ramCOH as ram

from .. import settings


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
    def __init__(self, name, x, y, sample_settings, birs, interpolation_regions):

        self.name = name

        self.settings = sample_settings.copy()
        self.baseline_regions = birs.copy()
        self.interpolation_regions = interpolation_regions.copy()

        self.results = pd.Series(
            {
                data: np.nan
                for data in ["SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR"]
            }
        )
        self.data = ram.H2O(x, y, laser=settings.general["laser_wavelength"])

    def get_birs(self) -> Dict[str, int]:

        birs = self.baseline_regions

        birs.index = range(len(birs))
        return dict(birs)

    def calculate_baseline(self):

        birs = np.reshape(self.baseline_regions.values, (5, 2))
        smooth_factor = self.settings["baseline_smoothing"]

        self.data.baselineCorrect(baseline_regions=birs, smooth_factor=smooth_factor)

    def calculate_interpolation(self):

        if not self.settings["interpolate"]:
            return
        amount = self.interpolation_regions.shape[0] / 2
        regions = np.reshape(self.interpolation_regions.values, (amount, 2))
        smoothing = self.settings["interpolation_smoothing"]
        self.data.interpolate(
            interpolate=regions,
            smooth_factor=smoothing,
            use=self.settings["interpolate"],
        )

    def calculate_noise(self):

        self.data.calculate_noise()
        self.data.calculate_SNR()
        self.results[["noise", "Si_SNR", "H2O_SNR"]] = [
            round(i, 1) for i in (self.data.noise, self.data.Si_SNR, self.data.H2O_SNR)
        ]

    def calculate_areas(self):

        self.data.calculate_SiH2Oareas()
        self.results[["SiArea", "H2Oarea"]] = self.data.SiH2Oareas
        self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]

    def set_birs(self, kwargs) -> None:

        for bir, new_value in kwargs.items():
            index = int(bir)
            self.baseline_regions.iloc[index] = new_value

    def set_interpolation(self, **kwargs) -> None:

        for region, new_value in kwargs.items():
            index = int(region)
            self.baseline_regions.iloc[index] = new_value

    def set_baseline_smoothing(self, value: List[float]):

        self.settings["baseline_smoothing"] = value[-1]

    def get_plot_data(self) -> Dict[str, Any]:
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
        dict
            Dictionary with baseline interpolation region boundaries
        """

        return {
            "sample_name": self.name,
            "x": self.data.x,
            "spectra": self.data.signal.all,
            "baseline_spectrum": self.data._spectrumSelect,
            "birs": self.get_birs(),
        }
