import blinker as bl
import numpy as np

from typing import Dict, List

from ..GUI.plots import Plot


class Plot_listener:

    on_plot_change = bl.signal("refresh plot")

    def __init__(self, plots: Dict[str, Plot]):
        self.subscribe_to_signals()
        self.plots = plots

    def plot_sample(
        self, *args, name: str, x: np.ndarray, spectra: Dict[str, np.ndarray]
    ):
        for plot in self.plots.values():
            plot.plot_lines(x, spectra)

    def subscribe_to_signals(self):
        self.on_plot_change.connect(self.plot_sample)
