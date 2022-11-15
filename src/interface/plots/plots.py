import numpy as np
from itertools import product

from typing import Protocol, Dict, List
from matplotlib.patches import Polygon
from enum import Enum, auto
import blinker as bl

from .double_plots import Double_plot
from ..screens import Screen

on_settings_change = bl.signal("settings change")


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def plot_birs(self):
        ...


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

        for i, (ax, (left_boundary, right_boundary)) in enumerate(
            product(self.axs, birs)
        ):
            try:
                current_bir = self.birs[i]
                coordinates = construct_bir_coordinates(left_boundary, right_boundary)
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
        print(len(self.birs))
        # self.birs = bir_plots
        # self.fig.canvas.draw_idle()
        if connect_mouse:
            self.connect_mouse_events()

    def connect_mouse_events(self):
        drag_ax1 = drag_polygons(
            self.fig, ax=self.axs[0], polygons=self.birs[:5], drag_polygons=[1, 2]
        )
        drag_ax2 = drag_polygons(
            self.fig, ax=self.axs[1], polygons=self.birs[5:], drag_polygons=[1, 2]
        )
        self.mouse_connections += [drag_ax1, drag_ax2]

        for ax in [drag_ax1, drag_ax2]:
            self.fig.canvas.mpl_connect("button_press_event", ax.on_click)
            self.fig.canvas.mpl_connect("button_release_event", ax.on_release)
            self.fig.canvas.mpl_connect("motion_notify_event", ax.on_motion)


class drag(Enum):
    LEFT = auto()
    RIGHT = auto()
    BOTH = auto()


def construct_bir_coordinates(xmin, xmax):
    return np.array([[xmin, 0.0], [xmin, 1.0], [xmax, 1.0], [xmax, 0.0], [xmin, 0.0]])


class drag_polygons:
    def __init__(
        self,
        fig,
        ax,
        polygons: List[Polygon],
        drag_polygons: List[int],
    ):
        self.fig = fig
        self.ax = ax
        self.polygons = polygons
        self.drag_polygons = drag_polygons  # Drag these entire polygons, for al others only the left and right borders will be dragged

        self.dragging = None

    def on_click(self, event):
        """
        calback method for left mouseclick events
        """

        if (event.button == 1) and (event.inaxes == self.ax):
            object_id = self.find_neighbor_object(event)
            if object_id:
                self.dragging = object_id

    def on_motion(self, event):
        """
        callback method for mouse motion events

        """

        if not self.dragging:
            return

        buffer = 10
        x_new = event.xdata
        id = self.dragging

        if id[1] in [drag.LEFT, drag.BOTH]:
            previous_bir = self.polygons[id[0] - 1]
            x_coordinates = [c[0] for c in previous_bir.get_xy()]
            x_min = max(x_coordinates) + buffer
            if id[1] == drag.LEFT:
                current_bir = self.polygons[id[0]]
                x_coordinates = [c[0] for c in current_bir.get_xy()]
                x_max = max(x_coordinates) - buffer
        if id[1] in [drag.RIGHT, drag.BOTH]:
            next_bir = self.polygons[id[0] + 1]
            x_coordinates = [c[0] for c in next_bir.get_xy()]
            x_max = min(x_coordinates) - buffer
            if id[1] == drag.RIGHT:
                current_bir = self.polygons[id[0]]
                x_coordinates = [c[0] for c in current_bir.get_xy()]
                x_min = min(x_coordinates) + buffer

        if id == (0, drag.LEFT):
            x_min = 0
        elif id == (5, drag.RIGHT):
            x_max = np.Inf

        if id[1] != drag.BOTH:

            x_new = np.clip(x_new, a_min=x_min, a_max=x_max)

            if id[1] == drag.LEFT:

                x_right = max(x_coordinates)
                new_coordinates = construct_bir_coordinates(int(x_new), int(x_right))
                current_bir.set_xy(new_coordinates)
            elif id[1] == drag.RIGHT:
                x_left = min(x_coordinates)
                new_coordinates = construct_bir_coordinates(int(x_left), int(x_new))
                current_bir.set_xy(new_coordinates)
        else:
            current_bir = self.polygons[id[0]]
            x_coordinates = [c[0] for c in current_bir.get_xy()]
            half_width = (max(x_coordinates) - min(x_coordinates)) / 2
            x_left = np.clip(x_new - half_width, x_min, x_max)
            x_right = np.clip(x_new + half_width, x_min, x_max)
            new_coordinates = construct_bir_coordinates(int(x_left), int(x_right))
            current_bir.set_xy(new_coordinates)

        self.send_bir_change(id)
        self.fig.canvas.draw_idle()

    def on_release(self, event):

        self.dragging = None

    def find_neighbor_object(self, event):
        """
        Find lines around mouse position
        """
        drag_options = [drag.LEFT, drag.RIGHT]
        distance_threshold = 5
        object_id = None
        for i, polygon in enumerate(self.polygons):
            x_coordinates = [c[0] for c in polygon.get_xy()]
            xmin = min(x_coordinates)
            xmax = max(x_coordinates)
            if i in self.drag_polygons:
                if xmin < event.xdata < xmax:
                    object_id = (i, drag.BOTH)

            else:
                for j, x in enumerate([xmin, xmax]):
                    distance = abs(event.xdata - x)
                    if distance < distance_threshold:
                        object_id = (i, drag_options[j])
        return object_id

    def send_bir_change(self, id):
        if not id:
            return
        current_bir = self.polygons[id[0]]
        x_coordinates = [c[0] for c in current_bir.get_xy()]
        if id[1] == drag.BOTH:

            new_from = min(x_coordinates)
            new_to = max(x_coordinates)
            new_settings = {str(id[0]): [new_from, new_to]}
        elif id[1] == drag.LEFT:
            new_from = min(x_coordinates)
            new_settings = {str(id[0]): [new_from, np.nan]}
        elif id[1] == drag.RIGHT:
            new_to = max(x_coordinates)
            new_settings = {str(id[0]): [np.nan, new_to]}

        on_settings_change.send("plot input", birs=new_settings)
