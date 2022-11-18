import blinker as bl
import numpy as np

from ..sample_controller import Sample_controller
from ..interface import Gui


class Calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")
    on_plot_change = bl.signal("refresh plot")

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def switch_sample(self, *args, index: int):

        # Switch sample
        self.sample_controller.current_sample_index = index
        # Update GUI variables

        bir_settings = self.sample_controller.current_sample.birs

        self.gui.update_variables(birs=bir_settings)
        # Recalculate current sample
        self.sample_controller.calculate_sample()

        self.refresh_plots("sample change")

    def change_settings(self, *args, **kwargs):
        self.sample_controller.change_sample_settings(**kwargs)
        self.sample_controller.calculate_sample()

        self.gui.update_variables(**kwargs)
        self.refresh_plots()

    def refresh_plots(self, *args):
        plot_data = self.sample_controller.current_sample.retrieve_plot_data()

        self.on_plot_change.send("refresh plot", **plot_data)

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.change_settings)
