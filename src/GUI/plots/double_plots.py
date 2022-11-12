from typing import Dict
import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple

from ... import settings


class Double_plot:
    def __init__(self, dpi: int):

        window_size = settings.gui["geometry"]["size"]
        height = int(window_size[-4:]) * 0.6 / dpi
        width = int(window_size[:4]) * 0.3 / dpi

        self.fig, self.axs = plt.subplots(
            2, 1, figsize=(3, 7), dpi=dpi, constrained_layout=True
        )
        self.lines = {"ax1": {}, "ax2": {}}

        for ax in self.axs:
            ax.set_yticks([])

    def setup_ax1(self, title: str, ylabel: str, limits: Tuple[int, int]):
        ax = self.axs[0]

        ax.set_title(title)
        ax.set_ylabel(ylabel)

        ax.set_xlim(*limits)

    def setup_ax2(self, title: str, xlabel: str, limits: Tuple[int, int]):

        ax = self.axs[1]

        ax.set_title(title)
        ax.set_xlabel(xlabel)

        ax.set_xlim(*limits)

    def plot_lines(self, x: np.ndarray, spectra: Dict[str, np.ndarray]):

        for ax, lines in zip(self.axs, self.lines.values()):

            xmin, xmax = ax.get_xlim()
            ymax = []
            for name, spectrum in spectra.items():
                if name not in [
                    "raw",
                    "interpolated",
                    "baseline",
                    "baseline_corrected",
                ]:
                    continue
                try:
                    lines[name][0].remove()  # Remove old line
                except KeyError:
                    pass
                lines[name] = ax.plot(x, spectrum, label=name)
                ymax.append(spectrum[(xmin < x) & (x < xmax)].max())
            ymax = max(ymax) * 1.1
            ax.set_ylim(0, ymax)

        self.fig.canvas.draw_idle()

    def plot_birs(self):
        pass

    def update(self):
        pass
