import pandas as pd
import ramCOH as ram


class Deconvolution_processor:
    def __init__(self, sample: ram.RamanProcessing, settings: pd.Series):
        self.sample = sample
        self.settings = settings

    def get_settings(self):

        return self.settings.to_dict()

    def apply_settings(self, kwargs):
        for key, value in kwargs.items():
            self.settings[key] = value

    def calculate(self, baseline0=True):
        if self.sample.noise is None:
            self.sample.calculate_noise()

        settings = self.get_settings()

        self.sample.deconvolve(
            y="baseline_corrected",
            noise=self.data.noise,
            baseline0=baseline0,
            **settings,
        )
