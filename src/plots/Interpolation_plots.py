from ..interface.screens import Screen
from .plots import Single_plot


class Interpolation_plot(Single_plot):
    def __init__(self, screen: Screen):

        super().__init__(screen, xlabel="Raman shift cm$^{-1}$", ylabel="Counts")
        self.setup_ax(limits=(0, 4000))

        self.irs = []
        self.mouse_connections = []

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        return super().plot_lines(x, spectra, *args, **kwargs)
