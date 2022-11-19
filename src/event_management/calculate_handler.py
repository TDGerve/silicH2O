import blinker as bl

from ..spectral_processing import Sample_controller
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
        self.sample_controller.calculate_sample()
        bir_settings, areas = self.sample_controller.get_sample_settings()

        self.gui.update_variables(birs=bir_settings, areas=areas)
        # Recalculate current sample

        self.refresh_plots("sample change")

    def change_settings(self, *args, **kwargs):
        self.sample_controller.change_sample_settings(**kwargs)
        self.sample_controller.calculate_sample()

        _, areas = self.sample_controller.get_sample_settings()

        self.gui.update_variables(areas=areas, **kwargs)
        self.refresh_plots()

    def refresh_plots(self, *args):
        plot_data = self.sample_controller.get_sample_plotdata()

        self.on_plot_change.send("refresh plot", **plot_data)

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.change_settings)
