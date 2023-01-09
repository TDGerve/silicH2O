import numpy as np
import csaps as cs
import scipy.optimize as opt
import scipy.interpolate as itp
from warnings import warn


from ramCO2.signal_processing import functions as f
from ramCO2.signal_processing import curve_fitting as cf
from ramCO2.signal_processing import curves as c
from ramCO2.signal_processing import deconvolution as d
from ramCO2.raman.baseclass import RamanProcessing

from .olivine import Olivine


class H2O(RamanProcessing):
    # Baseline regions
    birs_default = np.array(
        [[200, 300], [640, 655], [800, 810], [1220, 2300], [3750, 4000]]
    )

    def __init__(self, x, y, **kwargs):

        super().__init__(x, y, **kwargs)
        self._processing.update(
            {"long_corrected": False, "interpolated": False, "olivine_corrected": False}
        )

    def longCorrect(self, T_C=23.0, normalisation="area", **kwargs):

        laser = kwargs.get("laser", self.laser)

        y = kwargs.get("y", self._spectrumSelect)
        spectrum = self.signal.get(y)

        long_corrected = f.long_correction(self.x, spectrum, T_C, laser, normalisation)
        self.signal.add("long_corrected", long_corrected)
        # self.LC = 1
        self._spectrumSelect = "long_corrected"
        self._processing["long_corrected"] = True

    def calculate_SNR(self):

        if self.noise is None:
            self.calculate_noise()

        Si_left = max(self.birs[0])
        Si_right = min(self.birs[-2])
        Si_range = (self.x > Si_left) & (self.x < Si_right)

        water_left = max(self.birs[-2])
        water_right = min(self.birs[-1])
        water_range = (self.x > water_left) & (self.x < water_right)

        self.Si_SNR = max(self.signal.baseline_corrected[Si_range]) / self.noise
        self.H2O_SNR = max(self.signal.baseline_corrected[water_range]) / self.noise

    def interpolate(self, *, interpolate=[[780, 900]], smooth_factor=1, **kwargs):

        # birs = np.array(
        #     [[self.x.min(), min(interpolate)], [max(interpolate), self.x.max()]]
        # )
        spectrum_index = None
        for region in enumerate(interpolate):
            if not spectrum_index:
                spectrum_index = region[1] < self.x < region[0]
            else:
                spectrum_index = spectrum_index | (region[1] < self.x < region[0])

        spectrum = self.signal.get("raw")
        smooth = smooth_factor * 1e-5
        use = kwargs.get("use", True)

        # # Boolean array for glass only regions; no interference peaks
        # for i, region in enumerate(birs):
        #     if i == 0:
        #         glassIndex = (self.x > region[0]) & (self.x < region[1])
        #     else:
        #         glassIndex = glassIndex | ((self.x > region[0]) & (self.x < region[1]))
        # array with interference peaks
        interpolate_index = ~spectrum_index

        xbir = self.x[spectrum_index]
        ybir = spectrum[spectrum_index]

        spline = cs.csaps(xbir, ybir, smooth=smooth)
        self.spectrum_spline = spline(self.x)
        # Interpolated residual
        noise = (spectrum[spectrum_index] - self.spectrum_spline[spectrum_index]).std(
            axis=None
        )

        # _, baseline = f._extractBIR(
        #     self.x[self.x > 350], self.interpolation_residuals[self.x > 350], birs
        # )
        # noise = baseline.std(axis=None)
        # Add signal noise to the spline
        noise_spline = self.spectrum_spline + np.random.normal(0, noise, len(self.x))

        # only replace interpolated parts of the spectrum
        self.signal.add("interpolated", spectrum.copy())
        self.signal.interpolated[interpolate_index] = noise_spline[interpolate_index]

        # Area of interpolated regions
        # self.interpolated_area = np.trapz(
        #     self.interpolation_residuals[interpolate_index], self.x[interpolate_index]
        # )

        if use:
            self._spectrumSelect = "interpolated"
            self._processing["interpolated"] = True

    def _interpolate_olivine_peaks(self, olivine_free_regions, smooth=1e-6, **kwargs):

        spectrum = self.signal.get("raw")

        xbir, ybir = f._extractBIR(self.x, spectrum, olivine_free_regions)

        spline_model = cs.csaps(xbir, ybir, smooth=smooth)
        spline = spline_model(self.x)

        return spline

    @staticmethod
    def _root_olivine_interference(
        scaling, x, x_range, olivine, glass, glass_interpolated
    ):

        scale, shift = scaling
        x_min, x_max = x_range
        # Trim glass spectra to length
        glass = glass[(x > x_min) & (x < x_max)]
        glass_interpolated = glass_interpolated[(x > x_min) & (x < x_max)]
        # Trim and scale olivine spectrum
        olivine_scaled = olivine[(x > (x_min + shift)) & (x < (x_max + shift))] * scale
        # Subtract olivine
        glass_corrected = glass - olivine_scaled

        return [sum(abs(glass_interpolated - glass_corrected)), 0]

    def subtract_olivine_host(
        self, olivine: Olivine, boundaries=[700, 1020], inplace=False, **kwargs
    ):
        if not hasattr(olivine.signal, "baseline_corrected"):
            raise NameError("Apply baseline correction to olivine first")

        x_min, x_max = min(olivine.x), max(olivine.x)

        boundary_left, boundary_right = boundaries
        x_range = (self.x > x_min) & (self.x < x_max)
        x = self.x[x_range]

        glass_spectrum = getattr(self.signal, "raw")[x_range]
        glass_spline = self._interpolate_olivine_peaks(
            olivine_free_regions=olivine.birs
        )[x_range]

        olivine_interpolation_model = itp.interp1d(
            olivine.x, olivine.signal.baseline_corrected
        )
        olivine_y = olivine_interpolation_model(x)

        olivine_scaling = opt.root(
            self._root_olivine_interference,
            x0=[0.2, 0],
            args=(
                x,
                [boundary_left, boundary_right],
                olivine_y,
                glass_spectrum,
                glass_spline,
            ),
        ).x

        scale, shift = olivine_scaling
        olivine_x = x + shift
        olivine_y = olivine_y * scale

        glass_corrected = glass_spectrum - olivine_y

        # if inplace:
        #     setattr(self.signal, "olivine_corrected", olivine_corrected)
        #     self._spectrumSelect = "olivine_corrected"
        #     self._processing["olivine_corrected"] = True
        # else:
        return olivine_x, olivine_y, glass_corrected, glass_spline

    def extract_olivine(
        self, olivine_x, olivine_y, *, peak_prominence=10, smooth=1e-6, **kwargs
    ):

        # Set default values
        default_birs = np.array(
            [[0, 780], [900, 4000]]
        )  # np.array([[0, 250], [460, 550], [650, 720], [1035, 4000]])
        birs = kwargs.get("birs", default_birs)
        fit_window = kwargs.get("fit_window", 6)
        noise_threshold = kwargs.get("noise_threshold", 1.5)
        threshold_scale = kwargs.get("threshold_scale", 0.0)
        cutoff_high = 1100
        cutoff_low = 700

        y = kwargs.get("y", self._spectrumSelect)
        spectrum = self.signal.get(y)

        xbir, ybir = f._extractBIR(self.x, spectrum, birs)

        # fit spline to olivine free regions of the spectrum
        spline = cs.csaps(xbir, ybir, smooth=smooth)
        spectrum_spline = spline(self.x)
        self.spectrum_spline = spectrum_spline.copy()
        # Signal attributed to olivine interference
        olivine_interference = spectrum - spectrum_spline
        self.olivine_interference = olivine_interference.copy()

        # Calculate noise level
        noise_area = (self.x > 1250) & (self.x < 2000)
        noise = olivine_interference[noise_area].std(axis=None)

        # Remove part of the spectrum with no major olivine peaks
        trim = (self.x > cutoff_low) & (self.x < cutoff_high)
        olivine_trim = olivine_interference[trim]
        x = self.x[trim]

        # Deconvolute the major olivine peaks
        olivine_fit = RamanProcessing(x, olivine_trim)
        # print("fitting interference")ol
        olivine_fit.deconvolve(
            peak_prominence=peak_prominence,
            noise_threshold=1.5,
            threshold_scale=0.0,
            min_amplitude=6,
            min_peak_width=6,
            fit_window=6,
            noise=noise,
            max_iterations=3,
        )

        olivine_main_peaks = olivine_fit.deconvolution_parameters

        # Deconvolute host crystal spectrum
        olivine = Olivine(olivine_x, olivine_y)
        olivine.baselineCorrect()
        olivine.calculate_noise()
        # print("fitting host")
        olivine.deconvolve(
            y="baseline_corrected",
            fit_window=fit_window,
            noise_threshold=noise_threshold,
            threshold_scale=threshold_scale,
        )

        stepsize = abs(np.diff(self.x).mean())
        x_olivine_peaks = np.arange(700, 1200, int(stepsize * 10))
        interference_max = c.sum_GaussLorentz(
            x_olivine_peaks, *olivine_fit.deconvolution_parameters
        ).max()
        host_max = c.sum_GaussLorentz(
            x_olivine_peaks, *olivine.deconvolution_parameters
        ).max()
        self.olivine_scale = host_max / interference_max

        self.olivine = c.sum_GaussLorentz(self.x, *olivine.deconvolution_parameters)

        olivine_corrected = spectrum - (self.olivine / self.olivine_scale)
        self.signaladd("olivine_corrected", olivine_corrected)
        self._spectrumSelect = "olivine_corrected"
        self._processing["olivine_corrected"] = True

        self.olivinePeaks = [
            {"center": i, "amplitude": j, "width": k, "shape": l, "baselevel": m}
            for _, (i, j, k, l, m) in enumerate(zip(*olivine_main_peaks))
        ]

    def calculate_SiH2Oareas(self, **kwargs):

        if "baseline_corrected" not in self.signal.names:
            raise RuntimeError("run baseline correction first")

        Si_left = max(self.birs[0])
        Si_right = min(self.birs[-2])
        Si_range = (self.x > Si_left) & (self.x < Si_right)

        water_left = max(self.birs[-2])
        water_right = min(self.birs[-1])
        water_range = (self.x > water_left) & (self.x < water_right)

        spectrum = self.signal.get("baseline_corrected")
        SiArea = np.trapz(spectrum[Si_range], self.x[Si_range])
        H2Oarea = np.trapz(spectrum[water_range], self.x[water_range])

        self.SiH2Oareas = SiArea, H2Oarea

        return self.SiH2Oareas
