from typing import Dict, List, Optional, Protocol, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .. import app_configuration
from ..interface.screens import Screen
from . import plot_layout as pl


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def draw_plot(self):
        ...

    def clear_plot(self):
        ...


class Double_plot:
    def __init__(self, screen: Screen, xlabel: str, ylabel: str):

        self.colors = getattr(pl.colors, app_configuration.gui["plot_theme"])

        width, height = [
            size * screen.scaling / screen.dpi for size in screen.resolution
        ]

        pl.plot_layout(scaling=screen.scaling, colors=self.colors)

        self.fig, self.axs = plt.subplots(
            2, 1, figsize=(width, height)  # , constrained_layout=True
        )
        # self.lines = {"ax0": {}, "ax1": {}}
        self.name = None
        self.lines = {"ax0": {}, "ax1": {}}

        # Needs matplotlib > 3.4 & Python > 3.7
        self.fig.supxlabel(xlabel)
        self.fig.supylabel(ylabel)

        for ax in self.axs:
            # ax.set_yticks([])
            ax.set_ylim(0, 1e-2)

        # Disconnect key bindings
        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)

    def setup_ax0(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[0]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def setup_ax1(self, title: str, limits: Tuple[int, int]):

        ax = self.axs[1]
        ax.set_title(title)
        ax.set_xlim(*limits)

    def clear_figure(self):

        if self.name is None:
            return

        self.name.set_text("")

        for lines in self.lines.values():
            self.clear_lines(lines)

        self.fig.canvas.draw_idle()

    def clear_plot_elements(self, plot_elements: List, amount: Optional[int] = None):
        if amount is None:
            amount = len(plot_elements)
        for _ in range(amount):
            try:
                plot_elements[0].remove()
            except TypeError:
                plot_elements[0][0].remove()
            plot_elements.remove(plot_elements[0])
        self.fig.canvas.draw_idle()

    def clear_lines(self, lines: Dict, keys: Optional[List[str]] = None):
        if keys is None:
            keys = lines.keys()
        for key in keys:
            try:
                line = lines[key][0]
                line.set_xdata([])
                line.set_ydata([])
            except KeyError:
                pass

    def display_name(self, sample_name):
        if self.name is None:
            self.name = self.axs[0].text(
                0.01, 0.95, sample_name, transform=self.axs[0].transAxes
            )
        else:
            self.name.set_text(sample_name)

    def draw_plot(self):
        self.fig.canvas.draw_idle()
        self.reset_home()
        # self.fig.canvas.toolbar.push_current()

    def reset_home(self):
        nav_stack = self.fig.canvas.toolbar._nav_stack._elements
        if len(nav_stack) > 0:
            # Get the first key in the navigation stack
            axs_names = list(nav_stack[0].keys())
            axs_limits = self.get_ax_limits()
            for name, ax, limits in zip(axs_names, self.axs, axs_limits):
                ax.relim()
                # Construct a new tuple for replacement
                alist = []
                for x in self.fig.canvas.toolbar._nav_stack._elements[0][name]:
                    alist.append(x)
                alist[0] = limits
                # Replace in the stack
                self.fig.canvas.toolbar._nav_stack._elements[0][name] = tuple(alist)

    def get_ax_limits(self):
        ...

    def _get_ax_limits(self, ax1_xlim: Tuple[int, int], ax2_xlim: Tuple[int, int]):
        axs_limits = [[*ax1_xlim, 0, 0], [*ax2_xlim, 0, 0]]
        for i, (limits, lines) in enumerate(
            zip((ax1_xlim, ax2_xlim), self.lines.values())
        ):

            y_max = 0

            for line in lines.values():
                x_data = line[0].get_xdata()
                data_limits = (limits[0] < x_data) & (x_data < limits[1])
                y_data = line[0].get_ydata()[data_limits]
                y_max = max(y_max, max(y_data))

            axs_limits[i][3] = y_max

        return axs_limits

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):

        for i in range(2):
            self.plot_lines_axis(i, x, spectra)

    def plot_lines_axis(
        self,
        ax_id: int,
        x: np.ndarray,
        spectra: Dict[str, np.ndarray],
        set_ylim=True,
        *args,
        **kwargs,
    ):

        ax = self.axs[ax_id]
        colors = self.colors.by_key()["color"]
        lines = self.lines[f"ax{ax_id}"]

        xmin, xmax = ax.get_xlim()
        ymax = []

        # line_surplus = set(lines.keys()).difference(set(spectra.keys()))
        # if line_surplus:
        #     self.clear_lines(lines, keys=list(line_surplus))

        for (name, y), color in zip(spectra.items(), colors):
            ymax.append(y[(xmin < x) & (x < xmax)].max())
            try:
                if np.array_equal(lines[name][0].get_ydata(), y):
                    continue

                lines[name][0].set_xdata(x)
                lines[name][0].set_ydata(y)
            except KeyError:
                lines[name] = ax.plot(x, y, label=name, color=color, **kwargs)
                # if name in ("deconvoluted", "baseline"):
                #     lines[name][0].set(linewidth=2, alpha=0.5)

        if not set_ylim:
            return

        ymax = max(ymax) * 1.1
        ax.set_ylim(0, ymax)
        if ymax > 2e3:
            ax.ticklabel_format(axis="y", style="scientific", useMathText=True)

        self.set_line_formatting()

    def set_line_formatting(self):
        formatting = {
            "deconvoluted": [3, 0.4],
            "baseline": [2, 0.5],
            "interpolated": [2, 0.7],
            "interference_corrected": [1, 0.7],
        }
        for lines in self.lines.values():
            for name, fmt in formatting.items():
                try:
                    lines[name][0].set(linewidth=fmt[0], alpha=fmt[1])
                except KeyError:
                    continue


class Single_plot:
    def __init__(self, screen: Screen, xlabel: str, ylabel: str):

        self.colors = getattr(pl.colors, app_configuration.gui["plot_theme"])

        self.scale = screen.scaling
        width, height = [
            size * screen.scaling / screen.dpi for size in screen.resolution
        ]

        pl.plot_layout(scaling=screen.scaling, colors=self.colors)

        self.fig, self.ax = plt.subplots(
            figsize=(width, height), constrained_layout=True
        )
        self.lines = {}
        self.name = None

        self.ax.set_ylim(0, 1e-2)

        self.fig.supxlabel(xlabel)
        self.fig.supylabel(ylabel)

    def setup_ax(self, limits: Tuple[int, int], title: str = None):

        self.ax.set_title(title)
        self.ax.set_xlim(*limits)

    def clear_figure(self):

        if self.name is None:
            return

        self.name.set_text("")
        self.clear_lines(self.lines)

        self.fig.canvas.draw_idle()

    def clear_plot_elements(self, plot_elements: List, amount: Optional[int] = None):
        if amount is None:
            amount = len(plot_elements)
        for _ in range(amount):
            try:
                plot_elements[0].remove()
            except TypeError:
                plot_elements[0][0].remove()
            plot_elements.remove(plot_elements[0])

        self.fig.canvas.draw_idle()

    def clear_lines(self, lines: Dict, keys: Optional[List[str]] = None):
        if keys is None:
            keys = lines.keys()
        for key in keys:
            try:
                line = lines[key][0]
                line.set_xdata([])
                line.set_ydata([])
            except KeyError:
                pass

    def display_name(self, name):
        if self.name is None:
            self.name = self.ax.text(
                0.03,
                0.97,
                name,
                transform=self.ax.transAxes,
            )
        else:
            self.name.set_text(name)

    def draw_plot(self):
        self.fig.canvas.draw_idle()
        self.fig.canvas.toolbar.update()
        self.fig.canvas.toolbar.push_current()

    def plot_lines(
        self,
        x: np.ndarray,
        spectra: Dict[str, np.ndarray],
        set_ylim=True,
        *args,
        **kwargs,
    ):
        colors = self.colors.by_key()["color"]

        for color, (name, new_vals) in zip(colors, spectra.items()):

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

        self.set_line_formatting()

        if not set_ylim:
            return

        ymax = max(ymax) * 1.1
        self.ax.set_ylim(0, ymax)
        if ymax > 2e3:
            self.ax.ticklabel_format(axis="y", style="scientific", useMathText=True)

    def set_line_formatting(self):
        formatting = {
            "deconvoluted": [3, 0.4],
            "baseline": [2, 0.5],
            "interpolated": [2, 0.7],
            "interference_corrected": [1, 0.7],
        }

        for name, fmt in formatting.items():
            try:
                self.lines[name][0].set(linewidth=fmt[0], alpha=fmt[1])
            except KeyError:
                continue
