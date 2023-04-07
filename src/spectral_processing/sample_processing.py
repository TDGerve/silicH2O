from typing import Any, Dict, List, Optional, Protocol, Tuple

import blinker as bl
import numpy as np
import numpy.typing as npt
import pandas as pd
import ramCOH as ram

from .Processors import (
    Baseline_processor,
    Deconvolution_processor,
    Interference_processor,
    Interpolation_processor,
)

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
    def __init__(
        self,
        name: str,
        x: npt.NDArray,
        y: npt.NDArray,
        settings: pd.Series,
        baseline_regions: pd.Series,
    ):
        self.name = name

        self.sample = ram.RamanProcessing(x, y)

        self.baseline = Baseline_processor(
            sample=self.sample,
            interpolation_regions=baseline_regions,
            settings=settings.loc["baseline"],
        )
        self.deconvolution = Deconvolution_processor(
            sample=self.sample, settings=settings.loc["deconvolution"]
        )

    @property
    def settings(self) -> pd.Series:
        settings = {
            "baseline": self.baseline.settings,
            "deconvolution": self.deconvolution.settings,
        }
        return pd.concat(settings, axis=0)

    def apply_settings(self, settings: pd.Series, groups: List[str]):
        for group in groups:
            processor = getattr(self, group)
            setattr(processor, "settings", settings.loc[group].copy())

    def get_birs(self) -> Dict[str, int]:
        return self.baseline.interpolation_regions.dictionary

    def set_baseline(self, kwargs) -> None:
        self.baseline.apply_settings(kwargs)

    def get_baseline_settings(self) -> Dict:
        return self.baseline.get_settings()

    def add_bir(self, index: int):
        self.baseline.interpolation_regions.add(index=index)

    def remove_bir(self, index: int):
        self.baseline.interpolation_regions.remove(index=index)

    def calculate_baseline(self):
        self.baseline.calculate()

    def deconvolve(self):
        self.deconvolution.calculate()

    def get_deconvolution_settings(self) -> Dict:
        return self.deconvolution.settings

    def set_deconvolution_settings(self, kwargs):
        self.deconvolution.apply_settings(kwargs)

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
            "name": self.name,
            "x": self.sample.x,
            "spectra": self.get_plot_spectra(),
            "birs": self.baseline.interpolation_regions.nested_array,  # self.get_birs(),
            "peaks": self.sample.peaks,
        }


class h2o_processor(Raman_processor):
    def __init__(
        self,
        name: str,
        x: npt.NDArray,
        y: npt.NDArray,
        settings: pd.Series,
        baseline_regions: pd.Series,
        interpolation_regions: pd.Series,
    ):
        self.name = name
        self._H2Oreference: float = np.nan

        # self.settings = settings.dropna().copy()

        self.sample = ram.Glass(x, y)

        self.baseline = Baseline_processor(
            sample=self.sample,
            interpolation_regions=baseline_regions,
            settings=settings.loc["baseline"],
        )
        self.interference = Interference_processor(
            sample=self.sample, settings=settings.loc["interference"]
        )
        self.interpolation = Interpolation_processor(
            sample=self.sample,
            regions=interpolation_regions,
            settings=settings.loc["interpolation"],
        )

        self.results = pd.Series(
            {
                data: np.nan
                for data in [
                    "SiArea",
                    "H2Oarea",
                    "rWS",
                    "noise",
                    "Si_SNR",
                    "H2O_SNR",
                    "H2O",
                ]
            }
        )

        self._interference_sample: Optional[Raman_processor] = None

        self.set_spectrum_processing()

    # @property
    # def H2Oreference(self):
    #     return self._H2Oreference

    @property
    def settings(self):
        settings = {
            "baseline": self.baseline.settings,
            "interpolation": self.interpolation.settings,
            "interference": self.interference.settings,
        }
        return pd.concat(settings, axis=0)

    @property
    def interference_sample(self):
        return self._interference_sample

    @property
    def interpolation_spectrum(self) -> str:
        return ["raw", "interference_corrected"][self.settings[("interference", "use")]]

    def set_spectrum_processing(
        self, types: Optional[str] = None, values: Optional[bool] = None
    ) -> None:
        if types is None:
            types = ["interpolated", "interference_corrected"]
            values = self.settings.loc[
                ["interpolation", "interference"], ["use", "use"]
            ].values

        self.sample._set_processing(types=types, values=values)

        for t, val in zip(types, values):
            name = {
                "interpolated": "interpolation",
                "interference_corrected": "interference",
            }[t]
            processor = getattr(self, name)
            processor.settings["use"] = bool(val)  # Make sure it is not numpy.bool_

        if len(values) > 1:
            return

        interpolated = self.sample._spectrumSelect == "interpolated"
        interference_set = types[0] == "interference_corrected"
        if interpolated & interference_set:
            self.calculate_interpolation(interference=False)

    def add_interpolation_region(self, index: int):
        self.interpolation.regions.add(index=index)

    def remove_interpolation_region(self, index):
        self.interpolation.regions.remove(index=index)

    def set_interference(self, x, y, settings, baseline_regions):
        self._interference_sample = Raman_processor(
            self.name,
            x,
            y,
            settings,
            baseline_regions,
        )

    def remove_interference(self):
        if self._interference_sample is None:
            return
        self._interference_sample = None
        self.sample.signal.remove(["interference_corrected"])
        self.settings[("interference", "use")] = False

    def get_interference_settings(self) -> Tuple[Dict, Dict]:
        subtraction_settings = self.get_subtraction_parameters()
        if self.interference_sample is None:
            return {"subtraction": subtraction_settings}

        return {
            "interference": self.interference_sample.get_baseline_settings(),
            "deconvolution": self.interference_sample.get_deconvolution_settings(),
            "subtraction": subtraction_settings,
        }

    def calculate_noise(self):
        super().calculate_noise()
        self.sample.calculate_SNR()
        self.results[["noise", "Si_SNR", "H2O_SNR"]] = [
            round(i, 2)
            for i in (self.sample.noise, self.sample.Si_SNR, self.sample.H2O_SNR)
        ]

    def calculate_areas(self):
        self.sample.calculate_SiH2Oareas()
        self.results[["SiArea", "H2Oarea"]] = self.sample.SiH2Oareas
        self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]

    def calculate_results(self):
        self.calculate_baseline()
        self.calculate_noise()
        self.calculate_areas()

    def get_interpolation_regions(self) -> Dict[str, int]:
        return self.interpolation.regions.dictionary

    def calculate_interpolation(
        self, interference: bool
    ) -> Tuple[npt.NDArray, npt.NDArray]:
        kwargs = {"spectrum": self.interpolation_spectrum}
        if interference:
            kwargs["spectrum"] = "raw"
            kwargs["add_noise"] = False
            kwargs["regions"] = [self.interference.minimisation_region]
            kwargs["smoothing"] = self.interference.settings["smoothing"]

        return self.interpolation.calculate(**kwargs)

    def get_interpolation_settings(self) -> Dict:
        return self.interpolation.get_settings()

    def set_interpolation(self, kwargs: Dict) -> None:
        self.interpolation.apply_settings(kwargs)

    def set_subtraction_parameters(self, kwargs: Dict) -> None:
        self.interference.apply_settings(**kwargs)

    def get_subtraction_parameters(self) -> Dict:
        return self.interference.get_settings()

    def subtract_interference(self) -> bool:
        return self.interference.calculate(interference=self.interference_sample.sample)

    def get_plot_spectra(self) -> Dict:
        spectra = super().get_plot_spectra()
        return {
            **{"interpolation_spectrum": spectra.get(self.interpolation_spectrum)},
            **spectra,
        }

    def get_plotdata(self) -> Dict[str, Any]:
        plotdata = super().get_plotdata()
        plotdata["subtraction_region"] = self.interference.minimisation_region
        plotdata["interpolation_regions"] = self.interpolation.regions.nested_array

        if self.interpolation.results is not None:
            plotdata["interpolated_interval"] = self.interpolation.results

        if self.interference_sample:
            plotdata["interference"] = self.interference_sample.get_plotdata()

        return plotdata
