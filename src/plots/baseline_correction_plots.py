from itertools import product
from typing import Dict

import blinker as bl
import numpy as np

from ..interface.screens import Screen
from .plot_interaction import construct_polygon_coordinates, drag_polygons
from .plots import Double_plot

on_settings_change = bl.signal("settings change")


class Baseline_correction_plot(Double_plot):
    def __init__(self, screen: Screen):

        super().__init__(screen, xlabel="Raman shift cm$^{-1}$", ylabel="Counts")

        self.setup_ax0(
            title="Silicate region",
            limits=(100, 1400),
        )
        self.setup_ax1(title="H$_2$O region", limits=(2000, 4000))

        self.birs = []
        self.plot_interactions = []
        self.mouse_connections = []
        self.plot_interactions = []

    def draw_plot(self, **kwargs):
        birs = kwargs.pop("birs")

        self.plot_lines(**kwargs)
        self.plot_birs(birs)

        self.fig.canvas.draw_idle()

    def plot_lines(
        self,
        x: np.ndarray,
        spectra: Dict[str, np.ndarray],
        baseline_spectrum: str,
        **kwargs
    ):

        plot_items = (baseline_spectrum, "baseline", "baseline_corrected")

        keys = list(spectra.keys())
        for key in keys:
            if key not in plot_items:
                _ = spectra.pop(key)

        return super().plot_lines(x, spectra)

    def clear_birs(self, amount=None):
        if amount is None:
            amount = len(self.birs)
        for _ in range(amount):
            self.birs[0].remove()
            self.birs.remove(self.birs[0])
        self.fig.canvas.draw_idle()

    def clear_figure(self):
        self.clear_birs()
        super().clear_figure()

    def plot_birs(self, birs: Dict[(int, float)]):

        if len(birs.keys()) != len(self.birs):
            self.clear_birs()

        connect_mouse = False if self.birs else True

        bir_values = list(birs.values())
        birs = np.reshape(bir_values, (len(bir_values) // 2, 2))

        # bir_surplus = (len(self.birs) / 2) - len(birs)
        # if bir_surplus > 0:
        #     self.clear_birs(amount=bir_surplus)

        for i, (ax, (left_boundary, right_boundary)) in enumerate(
            product(self.axs, birs)
        ):
            try:
                current_bir = self.birs[i]
                coordinates = construct_polygon_coordinates(
                    left_boundary, right_boundary
                )

                if np.array_equal(coordinates, current_bir.get_xy()):
                    continue

                current_bir.set_xy(coordinates)  # Replace old bir

            except IndexError:
                self.birs.append(
                    ax.axvspan(
                        left_boundary,
                        right_boundary,
                        alpha=0.5,
                        color="lightgray",
                        edgecolor=None,
                    )
                )

        if connect_mouse:
            self.connect_mouse_events()

    def connect_mouse_events(self):

        # disconnect previously existing connections
        for connection in self.mouse_connections:
            self.fig.canvas.mpl_disconnect(connection)

        bir_amount = len(self.birs) // 2

        drag_ax0 = drag_polygons(
            ax=self.axs[0],
            polygons=self.birs[:bir_amount],
            identifier="baseline",
        )
        drag_ax1 = drag_polygons(
            ax=self.axs[1],
            polygons=self.birs[bir_amount:],
            identifier="baseline",
        )

        self.plot_interactions = [drag_ax0, drag_ax1]

        # connect mouse events
        for ax in [drag_ax0, drag_ax1]:
            self.mouse_connections.append(
                self.fig.canvas.mpl_connect("button_press_event", ax.on_click)
            )
            self.mouse_connections.append(
                self.fig.canvas.mpl_connect("button_release_event", ax.on_release)
            )
            self.mouse_connections.append(
                self.fig.canvas.mpl_connect("motion_notify_event", ax.on_motion)
            )
