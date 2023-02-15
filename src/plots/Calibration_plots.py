import matplotlib.pyplot as plt
import numpy as np

from .. import app_configuration
from ..interface.screens import Screen
from . import plot_layout as pl
from .plots import Single_plot


class Calibration_plot(Single_plot):
    def __init__(self, screen: Screen):
        super().__init__(
            screen=screen,
            xlabel="Raman Area$_{H_2O}$/Area$_{Si}$",
            ylabel="",
        )

        self.ax.grid(axis="both", visible=True)
        self.fig.set_size_inches(w=10 * self.scale, h=8 * self.scale)
        self.fig.supylabel("ref.\nH$_2$O (wt.%)", rotation=0, ma="center")

        self.calibration_stds = None

    def plot_samples(self, H2OSi, H2Oref):
        self.calibration_stds = self.ax.plot(H2OSi, H2Oref, "D", mec="k", zorder=10)

    def plot_calibrationline(self, intercept: float, slope: float):
        calibration = lambda H2OSi: intercept + H2OSi * slope
        xmin, xmax = self.ax.get_xlim()
        x = np.linspace(xmin, xmax, 2)

        self.lines["calibration"] = self.ax.plot(
            x, calibration(x), "--", color="darkgrey"
        )
