from typing import Dict, List, Optional

import blinker as bl
import numpy as np

from .. import app_configuration
from ..plots import Plot


class Plot_listener:

    on_plot_change = bl.signal("refresh plot")
    on_clear_plot = bl.signal("clear plot")
    # on_plots_initialised = bl.signal("plots initialised")

    # on_plot_calibration = bl.signal("plot calibration")

    def __init__(self, plots: Dict[str, Plot]):
        self.plots = plots

        self.subscribe_to_signals()

    @property
    def current_tab(self):
        return app_configuration.gui["current_tab"]

    def plot_sample(
        self,
        *args,
        plot: str,
        plotdata: Dict,
        **kwargs,
    ):

        plot = self.plots[plot]

        sample_name = plotdata.pop("name", None)
        if sample_name:
            plot.display_name(sample_name)
        plot.draw_plot(**plotdata)

    # def plot_calibration(self, *args, **kwargs):
    #     plot = self.plots["calibration"]
    #     plot.draw_plot(**kwargs)

    def clear_plot(self, *args):
        for plot in self.plots.values():
            plot.clear_figure()

    def subscribe_to_signals(self):
        self.on_plot_change.connect(self.plot_sample)
        # self.on_plot_calibration.connect(self.plot_calibration)
        self.on_clear_plot.connect(self.clear_plot)
