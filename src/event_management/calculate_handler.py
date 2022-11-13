import blinker as bl

from ..sample_handlers import Sample_handler
from ..interface import Gui


class Calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")
    on_plot_change = bl.signal("refresh plot")

    def __init__(self, sample_database: Sample_handler, gui: Gui):
        self.sample_database = sample_database
        self.gui = gui

        self.subscribe_to_signals()

    def switch_sample(self, *args, index: int):

        self.sample_database.current_sample_index = index
        self.sample_database.current_sample.calculate()

        bir_settings = self.sample_database.current_sample.construct_birs()
        self.gui.update_variables(bir_settings=bir_settings)

        self.refresh_plots("sample change")

    def change_settings(self, *args, **kwargs):
        self.sample_database.current_sample.change_settings(**kwargs)
        self.sample_database.current_sample.calculate()

        self.refresh_plots("settings change")

    def refresh_plots(self, *args):
        (
            sample_name,
            x,
            spectra,
            baseline_spectrum,
        ) = self.sample_database.current_sample.retrieve_plot_data()
        self.on_plot_change.send(
            "refresh plot",
            sample_name=sample_name,
            x=x,
            spectra=spectra,
            baseline_spectrum=baseline_spectrum,
        )

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.change_settings)
