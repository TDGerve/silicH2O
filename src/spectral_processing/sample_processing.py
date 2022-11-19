import pandas as pd
import numpy as np

from typing import List, Protocol, Dict

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
            {data: np.nan for data in ["SiArea", "H2Oarea", "rWS"]}
        )
        self.data = ram.H2O(x, y, laser=settings.general["laser_wavelength"])

    def get_birs(self) -> List[List[int]]:
        # birs = [list(bir[1]) for bir in self.settings.groupby(level=0)]
        birs = self.baseline_regions
        birs.index = range(len(birs))
        return dict(birs)

    # def calculate(self) -> None:

    #     self.calculate_interpolation()
    #     self.data.baselineCorrect(baseline_regions=self.birs)
    #     self.data.calculate_SiH2Oareas()
    #     self.results[["SiArea", "H2Oarea"]] = self.data.SiH2Oareas
    #     self.results["rWS"] = self.results["H2Oarea"] / self.results["SiArea"]

    def calculate_interpolation(self):

        if True:  # not self.settings[("interpolate", "use")]:
            return
        region = self.settings[("interpolate", "region")]
        smoothing = self.settings[("interpolate", "smoothing")]
        self.data.interpolate(interpolate=region, smooth_factor=smoothing)

    def set_birs(self, **kwargs) -> None:
        for bir, new_value in kwargs.items():
            index = int(bir)
            self.baseline_regions.iloc[index] = new_value

    def set_interpolation(self, **kwargs) -> None:
        pass

    # def change_settings(self, birs: dict = None, interpolate: dict = None) -> None:
    #     if birs is not None:

    #         self.set_birs(**birs)
    #     if interpolate is None:
    #         return
    #     self.set_interpolation(interpolate)

    def get_plot_data(self) -> Dict[str, any]:
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
            "birs": self.get_birs(),
        }
