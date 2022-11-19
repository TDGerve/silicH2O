import blinker as bl
import numpy as np

from typing import Dict, List

from ..plots import Plot


class Plot_listener:

    on_plot_change = bl.signal("refresh plot")
    on_plots_initialised = bl.signal("plots initialised")

    def __init__(self, plots: Dict[str, Plot]):
        self.plots = plots

        self.subscribe_to_signals()

    def plot_sample(
        self,
        *args,
        sample_name: str,
        x: np.ndarray,
        spectra: Dict[str, np.ndarray],
        baseline_spectrum: str,
        birs: List[int],
        **kwargs,
    ):

        for name, plot in self.plots.items():
            plot.plot_lines(x, spectra, baseline_spectrum=baseline_spectrum)
            if name == "baseline_correction":

                plot.plot_birs(birs)

    def subscribe_to_signals(self):
        self.on_plot_change.connect(self.plot_sample)
