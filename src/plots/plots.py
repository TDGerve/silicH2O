import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple, Protocol, Dict

from . import plot_layout as pl
from ..interface.screens import Screen

from .. import settings


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def plot_birs(self):
        ...


class Double_plot:
    def __init__(self, screen: Screen, xlabel: str, ylabel: str):

        self.colors = getattr(pl.colors, settings.gui["plot_theme"])

        width, height = [
            size * screen.scaling / screen.dpi for size in screen.resolution
        ]

        pl.Plot_layout(scaling=screen.scaling, colors=self.colors)

        self.fig, self.axs = plt.subplots(
            2, 1, figsize=(width, height)  # , constrained_layout=True
        )
        self.lines = {"ax1": {}, "ax2": {}}

        # Needs matplotlib > 3.4 & Python > 3.7
        self.fig.supxlabel(xlabel)
        self.fig.supylabel(ylabel)

        for ax in self.axs:
            ax.set_yticks([])
            ax.set_ylim(0, 1e-2)

    def setup_ax1(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[0]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def setup_ax2(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[1]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        colors = self.colors.by_key()["color"]

        for ax, lines in zip(self.axs, self.lines.values()):

            xmin, xmax = ax.get_xlim()
            ymax = []
            for (name, spectrum), color in zip(spectra.items(), colors):
                ymax.append(spectrum[(xmin < x) & (x < xmax)].max())
                try:
                    if np.array_equal(lines[name][0].get_ydata(), spectrum):
                        continue

                    lines[name][0].set_xdata(x)
                    lines[name][0].set_ydata(spectrum)
                except KeyError:
                    lines[name] = ax.plot(x, spectrum, label=name, color=color)

            ymax = max(ymax) * 1.1
            ax.set_ylim(0, ymax)

        self.fig.canvas.draw_idle()
