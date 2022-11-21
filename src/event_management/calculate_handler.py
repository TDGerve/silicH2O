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

        settings = self.sample_controller.get_sample_settings()

        self.gui.update_variables(**settings)
        self.update_gui_results()

        self.refresh_plots("sample change")

    def change_settings(self, *args, **kwargs):
        self.sample_controller.change_sample_settings(**kwargs)
        self.sample_controller.calculate_sample()

    def update_gui_results(self):
        results = self.sample_controller.get_sample_results()
        self.gui.update_variables(**results)

    def update_from_plot(self, *args, **settings):

        self.change_settings(**settings)

        self.gui.update_variables(**settings)
        self.update_gui_results()

        self.refresh_plots("settings change")

    def update_from_widgets(self, *args, **kwargs):

        self.change_settings(**kwargs)
        self.update_gui_results()

        self.refresh_plots("settings change")

    def refresh_plots(self, *args):
        plot_data = self.sample_controller.get_sample_plotdata()

        self.on_plot_change.send("refresh plot", **plot_data)

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.update_from_plot, sender="plot")
        self.on_settings_change.connect(self.update_from_widgets, sender="widget")
