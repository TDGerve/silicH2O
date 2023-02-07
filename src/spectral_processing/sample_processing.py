from typing import Any, Dict, List, Optional, Protocol, Tuple

import blinker as bl
import numpy as np
import numpy.typing as npt
import pandas as pd
import ramCOH as ram

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

        self.settings = sample_settings.dropna().copy()
        self.baseline_regions = birs.dropna().copy()

        self.data = ram.RamanProcessing(
            x, y, laser=app_configuration.data_processing["laser_wavelength"]
        )

    def set_spectrum_processing(self, spectrum: str, value: bool) -> None:
        self.data._set_processing(spectrum=spectrum, value=value)

    def get_birs(self) -> Dict[str, int]:

        birs = self.baseline_regions.copy()

        birs.index = range(len(birs))
        return {f"bir_{idx:02d}": int(value) for idx, value in birs.items()}

    def set_baseline(self, kwargs) -> None:

        smoothing = kwargs.get("smoothing", None)
        if smoothing:
            self.settings[("baseline", "smoothing")] = smoothing

        for bir, new_value in kwargs.items():
            if "bir" not in bir:
                continue
            index = int(bir[-2:])
            i = index // 2
            j = ["from", "to"][index % 2]
            self.baseline_regions.loc[(str(i), j)] = int(new_value)

    def get_baseline_settings(self):
        baseline_settings = self.settings[("baseline")].to_dict()
        birs = self.get_birs()
        return {**baseline_settings, **birs}

    def add_bir(self, index: int, max_width: int = 30):

        min_value = self.baseline_regions.loc[str(index)].values[1]
        max_value = self.baseline_regions.loc[str(index + 1)].values[0]

        max_allowed_width = (max_value - 5) - (min_value + 5)
        if max_allowed_width < 0:
            self.on_display_message(message="new bir does not fit!")
            return
        set_width = min(max_width, max_allowed_width)
        center = np.mean([max_value, min_value])

        left_boundary = center - (set_width / 2)
        right_boundary = center + (set_width / 2)

        current_boundary_amount = len(self.baseline_regions) // 2

        for i in reversed(range(index + 1, current_boundary_amount)):
            values = self.baseline_regions.loc[str(i)].values
            self.baseline_regions.loc[(str(i + 1), "from")] = values[0]
            self.baseline_regions.loc[(str(i + 1), "to")] = values[1]

        self.baseline_regions.loc[(str(index + 1))] = (
            int(left_boundary),
            int(right_boundary),
        )

    def remove_bir(self, index: int):

        current_boundary_amount = len(self.baseline_regions) // 2

        for i in range(index, current_boundary_amount - 1):
            values = self.baseline_regions.loc[str(i + 1)].values
            self.baseline_regions.loc[(str(i), ["from", "to"])] = values

        # drop unused region
        self.baseline_regions.drop(self.baseline_regions.index[-2:], inplace=True)

    def calculate_baseline(self):
        bir_amount = self.baseline_regions.shape[0] // 2
        birs = np.reshape(self.baseline_regions.values, (bir_amount, 2))
        smooth_factor = self.settings[("baseline", "smoothing")]

        self.data.baselineCorrect(baseline_regions=birs, smooth_factor=smooth_factor)

    def deconvolve(self):
        if self.data.noise is None:
            self.data.calculate_noise()

        settings = self.get_deconvolution_settings()
        default_settings = {
            "baseline0": True,
        }

        self.data.deconvolve(
            y="baseline_corrected",
            noise=self.data.noise,
            **settings,
            **default_settings,
        )

    def get_deconvolution_settings(self):

        settings = self.settings[("deconvolution")]
        return settings.to_dict()

    def set_deconvolution_settings(self, kwargs):
        for key, value in kwargs.items():
            self.settings[("deconvolution", key)] = value

    def calculate_noise(self):

        self.data.calculate_noise()

    def _set_parameters(self, group: str, parameters: Dict, names: List[str]) -> None:

        for name in names:
            value = parameters.pop(name, None)
            if value is not None:
                self.settings[(group, name)] = value

    def get_plot_spectra(self):
        spectra = {"baseline_spectrum": None}
        spectra = {**spectra, **self.data.signal.all}
        spectra["baseline_spectrum"] = spectra.get(self.data._spectrumSelect)
        return spectra

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
            "spectra": self.get_plot_spectra(),
            "birs": self.get_birs(),
            "peaks": self.data.peaks,
        }


class h2o_processor(Raman_processor):
    def __init__(self, name, x, y, sample_settings, birs, interpolation_regions):

        self.name = name

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

    @property
    def interference(self):
        return self._interference

    def set_interference(self, x, y, sample_settings, birs):
        # y_interpolated = self._intertpolate_spectrum(x, y)
        self._interference = Raman_processor(
            self.name,
            x,
            y,
            sample_settings,
            birs,
        )

    def get_interference_settings(self) -> Tuple[Dict, Dict]:
        subtraction_settings = self.get_subtraction_settings()
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

    def calculate_interpolation(self):

        settings = self.get_interpolation_settings()

        self.interpolated_interval = self.data.interpolate(
            **settings,
            output=True,
        )

    def get_interpolation_settings(self):
        current_tab = app_configuration.gui["current_tab"]
        if current_tab == "interpolation":
            regions = self.interpolation_regions.values
            amount = len(regions) // 2
            regions = np.reshape(regions, (amount, 2))

            smoothing = self.settings[("interpolation", "smoothing")]
            use = self.settings[("interpolate", "use")]
            add_noise = True
            kwargs = {}
        elif current_tab == "interference":
            regions = np.array([self.get_subtraction_region()])
            smoothing = self.settings[("interference", "smoothing")]
            use = False
            add_noise = False
            kwargs = {"y": "raw"}
        return {
            **{
                "interpolate": regions,
                "smooth_factor": smoothing,
                "add_noise": add_noise,
                "use": use,
            },
            **kwargs,
        }

    def set_interpolation(self, kwargs: Dict) -> None:

        for region, new_value in kwargs.items():
            index = int(region[-2:])
            self.interpolation_regions.iloc[index] = new_value

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

    def get_subtraction_settings(self):
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

        settings = self.get_subtraction_settings()
        settings["interval"] = [settings.pop(key) for key in ("bir_00", "bir_01")]

        self.data.subtract_interference(interference=interference, **settings)
        return True

    def get_plotdata(self) -> Dict[str, Any]:

        plotdata = super().get_plotdata()
        plotdata["subtraction_region"] = self.get_subtraction_region()
        plotdata["interpolation_regions"] = None

        if self.interpolated_interval is not None:
            plotdata["interpolated_interval"] = self.interpolated_interval

        if self.interference:
            plotdata["interference"] = self.interference.get_plotdata()

        return plotdata
