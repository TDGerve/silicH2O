from typing import Dict, List, Optional

import blinker as bl
import numpy as np

from ..interface import Gui
from ..plots import Plot


class Plot_listener:

    on_plot_change = bl.signal("refresh plot")
    on_clear_plot = bl.signal("clear plot")
    on_plots_initialised = bl.signal("plots initialised")
    on_mouse_movement = bl.signal("mouse moved")

    on_display_message = bl.signal("display message")

    def __init__(self, plots: Dict[str, Plot], gui: Gui):
        self.plots = plots
        self.gui = gui

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
            plot.display_name(sample_name)
            plot.plot_lines(x, spectra, baseline_spectrum=baseline_spectrum)
            if name == "baseline_correction":

                plot.plot_birs(birs)

    def clear_plot(self, *args):
        for plot in self.plots.values():
            plot.clear_figure()

    def send_plot_coordinates(self, *args, **kwargs):
        # print(kwargs)
        self.gui.update_variables(**kwargs)

    def display_message(self, *args, message: str, duration: Optional[int] = 2):

        message = f"{message:>50}"
        kwargs = {"infobar": {"info": message}}
        self.gui.update_variables(**kwargs)
        if duration is None:
            return
        self.gui.window.after(
            int(duration * 1e3), lambda: self.gui.update_variables(infobar={"info": ""})
        )

    def subscribe_to_signals(self):
        self.on_plot_change.connect(self.plot_sample)
        self.on_mouse_movement.connect(self.send_plot_coordinates)
        self.on_clear_plot.connect(self.clear_plot)
        self.on_display_message.connect(self.display_message)
