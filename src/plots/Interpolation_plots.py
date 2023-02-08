from typing import Dict

import numpy as np

from ..interface.screens import Screen
from .plot_interaction import construct_polygon_coordinates, drag_polygons
from .plots import Single_plot


class Interpolation_plot(Single_plot):
    def __init__(self, screen: Screen):

        super().__init__(screen, xlabel="Raman shift cm$^{-1}$", ylabel="Counts")
        self.setup_ax(limits=(0, 4000))

        self.birs = []
        self.interpolated_lines = []
        self.mouse_connections = []
        self.plot_interactions = []

    def draw_plot(self, **kwargs):

        birs = kwargs.pop("birs")

        self.plot_lines(**kwargs)
        self.plot_birs(birs)

        self.fig.canvas.draw_idle()

    def plot_lines(
        self, x: np.ndarray, spectra: Dict[str, np.ndarray], *args, **kwargs
    ):
        plot_items = "interpolation_spectrum"

        keys = list(spectra.keys())
        for key in keys:
            if key not in plot_items:
                _ = spectra.pop(key)

        return super().plot_lines(x, spectra, *args, **kwargs)

    def plot_interpolation(self, x, y, interpolation_regions, *args, **kwargs):

        color = self.colors.by_key()["color"][3]
        data = []
        for (x_min, x_max) in interpolation_regions:
            mask = (x < x_max) & (x > x_min)
            data.append(*[x[mask], y[mask], color])

        self.interpolated_lines = self.ax.plot(*data, label="interpolated")

    def clear_interpolations(self):
        for line in self.interpolated_lines:
            line.remove()
        self.interpolated_lines = []

    def clear_figure(self):
        self.clear_plot_elements(self.birs)
        self.clear_interpolations()
        super().clear_figure()

    def plot_birs(self, birs: Dict[(int, float)], connect_mouse=False):

        if not self.birs:
            connect_mouse = True

        ax = self.ax

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
            self.connect_mouse_events(objects=self.birs, identifier="interpolation")

    def connect_mouse_events(self, objects, identifier: str):

        mouse_connections = self.mouse_connections

        for connection in mouse_connections:
            self.fig.canvas.mpl_disconnect(connection)

        ax = self.ax

        plot_interaction = drag_polygons(ax=ax, polygons=objects, identifier=identifier)
        self.plot_interactions = plot_interaction

        events = ("button_press_event", "button_release_event", "motion_notify_event")
        actions = ("on_click", "on_release", "on_motion")

        for event, action in zip(events, actions):
            mouse_connections.append(
                self.fig.canvas.mpl_connect(event, getattr(plot_interaction, action))
            )
