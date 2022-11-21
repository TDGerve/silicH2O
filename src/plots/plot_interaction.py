import numpy as np
from matplotlib.patches import Polygon

from typing import List
from enum import Enum, auto

import blinker as bl

on_settings_change = bl.signal("settings change")


class drag(Enum):
    LEFT = auto()
    RIGHT = auto()
    BOTH = auto()


def construct_polygon_coordinates(xmin, xmax):
    return np.array([[xmin, 0.0], [xmin, 1.0], [xmax, 1.0], [xmax, 0.0], [xmin, 0.0]])


class drag_polygons:
    def __init__(
        self,
        ax,
        polygons: List[Polygon],
        drag_polygons: List[int],
    ):

        self.ax = ax
        self.polygons = polygons
        self.drag_polygons = drag_polygons  # Drag these entire polygons, for al others only the left and right borders will be dragged

        self.dragging = None
        self.width = None

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

        if not self.dragging or not event.xdata:
            return

        buffer = 5
        x_new = event.xdata
        id = self.dragging

        if id[1] in [drag.LEFT, drag.BOTH]:
            previous_polygon = self.polygons[id[0] - 1]
            x_coordinates = [c[0] for c in previous_polygon.get_xy()]
            x_min = max(x_coordinates) + buffer
            if id[1] == drag.LEFT:
                current_polygon = self.polygons[id[0]]
                x_coordinates = [c[0] for c in current_polygon.get_xy()]
                x_max = max(x_coordinates) - buffer
        if id[1] in [drag.RIGHT, drag.BOTH]:
            next_polygon = self.polygons[id[0] + 1]
            x_coordinates = [c[0] for c in next_polygon.get_xy()]
            x_max = min(x_coordinates) - buffer
            if id[1] == drag.RIGHT:
                current_polygon = self.polygons[id[0]]
                x_coordinates = [c[0] for c in current_polygon.get_xy()]
                x_min = min(x_coordinates) + buffer

        if id == (0, drag.LEFT):
            x_min = 0
        elif id == (5, drag.RIGHT):
            x_max = np.Inf

        if id[1] != drag.BOTH:

            x_new = np.clip(x_new, a_min=x_min, a_max=x_max)

            if id[1] == drag.LEFT:

                x_right = max(x_coordinates)
                new_coordinates = construct_polygon_coordinates(
                    int(x_new), int(x_right)
                )
                current_polygon.set_xy(new_coordinates)
            elif id[1] == drag.RIGHT:
                x_left = min(x_coordinates)
                new_coordinates = construct_polygon_coordinates(int(x_left), int(x_new))
                current_polygon.set_xy(new_coordinates)
        else:
            current_polygon = self.polygons[id[0]]
            x_coordinates = [c[0] for c in current_polygon.get_xy()]

            half_width = self.width / 2
            x_left = np.clip(x_new - half_width, x_min, x_max)
            x_right = np.clip(x_left + half_width * 2, x_min, x_max)
            new_coordinates = construct_polygon_coordinates(int(x_left), int(x_right))
            current_polygon.set_xy(new_coordinates)

        self.send_bir_change(id)

    def on_release(self, event):

        self.dragging = None
        self.width = None

    def find_neighbor_object(self, event, distance_threshold=3):
        """
        Find lines around mouse position
        """
        drag_options = [drag.LEFT, drag.RIGHT]

        object_id = None
        for i, polygon in enumerate(self.polygons):
            x_coordinates = [c[0] for c in polygon.get_xy()]
            xmin = min(x_coordinates)
            xmax = max(x_coordinates)
            if i in self.drag_polygons:
                if xmin < event.xdata < xmax:
                    object_id = (i, drag.BOTH)
                    self.width = xmax - xmin

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

        new_from = min(x_coordinates)
        new_to = max(x_coordinates)
        new_settings = {str(id[0] * 2): int(new_from), str(id[0] * 2 + 1): int(new_to)}

        on_settings_change.send("plot", birs=new_settings)
