from typing import Dict, Optional

import numpy as np
from ramCOH.signal_processing.curves import GaussLorentz

from ..interface.screens import Screen
from .plot_interaction import construct_polygon_coordinates, drag_polygons
from .plots import Double_plot


class Subtraction_plot(Double_plot):
    def __init__(self, screen: Screen):

        super().__init__(screen, xlabel="Raman shift cm$^{-1}$", ylabel="Counts")
        self.setup_ax0("glass", limits=(0, 4000))
        self.setup_ax1("interference", limits=(0, 4000))

        self.birs = []
        self.peak_curves = []
        self.peak_centers = []
        self.subtraction_region = []
        self.mouse_connections = {"interference": [], "subtraction": []}
        self.plot_interactions = {"interference": [], "subtraction": []}

    def draw_plot(self, **kwargs):

        interference = kwargs.pop("interference", None)
        if interference:
            birs = interference.pop("birs")
            peaks = interference.pop("peaks")
            self.plot_birs(birs)
            self.plot_peaks(peaks)
            self.plot_lines_axis(1, **interference)

        else:
            self.clear_interference()

        self.plot_lines_axis(0, **kwargs)
        self.plot_subtraction_region(**kwargs)
        self.fig.canvas.draw_idle()

    def plot_lines_axis(
        self, ax_id: int, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        plot_items = [
            ("raw", "interference_deconvoluted", "interference_corrected"),
            ("raw", "baseline", "baseline_corrected", "deconvoluted"),
        ][ax_id]

        keys = list(spectra.keys())
        for key in keys:
            if key not in plot_items:
                _ = spectra.pop(key)

        return super().plot_lines_axis(ax_id, x, spectra, *args, **kwargs)

    def clear_figure(self):
        for e in (
            self.birs,
            self.peak_curves,
            self.peak_centers,
            self.subtraction_region,
        ):
            self.clear_plot_elements(e)

        return super().clear_figure()

    def clear_interference(self):
        if self.birs:
            self.clear_plot_elements(self.birs)
            self.clear_plot_elements(self.peak_curves)

        for line in self.lines["ax1"].values():
            line[0].set_xdata([])
            line[0].set_ydata([])
        self.fig.canvas.draw_idle()

    def plot_peaks(self, peaks, plot_width=16, num=200):
        ax = self.axs[1]

        peak_surplus = len(self.peak_curves) - len(peaks)
        if peak_surplus > 0:
            self.clear_plot_elements(self.peak_curves)
            self.clear_plot_elements(self.peak_centers)

        for i, peak in enumerate(peaks):
            half_width = peak["width"] * plot_width
            x_new = np.linspace(
                start=peak["center"] - half_width,
                stop=peak["center"] + half_width,
                num=num,
            )
            y_new = GaussLorentz(x_new, **peak)
            try:
                (current_curve,) = self.peak_curves[i]
                (current_center,) = self.peak_centers[i]

                if np.array_equal(y_new, current_curve.get_ydata()):
                    continue

                current_curve.set_xdata(x_new)
                current_curve.set_ydata(y_new)

                current_center.set_xdata([peak["center"], peak["center"]])
                current_center.set_ydata([0, peak["amplitude"]])

            except IndexError:
                self.peak_curves.append(
                    ax.plot(
                        x_new,
                        y_new,
                        "-",
                        color="k",
                        alpha=0.3,
                        linewidth=2,
                    )
                )
                self.peak_centers.append(
                    ax.plot(
                        [peak["center"], peak["center"]],
                        [0, peak["amplitude"]],
                        "--",
                        color="k",
                        linewidth=1,
                    )
                )

    def plot_birs(self, birs: Dict[(int, float)], connect_mouse=False):

        if not self.birs:
            connect_mouse = True

        ax = self.axs[1]

        bir_values = list(birs.values())
        birs = np.reshape(bir_values, (len(bir_values) // 2, 2))

        bir_surplus = len(self.birs) - len(birs)
        if bir_surplus > 0:
            self.clear_plot_elements(self.birs)

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
                        alpha=0.5,
                        color="lightgray",
                        edgecolor=None,
                    )
                )

        if connect_mouse:
            self.connect_mouse_events(
                ax_id=1, objects=self.birs, identifier="interference"
            )

    def plot_subtraction_region(self, connect_mouse=False, **kwargs):
        if not self.subtraction_region:
            connect_mouse = True

        left, right = kwargs.get("subtraction_region")
        ax = self.axs[0]

        try:
            region = self.subtraction_region[0]
            coordinates = construct_polygon_coordinates(left, right)

            if np.array_equal(coordinates, region.get_xy()):
                return

            region.set_xy(coordinates)  # Replace old bir

        except IndexError:
            self.subtraction_region.append(
                ax.axvspan(
                    left,
                    right,
                    alpha=0.5,
                    color="lightgray",
                    edgecolor=None,
                )
            )
        if connect_mouse:
            self.connect_mouse_events(
                ax_id=0,
                objects=self.subtraction_region,
                identifier="subtraction",
            )

    def connect_mouse_events(self, ax_id: int, objects, identifier: str):

        mouse_connections = self.mouse_connections[identifier]

        for connection in mouse_connections:
            self.fig.canvas.mpl_disconnect(connection)

        ax = self.axs[ax_id]

        plot_interaction = drag_polygons(
            ax=ax,
            polygons=objects,  # drag_polygons=[1, 2]
            identifier=identifier,
        )
        self.plot_interactions[identifier] = plot_interaction

        events = ("button_press_event", "button_release_event", "motion_notify_event")
        actions = ("on_click", "on_release", "on_motion")

        for event, action in zip(events, actions):
            mouse_connections.append(
                self.fig.canvas.mpl_connect(event, getattr(plot_interaction, action))
            )
