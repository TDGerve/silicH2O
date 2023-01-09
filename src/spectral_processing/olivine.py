import numpy as np
from ramCO2.raman.baseclass import RamanProcessing


class Olivine(RamanProcessing):
    # Baseline regions
    birs_default = np.array(
        [
            [100, 185],
            [260, 272],
            [370, 380],
            [470, 515],
            [660, 740],
            [1050, 4000],
        ]
    )

    def __init__(self, x, y):

        super().__init__(x, y)

    def baselineCorrect(self, baseline_regions=None, smooth_factor=1e-4, **kwargs):

        if baseline_regions is None:
            baseline_regions = self.birs_default

        return super().baselineCorrect(
            baseline_regions=baseline_regions, smooth_factor=smooth_factor, **kwargs
        )

    def deconvolve(
        self,
        *,
        peak_prominence=4,
        noise_threshold=1.6,
        threshold_scale=0.2,
        min_amplitude=3,
        min_peak_width=6,
        fit_window=6,
        max_iterations=5,
        cutoff=1400,
        **kwargs,
    ):

        if "noise" in kwargs:
            noise = kwargs.pop("noise")
        elif hasattr(self, "noise"):
            noise = self.noise
        else:
            noise = None

        super().deconvolve(
            min_peak_width=min_peak_width,
            peak_prominence=peak_prominence,
            noise_threshold=noise_threshold,
            threshold_scale=threshold_scale,
            min_amplitude=min_amplitude,
            fit_window=fit_window,
            noise=noise,
            max_iterations=max_iterations,
            cutoff=cutoff,
            **kwargs,
        )
