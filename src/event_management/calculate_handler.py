import blinker as bl
import numpy as np

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

        print(f"switching to sample: {index} \n")
        print(f"new birs: {self.sample_database.spectra[index].settings}")

        # Switch sample
        self.sample_database.current_sample_index = index
        # Update GUI variables

        bir_settings = self.sample_database.current_sample.birs
        bir_settings = np.concatenate(bir_settings)  # Flatten nested list
        print(f"sample {index} birs: {bir_settings}")
        self.gui.update_variables(birs=bir_settings)
        # Recalculate current sample
        self.sample_database.current_sample.calculate()

        print("switch complete")
        self.refresh_plots("sample change")

    def change_settings(self, *args, **kwargs):
        print(f"changing setting: '{kwargs.keys()}'")
        self.sample_database.current_sample.change_settings(**kwargs)
        self.sample_database.current_sample.calculate()

        # self.gui.update_variables(**kwargs)
        print(f"change complete")
        self.refresh_plots()

    def refresh_plots(self, *args):
        print("request plot refresh")
        plot_data = self.sample_database.current_sample.retrieve_plot_data()

        self.on_plot_change.send("refresh plot", **plot_data)
        print("request complete")

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.change_settings)
