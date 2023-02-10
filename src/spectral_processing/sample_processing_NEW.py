from typing import Any, Dict, List, Optional, Protocol, Tuple

import blinker as bl
import numpy as np
import numpy.typing as npt
import pandas as pd
import ramCOH as ram

from .. import app_configuration
from .Processors import Baseline_processor, Deconvolution_processor

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
    def __init__(self, name, x, y, settings, baseline_regions):

        self.name = name

        self.settings = settings.dropna().copy()

        self.sample = ram.RamanProcessing(
            x, y, laser=app_configuration.data_processing["laser_wavelength"]
        )

        self.baseline = Baseline_processor(
            sample=self.sample,
            interpolation_regions=baseline_regions,
            settings=self.settings["baseline"],
        )
        self.deconvolution = Deconvolution_processor(
            sample=self.sample, settings=self.settings["deconvolution"]
        )

    def get_birs(self) -> Dict[str, int]:

        return self.baseline.interpolation_regions.dictionary

    def set_baseline(self, kwargs) -> None:

        self.baseline.apply_settings(kwargs)

    def get_baseline_settings(self) -> Dict:

        return self.baseline.get_settings()

    def add_bir(self, index: int, max_width: int = 30):

        self.baseline.interpolation_regions.add(index=index, max_width=max_width)

    def remove_bir(self, index: int):

        self.baseline.interpolation_regions.remove(index=index)

    def calculate_baseline(self):
        self.baseline.calculate()

    def deconvolve(self):

        self.deconvolution.calculate()

    def calculate_noise(self):

        self.sample.calculate_noise()

    def _set_parameters(self, group: str, parameters: Dict, names: List[str]) -> None:

        for name in names:
            value = parameters.pop(name, None)
            if value is not None:
                self.settings[(group, name)] = value

    def get_plot_spectra(self) -> Dict:
        spectra = self.sample.signal.all
        return {
            **{"baseline_spectrum": spectra.get(self.sample._spectrumSelect)},
            **spectra,
        }

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
            "x": self.sample.x,
            "spectra": self.get_plot_spectra(),
            "birs": self.get_birs(),
            "peaks": self.sample.peaks,
        }


class h2o_processor(Raman_processor):
    def __init__(self, name, x, y, sample_settings, birs, interpolation_regions):

        self.name = name

        # self.interpolation = Interpolation_processor()
        # self.interference = Interference_processor()

        self.settings = sample_settings.dropna().copy()
        self.baseline_regions = birs.dropna().copy()
        self.interpolation_regions = interpolation_regions.dropna().copy()

        self.results = pd.Series(
            {
                data: np.nan
                for data in ["SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR"]
            }
        )

        self._interference: Optional[Raman_processor] = None
        self.interpolated_interval: Optional[Tuple[npt.NDArray, npt.NDArray]] = None

        self.data = ram.H2O(
            x, y, laser=app_configuration.data_processing["laser_wavelength"]
        )

        self.set_spectrum_processing()

    def set_spectrum_processing(
        self, types: Optional[str] = None, values: Optional[bool] = None
    ) -> None:
        if types is None:
            types = ["interpolated", "interference_corrected"]
            values = self.settings.loc[
                ["interpolation", "interference"], ["use", "use"]
            ].values
            # values = [eval(val) for val in values]

        self.data._set_processing(types=types, values=values)

    @property
    def interference(self):
        return self._interference

    @property
    def interpolation_spectrum(self) -> str:
        return ["raw", "interference_corrected"][self.settings[("interference", "use")]]

    def set_interference(self, x, y, sample_settings, birs):
        # y_interpolated = self._intertpolate_spectrum(x, y)
        self._interference = Raman_processor(
            self.name,
            x,
            y,
            sample_settings,
            birs,
        )

    def remove_interference(self):
        if self._interference is None:
            return
        self._interference = None
        self.data.signal.remove(["interference_corrected"])
        self.settings[("interference", "use")] = False

    def get_interference_settings(self) -> Tuple[Dict, Dict]:
        subtraction_settings = self.get_subtraction_parameters()
        if self.interference is None:
            return {"subtraction": subtraction_settings}

        return {
            "interference": self.interference.get_baseline_settings(),
            "deconvolution": self.interference.get_deconvolution_settings(),
            "subtraction": subtraction_settings,
        }

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

    def get_interpolation_regions(self) -> Dict[str, int]:

        birs = self.interpolation_regions.copy()

        birs.index = range(len(birs))
        return {f"bir_{idx:02d}": int(value) for idx, value in birs.items()}

    def calculate_interpolation(self, tab: str):

        settings = self.get_interpolation_parameters(tab=tab)

        self.interpolated_interval = self.data.interpolate(
            **settings,
            output=True,
        )

    def get_glass_interpolation_parameters(self):
        regions = self.interpolation_regions.values
        amount = len(regions) // 2
        regions = np.reshape(regions, (amount, 2))

        return {
            "interpolate": regions,
            "smooth_factor": self.settings[("interpolation", "smoothing")],
            "add_noise": True,
            "use": self.settings[("interpolate", "use")],
            "y": self.interpolation_spectrum,
        }

    def get_interference_interpolation_parameters(self):
        return {
            "interpolate": np.array([self.get_subtraction_region()]),
            "smooth_factor": self.settings[("interference", "smoothing")],
            "use": False,
            "add_noise": False,
            "y": "raw",
        }

    def get_interpolation_parameters(self, tab: str):

        get_parameters = {
            "interpolation": self.get_glass_interpolation_parameters,
            "interference": self.get_interference_interpolation_parameters,
        }[tab]
        return get_parameters()

    def get_interpolation_settings(self) -> Dict:
        settings = {
            "smoothing": self.settings[("interpolation", "smoothing")],
            "use": self.settings[("interpolation", "use")],
        }
        return {**self.get_interpolation_regions(), **settings}

    def set_interpolation(self, kwargs: Dict) -> None:

        for name in ("smoothing", "use"):
            val = kwargs.pop(name, None)
            if val is None:
                continue
            self.settings[("interpolation", name)] = val

        for bir, new_value in kwargs.items():
            if "bir" not in bir:
                continue
            index = int(bir[-2:])
            i = index // 2
            j = ["from", "to"][index % 2]
            self.interpolation_regions.loc[(str(i), j)] = int(new_value)

    def set_subtraction_parameters(self, kwargs: Dict):
        names = ("smoothing", "spectrum", "use")
        self._set_parameters(group="interference", parameters=kwargs, names=names)

        for ID, new_value in kwargs.items():
            location = ["left", "right"][int(ID[-2:]) % 2]
            self.settings[("interference", f"boundary_{location}")] = new_value

    def get_subtraction_region(self):
        return self.settings.loc[
            (["interference"], ["boundary_left", "boundary_right"])
        ].values

    def get_subtraction_parameters(self):
        boundary_left, boundary_right = self.get_subtraction_region()
        return {
            "bir_00": boundary_left,
            "bir_01": boundary_right,
            "smoothing": self.settings[("interference", "smoothing")],
            "spectrum": self.settings[("interference", "spectrum")],
            "use": self.settings[("interference", "use")],
        }

    def get_interference_spectrum(self):

        spectrum_name = self.settings[("interference", "spectrum")]
        interference = self.interference

        spectrum = interference.data.signal.get(spectrum_name)
        if spectrum is None:
            return None

        return self.data.signal.interpolate_spectrum(
            old_x=interference.data.signal.x,
            old_y=spectrum,
        )

    def subtract_interference(self) -> bool:

        interference = self.get_interference_spectrum()
        if interference is None:
            on_display_message.send(message="interference not found", duration=5)
            return False

        settings = self.get_subtraction_parameters()
        settings["interval"] = [settings.pop(key) for key in ("bir_00", "bir_01")]

        self.data.subtract_interference(interference=interference, **settings)
        return True

    def get_plot_spectra(self) -> Dict:
        spectra = super().get_plot_spectra()
        return {
            **{"interpolation_spectrum": spectra.get(self.interpolation_spectrum)},
            **spectra,
        }

    def get_plotdata(self) -> Dict[str, Any]:

        plotdata = super().get_plotdata()
        plotdata["subtraction_region"] = self.get_subtraction_region()
        # plotdata["interpolation_regions"] = self.get_interpolation_settings()["regions"]

        if self.interpolated_interval is not None:
            plotdata["interpolated_interval"] = self.interpolated_interval

        if self.interference:
            plotdata["interference"] = self.interference.get_plotdata()

        return plotdata
