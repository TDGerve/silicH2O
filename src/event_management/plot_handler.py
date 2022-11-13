import blinker as bl
import numpy as np

from typing import Dict

from ..GUI.plots import Plot
from ..GUI import Main_window


class Plot_listener:

    on_plot_change = bl.signal("refresh plot")
    on_plots_initialised = bl.signal("plots initialised")

    def __init__(self, window: Main_window, plots: Dict[str, Plot]):
        self.plots = plots
        self.window = window

        self.subscribe_to_signals()

    def plot_sample(
        self,
        *args,
        sample_name: str,
        x: np.ndarray,
        spectra: Dict[str, np.ndarray],
        baseline_spectrum: str
    ):
        for plot in self.plots.values():
            plot.plot_lines(x, spectra, baseline_spectrum=baseline_spectrum)

    def draw_plots(self, *args):

        self.window.add_plots(self.plots)

    def subscribe_to_signals(self):
        self.on_plot_change.connect(self.plot_sample)
        self.on_plots_initialised.connect(self.draw_plots)
