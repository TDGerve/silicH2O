from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np

from .. import app_configuration
from ..interface.screens import Screen
from . import plot_layout as pl
from .plots import Single_plot


class Calibration_plot(Single_plot):
    def __init__(self, screen: Screen):
        super().__init__(
            screen=screen,
            xlabel="Raman Area$_{H_2O}$/Area$_{Si}$",
            ylabel="",
        )

        self.ax.grid(axis="both", visible=True)
        self.fig.set_size_inches(w=8 * self.scale, h=7 * self.scale)
        self.fig.supylabel("ref.\nH$_2$O (wt.%)", rotation=0, ma="center")

        self.annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(-10, 12),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            zorder=100,
        )
        self.annotation.set_visible(False)

        self.calibration_stds = None
        self.names = []

        self.mouse_connections = []

        self.connect_mouse_events()

    def clear_figure(self):
        ...

    def display_name(self, name):
        if self.name is None:
            self.name = self.ax.text(
                0.03,
                0.97,
                name,
                transform=self.ax.transAxes,
                fontsize="x-large",
                fontweight="semibold",
            )
        else:
            self.name.set_text(name)

    def draw_plot(self, **kwargs):
        H2OSi, H2Oref = kwargs.pop("standards")
        calibration_line = kwargs.pop("calibration_line")

        self.plot_samples(H2OSi=H2OSi, H2Oref=H2Oref)
        self.plot_calibrationline(calibration_line=calibration_line)

        self.fig.canvas.draw_idle()

    def plot_samples(self, H2OSi, H2Oref):
        try:
            plot = self.calibration_stds
            if np.array_equal(H2OSi, plot.get_xdata()) & np.array_equal(
                H2Oref, plot.get_ydata()
            ):
                return
            plot.set_xdata(H2OSi)
            plot.set_ydata(H2Oref)
        except AttributeError:
            (self.calibration_stds,) = self.ax.plot(
                H2OSi, H2Oref, "D", mec="k", zorder=10
            )

        self.names = H2OSi.index.to_list()
        # Reset ax limits
        self.ax.relim()
        self.ax.autoscale()

    def plot_calibrationline(self, calibration_line: Optional[Callable]):

        plot = self.calibration_stds

        x_total = plot.get_xdata()
        try:
            xmin, xmax = min(x_total), max(x_total)
        except ValueError:
            return

        x = np.linspace(xmin, xmax, 2)
        y = calibration_line(x)

        if y is None:
            return

        try:
            plot = self.lines["calibration"]

            if np.array_equal(plot.get_ydata(), y):
                return

            plot.set_xdata(x)
            plot.set_ydata(y)
        except KeyError:

            (self.lines["calibration"],) = self.ax.plot(
                x, y, "--", linewidth=2, color="darkgrey"
            )

    def update_annotation(self, ind):

        x, y = self.calibration_stds.get_data()

        self.annotation.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = "{}".format(", ".join([self.names[n] for n in ind["ind"]]))[:10]

        self.annotation.set_text(text)

    def hover(self, event):
        if not self.calibration_stds:
            return

        vis = self.annotation.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.calibration_stds.contains(event)
            if cont:
                self.update_annotation(ind)
                self.annotation.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annotation.set_visible(False)
                    self.fig.canvas.draw_idle()

    def connect_mouse_events(self):

        for connection in self.mouse_connections:

            self.fig.canvas.mpl_disconnect(connection)

        self.mouse_connections.append(
            self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        )
