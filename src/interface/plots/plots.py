import numpy as np

from typing import Protocol, Dict

from .double_plots import Double_plot
from ..screens import Screen


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def plot_birs(self):
        ...


class Baseline_correction_plot(Double_plot):
    def __init__(self, screen: Screen):

        super().__init__(
            screen, xlabel="Raman shift cm$^{-1}$", ylabel="Intensity (arbitr. units)"
        )

        self.setup_ax1(
            title="Silicate region",
            limits=(200, 1400),
        )
        self.setup_ax2(title="H$_2$O region", limits=(2000, 4000))

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], baseline_spectrum: str
    ):

        for key in spectra.keys():
            if key not in [
                baseline_spectrum,
                "baseline",
                "baseline_corrected",
            ]:
                _ = spectra.pop(key)

        return super().plot_lines(x, spectra)
