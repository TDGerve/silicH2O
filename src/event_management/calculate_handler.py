import blinker as bl

from .. import app_configuration
from ..interface import Gui
from ..spectral_processing import Sample_controller


class Calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")

    on_Ctrl_c = bl.signal("copy birs")
    on_Ctrl_v = bl.signal("paste birs")
    on_Ctrl_z = bl.signal("ctrl+z")

    on_plot_change = bl.signal("refresh plot")
    on_switch_tab = bl.signal("switch tab")
    on_reset_sample = bl.signal("reset sample")

    on_display_message = bl.signal("display message")

    copied_birs = None

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def display_sample(self, message: str):
        try:
            self.sample_controller.calculate_sample()
        except AttributeError:
            return

        settings = self.sample_controller.get_sample_settings()

        current_tab = app_configuration.gui["current_tab"]
        settings = settings[current_tab]

        self.gui.update_variables(**{current_tab: settings})
        self.update_gui_results()

        self.refresh_plots(message)

    def copy_birs(self, *args):
        try:
            self.copied_birs = self.sample_controller.get_sample_settings()["baseline"]
            self.on_display_message.send(message="copied birs")
        except AttributeError:
            pass

    def reset_sample(self, *args):
        self.sample_controller.reset_sample()

    def paste_birs(self, *args):
        if self.copied_birs is None:
            pass
        self.update_from_plot(baseline=self.copied_birs)
        self.refresh_plots("settings change")
        self.on_display_message.send(message="pasted birs")

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
        try:
            plot_data = self.sample_controller.get_sample_plotdata()
        except AttributeError:
            return
        self.on_plot_change.send(message, **plot_data)

    def reset_sample(self, *args):

        self.sample_controller.reset_sample()
        self.display_sample("sample reset")

    def tab_change(self, *args):
        self.display_sample(*args)

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample, sender="navigator")
        self.on_settings_change.connect(self.update_from_plot, sender="plot")
        self.on_settings_change.connect(self.update_from_widgets, sender="widget")

        self.on_Ctrl_c.connect(self.copy_birs)
        self.on_Ctrl_v.connect(self.paste_birs)
        self.on_Ctrl_z.connect(self.reset_sample)

        self.on_reset_sample.connect(self.reset_sample)
        self.on_switch_tab.connect(self.tab_change)
