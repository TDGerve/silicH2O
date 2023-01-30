from typing import Dict, Optional

import numpy as np

from ..interface.screens import Screen
from .plot_interaction import construct_polygon_coordinates, drag_polygons
from .plots import Double_plot


class Subtraction_plot(Double_plot):
    def __init__(self, screen: Screen):

        super().__init__(screen, xlabel="Raman shift cm$^{-1}$", ylabel="Counts")
        self.setup_ax0("glass", limits=(0, 4000))
        self.setup_ax1("interference", limits=(0, 4000))

        self.birs = []
        self.mouse_connection: Optional[drag_polygons] = None

    def draw_plot(self, **kwargs):

        interference = kwargs.pop("interference", None)
        if interference:
            birs = interference.pop("birs")
            self.plot_lines_axis(1, **interference)
            self.plot_birs(birs)
        else:
            self.clear_interference()

        self.plot_lines_axis(0, **kwargs)
        self.fig.canvas.draw_idle()

    def plot_lines_axis(
        self, ax_id: int, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        plot_items = [
            ("raw", "interference_corrected"),
            ("raw", "baseline", "baseline_corrected"),
        ][ax_id]

        keys = list(spectra.keys())
        for key in keys:
            if key not in plot_items:
                _ = spectra.pop(key)

        return super().plot_lines_axis(ax_id, x, spectra, *args, **kwargs)

    def clear_birs(self, amount=None):
        if amount is None:
            amount = len(self.birs)
        for _ in range(amount):
            self.birs[0].remove()
            self.birs.remove(self.birs[0])
        self.fig.canvas.draw_idle()

    def clear_figure(self):
        self.clear_birs()
        return super().clear_figure()

    def clear_interference(self):
        if self.birs:
            self.clear_birs()

        for line in self.lines["ax1"].values():
            line[0].set_xdata([])
            line[0].set_ydata([])
        self.fig.canvas.draw_idle()

    def plot_interference_peaks(self, peaks):
        ...

    def plot_birs(self, birs: Dict[(int, float)]):
        if not self.birs:
            connect_mouse = True
        else:
            connect_mouse = False

        ax = self.axs[1]

        bir_values = list(birs.values())
        birs = np.reshape(bir_values, (len(bir_values) // 2, 2))

        bir_surplus = len(self.birs) - len(birs)
        if bir_surplus > 0:
            self.clear_birs(amount=bir_surplus)

        for i, (left_boundary, right_boundary) in enumerate(birs):
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
        ax = self.axs[1]
        self.mouse_connection = drag_polygons(
            ax=ax,
            polygons=self.birs,  # drag_polygons=[1, 2]
            identifier="interference",
        )

        self.fig.canvas.mpl_connect(
            "button_press_event", self.mouse_connection.on_click
        )
        self.fig.canvas.mpl_connect(
            "button_release_event", self.mouse_connection.on_release
        )
        self.fig.canvas.mpl_connect(
            "motion_notify_event", self.mouse_connection.on_motion
        )
