import blinker as bl

from ..spectral_processing import Sample_controller
from ..interface import Gui


class Calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")

    on_plot_change = bl.signal("refresh plot")

    on_save_sample = bl.signal("save sample")
    on_reset_sample = bl.signal("reset sample")
    on_save_all = bl.signal("save all")

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def display_sample(self, message: str):

        self.sample_controller.calculate_sample()

        settings = self.sample_controller.get_sample_settings()

        self.gui.update_variables(**settings)
        self.update_gui_results()

        self.refresh_plots(message)

    def switch_sample(self, *args, index: int):

        # Switch sample
        self.sample_controller.current_sample_index = index
        self.display_sample("sample change")

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

        # self.refresh_plots("settings change")

    def update_from_widgets(self, *args, **kwargs):

        self.change_settings(**kwargs)
        self.update_gui_results()

        self.refresh_plots("settings change")

    def refresh_plots(self, message: str):

        plot_data = self.sample_controller.get_sample_plotdata()
        self.on_plot_change.send(message, **plot_data)

    def save_sample(self, *args):

        self.sample_controller.save_sample()

    def save_all_samples(self, *args):

        self.sample_controller.save_all_samples()

    def reset_sample(self, *args):

        self.sample_controller.reset_sample()
        self.display_sample("sample reset")

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample, sender="navigator")
        self.on_settings_change.connect(self.update_from_plot, sender="plot")
        self.on_settings_change.connect(self.update_from_widgets, sender="widget")

        self.on_reset_sample.connect(self.reset_sample)
        self.on_save_sample.connect(self.save_sample)
        self.on_save_all.connect(self.save_all_samples)
