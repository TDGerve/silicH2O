import blinker as bl
from ..sample_processing import h2o_processor
from ..sample_database import Sample_database


class sample_calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")

    def __init__(self, sample_database: Sample_database):
        self.sample_database = sample_database
        self.subscribe_to_signals()

    def switch_sample(self, sender, index: int):

        self.sample_database.current_sample_index = index
        self.sample_database.current_sample.calculate()

    def change_settings(self, sender, **kwargs):
        self.sample_database.current_sample.change_settings(**kwargs)
        self.sample_database.current_sample.calculate()

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample)
        self.on_settings_change.connect(self.change_settings)
