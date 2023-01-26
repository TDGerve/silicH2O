from typing import Any, Dict, List, Optional, Protocol

import blinker as bl
import numpy as np
import pandas as pd
import ramCOH as ram
from scipy import interpolate as itp

from .. import app_configuration

on_display_message = bl.signal("display message")


class Sample_proccessor(Protocol):
    name: str
    settings: dict
    results: dict
    data: ram.RamanProcessing

    def calculate(self, **settings):
        ...

    def change_settings(self, **kwargs):
        ...


class Raman_processor:
    def __init__(self, name, x, y, sample_settings, birs):

        self.name = name

        self.settings = sample_settings.copy()
        self.baseline_regions = birs.copy()

        self.data = ram.RamanProcessing(
            x, y, laser=app_configuration.data_processing["laser_wavelength"]
        )

    def get_birs(self) -> Dict[str, int]:

        birs = self.baseline_regions.copy()

        birs.index = range(len(birs))
        return {f"bir_{idx}": int(value) for idx, value in birs.items()}

    def add_bir(self, index: int, max_width: int = 30):

        min_value = self.baseline_regions[f"bir_{index * 2 + 1}"]
        max_value = self.baseline_regions[f"bir_{(index + 1) * 2}"]

        max_allowed_width = (max_value - 5) - (min_value + 5)
        if max_allowed_width < 0:
            self.on_display_message(message="new bir does not fit!")
            return
        set_width = min(max_width, max_allowed_width)
        center = np.mean([max_value, min_value])

        left_boundary = center - (set_width / 2)
        right_boundary = center + (set_width / 2)

        boundary_index = index * 2
        current_boundary_amount = len(len(self.baseline_regions))

        for i in range(
            current_boundary_amount,
            boundary_index + 2,
        ):
            self.baseline_regions[f"bir_{i + 2}"] = self.baseline_regions.pop(
                f"bir_{i}"
            )

        self.baseline_regions[f"bir_{boundary_index}"] = int(left_boundary)
        self.baseline_regions[f"bir_{boundary_index + 1}"] = int(right_boundary)

    def remove_bir(self, index: int):

        current_boundary_amount = len(self.baseline_regions) // 2

        # delete region
        # self.baseline_regions.drop(str(index), inplace=True)

        for i in range(index, current_boundary_amount - 1):
            values = self.baseline_regions.loc[str(i + 1)].values
            self.baseline_regions.loc[(str(i), ["from", "to"])] = values

        # drop unused region
        self.baseline_regions.drop(self.baseline_regions.index[-2:], inplace=True)

    def set_baseline(self, kwargs) -> None:

        for bir, new_value in kwargs.items():
            if bir == "smoothing":
                self.settings["baseline_smoothing"] = new_value
                continue
            index = int(bir[-1])
            self.baseline_regions.iloc[index] = int(new_value)

    def calculate_baseline(self):
        bir_amount = self.baseline_regions.shape[0] // 2
        birs = np.reshape(self.baseline_regions.values, (bir_amount, 2))
        smooth_factor = self.settings["baseline_smoothing"]

        self.data.baselineCorrect(baseline_regions=birs, smooth_factor=smooth_factor)

    def calculate_noise(self):

        self.data.calculate_noise()

    def set_baseline_smoothing(self, value: List[float]):

        self.settings["baseline_smoothing"] = value[-1]

    def get_plotdata(self) -> Dict[str, Any]:
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


class h2o_processor(Raman_processor):
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

        self._interference: Optional[Raman_processor] = None

        self.data = ram.H2O(
            x, y, laser=app_configuration.data_processing["laser_wavelength"]
        )

    @property
    def interference(self):
        return self._interference

    def set_interference(self, x, y, sample_settings, birs):
        # y_interpolated = self._intertpolate_spectrum(x, y)
        self._interfernce = Raman_processor(
            self.name,
            x,
            y,
            sample_settings,
            birs,
        )

    def _intertpolate_spectrum(self, x, y):
        interpolate = itp.interp1d(x, y, bounds_error=False, fill_value=np.nan)
        return interpolate(self.data.x)

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
            round(i, 2) for i in (self.data.noise, self.data.Si_SNR, self.data.H2O_SNR)
        ]

    def calculate_areas(self):

        self.data.calculate_SiH2Oareas()
        self.results[["SiArea", "H2Oarea"]] = self.data.SiH2Oareas
        self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]

    def set_interpolation(self, **kwargs) -> None:

        for region, new_value in kwargs.items():
            index = int(region[-1])
            self.baseline_regions.iloc[index] = new_value

    def get_plotdata(self) -> Dict[str, Any]:

        plot_data = super().get_plotdata()

        if self.interference:
            plot_data["interference"] = self.interference.get_plotdata()

        return plot_data
