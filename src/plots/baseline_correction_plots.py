import numpy as np

from itertools import product
from typing import Dict
import blinker as bl

from .plots import Double_plot
from .plot_interaction import drag_polygons, construct_polygon_coordinates
from ..interface.screens import Screen

on_settings_change = bl.signal("settings change")


class Baseline_correction_plot(Double_plot):
    def __init__(self, screen: Screen):

        super().__init__(
            screen, xlabel="Raman shift cm$^{-1}$", ylabel="Intensity (arbitr. units)"
        )

        self.setup_ax1(
            title="Silicate region",
            limits=(100, 1400),
        )
        self.setup_ax2(title="H$_2$O region", limits=(2000, 4000))

        self.birs = []
        self.mouse_connections = []

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], baseline_spectrum: str
    ):

        for key in spectra.keys():
            if key not in [
                baseline_spectrum,
                "baseline",
                "baseline_corrected",
            ]:
                _ = spectra.pop(key)

        return super().plot_lines(x, spectra)

    def plot_birs(self, birs):
        if not self.birs:
            connect_mouse = True
        else:
            connect_mouse = False

        birs = np.reshape(list(birs.values()), (5, 2))

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
                        alpha=0.3,
                        color="lightgray",
                        edgecolor=None,
                    )
                )

        if connect_mouse:
            self.connect_mouse_events()

    def connect_mouse_events(self):
        drag_ax1 = drag_polygons(
            ax=self.axs[0], polygons=self.birs[:5], drag_polygons=[1, 2]
        )
        drag_ax2 = drag_polygons(
            ax=self.axs[1], polygons=self.birs[5:], drag_polygons=[1, 2]
        )
        self.mouse_connections += [drag_ax1, drag_ax2]

        for ax in [drag_ax1, drag_ax2]:
            self.fig.canvas.mpl_connect("button_press_event", ax.on_click)
            self.fig.canvas.mpl_connect("button_release_event", ax.on_release)
            self.fig.canvas.mpl_connect("motion_notify_event", ax.on_motion)
