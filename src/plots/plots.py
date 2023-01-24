from typing import Dict, Protocol, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .. import app_settings
from ..interface.screens import Screen
from . import plot_layout as pl


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def plot_birs(self):
        ...

    def clear_plot(self):
        ...


class Double_plot:
    def __init__(self, screen: Screen, xlabel: str, ylabel: str):

        self.colors = getattr(pl.colors, app_settings.gui["plot_theme"])

        width, height = [
            size * screen.scaling / screen.dpi for size in screen.resolution
        ]

        pl.Plot_layout(scaling=screen.scaling, colors=self.colors)

        self.fig, self.axs = plt.subplots(
            2, 1, figsize=(width, height)  # , constrained_layout=True
        )
        self.lines = {"ax1": {}, "ax2": {}}
        self.name = None

        # Needs matplotlib > 3.4 & Python > 3.7
        self.fig.supxlabel(xlabel)
        self.fig.supylabel(ylabel)

        for ax in self.axs:
            # ax.set_yticks([])
            ax.set_ylim(0, 1e-2)

    def setup_ax1(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[0]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def setup_ax2(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[1]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def clear_figure(self):

        if self.name is None:
            return

        self.name.set_text("")

        for _, lines in zip(self.axs, self.lines.values()):

            for line in lines.values():
                line[0].set_xdata([])
                line[0].set_ydata([])

        self.fig.canvas.draw_idle()

    def display_name(self, sample_name):
        if self.name is None:
            self.name = self.axs[0].text(
                0.01, 0.95, sample_name, transform=self.axs[0].transAxes
            )
        else:
            self.name.set_text(sample_name)

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
            if ymax > 2e3:
                ax.ticklabel_format(axis="y", style="scientific", useMathText=True)

        self.fig.canvas.draw_idle()


class Single_plot:
    def __init__(self, screen: Screen, xlabel: str, ylabel: str):

        self.colors = getattr(pl.colors, app_settings.gui["plot_theme"])

        width, height = [
            size * screen.scaling / screen.dpi for size in screen.resolution
        ]

        pl.Plot_layout(scaling=screen.scaling, colors=self.colors)

        self.fig, self.ax = plt.subplots(figsize=(width, height))
        self.lines = {}
        self.name = None

        self.ax.set_ylim(0, 1e-2)

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def setup_ax(self, limits: Tuple[int, int], title: str = None):

        self.ax.set_title(title)
        self.ax.set_xlim(*limits)

    def clear_figure(self):

        if self.name is None:
            return

        self.name.set_text("")

        for line in self.lines.values():

            line[0].set_xdata([])
            line[0].set_ydata([])

        self.fig.canvas.draw_idle()

    def display_name(self, sample_name):
        if self.name is None:
            self.name = self.ax.text(
                0.01, 0.95, sample_name, transform=self.ax.transAxes
            )
        else:
            self.name.set_text(sample_name)

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        colors = self.colors.by_key()["color"]

        for color, (name, new_vals), color in zip(colors, spectra.items()):

            xmin, xmax = self.ax.get_xlim()
            ymax = []

            ymax.append(new_vals[(xmin < x) & (x < xmax)].max())
            try:
                if np.array_equal(self.lines[name][0].get_ydata(), new_vals):
                    continue

                self.lines[name][0].set_xdata(x)
                self.lines[name][0].set_ydata(new_vals)
            except KeyError:
                self.lines[name] = self.ax.plot(x, new_vals, label=name, color=color)

            ymax = max(ymax) * 1.1
            self.ax.set_ylim(0, ymax)
            if ymax > 2e3:
                self.ax.ticklabel_format(axis="y", style="scientific", useMathText=True)

        self.fig.canvas.draw_idle()
