from enum import Enum, auto
from typing import List

import blinker as bl
import numpy as np
from matplotlib.patches import Polygon

on_settings_change = bl.signal("settings change")
on_display_message = bl.signal("display message")


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
    ):

        self.ax = ax
        self.polygons = polygons

        self.dragging = None
        self.width = None
        self.mouse_location = None
        self.mouse_location = None

    def on_click(self, event):
        """
        calback method for left mouseclick events
        """

        if (event.button == 1) and (event.inaxes == self.ax):
            object_id = self.find_neighbor_object(event)
            if object_id:
                self.dragging = object_id
                self.mouse_location = event.xdata

    def on_motion(self, event):
        """
        callback method for mouse motion events

        """
        object_not_found = (not self.dragging) or (not event.xdata)

        if object_not_found:
            return

        movement_too_small = abs(event.xdata - self.mouse_location) < 1
        if movement_too_small:
            return

        buffer = 5
        x_new = event.xdata
        poly_id = self.dragging

        if poly_id[1] in [drag.LEFT, drag.BOTH]:
            if poly_id[0] == 0:
                x_min = 0
            else:
                previous_polygon = self.polygons[poly_id[0] - 1]
                x_coordinates = [c[0] for c in previous_polygon.get_xy()]
                x_min = max(x_coordinates) + buffer
            if poly_id[1] == drag.LEFT:
                current_polygon = self.polygons[poly_id[0]]
                x_coordinates = [c[0] for c in current_polygon.get_xy()]
                x_max = max(x_coordinates) - buffer

        if poly_id[1] in [drag.RIGHT, drag.BOTH]:
            if poly_id[0] == (len(self.polygons) - 1):
                x_max = np.Inf
            else:
                next_polygon = self.polygons[poly_id[0] + 1]
                x_coordinates = [c[0] for c in next_polygon.get_xy()]
                x_max = min(x_coordinates) - buffer
            if poly_id[1] == drag.RIGHT:
                current_polygon = self.polygons[poly_id[0]]
                x_coordinates = [c[0] for c in current_polygon.get_xy()]
                x_min = min(x_coordinates) + buffer

        if poly_id[1] != drag.BOTH:
            x_new = np.clip(x_new, a_min=x_min, a_max=x_max)

            if poly_id[1] == drag.LEFT:

                x_right = max(x_coordinates)
                new_coordinates = construct_polygon_coordinates(
                    int(x_new), int(x_right)
                )
                current_polygon.set_xy(new_coordinates)
            elif poly_id[1] == drag.RIGHT:
                x_left = min(x_coordinates)
                new_coordinates = construct_polygon_coordinates(int(x_left), int(x_new))
                current_polygon.set_xy(new_coordinates)
        else:
            current_polygon = self.polygons[poly_id[0]]
            x_coordinates = [c[0] for c in current_polygon.get_xy()]
            left_old = min(x_coordinates)

            movement = x_new - self.mouse_location
            self.mouse_location = self.mouse_location + movement

            x_left = np.clip(left_old + movement, x_min, x_max)
            x_right = np.clip(x_left + self.width, x_min, x_max)
            new_coordinates = construct_polygon_coordinates(int(x_left), int(x_right))
            current_polygon.set_xy(new_coordinates)

        self.send_bir_change(poly_id)

    def on_release(self, event):

        self.dragging = None
        self.width = None
        self.mouse_location = None
        self.mouse_location = None

    def find_neighbor_object(self, event, border_threshold: int = 5):
        """
        Find lines around mouse position
        """
        drag_options = [drag.LEFT, drag.RIGHT]

        object_id = None
        for i, polygon in enumerate(self.polygons):
            x_coordinates = [c[0] for c in polygon.get_xy()]
            xmin = min(x_coordinates)
            xmax = max(x_coordinates)

            self.width = xmax - xmin

            width_threshold = [self.width * 0.1, 10][self.width > 30]
            border_threshold_new = min(border_threshold, width_threshold)

            if (xmin + width_threshold) < event.xdata < (xmax - width_threshold):
                object_id = (i, drag.BOTH)
                return object_id

            else:
                for j, x in enumerate([xmin, xmax]):
                    distance = abs(event.xdata - x)
                    if distance < border_threshold_new:
                        object_id = (i, drag_options[j])
                        return object_id

    def send_bir_change(self, id):
        if not id:
            return
        current_bir = self.polygons[id[0]]
        x_coordinates = [c[0] for c in current_bir.get_xy()]

        new_from = min(x_coordinates)
        new_to = max(x_coordinates)

        new_settings = {
            f"bir_{id[0] * 2}": int(new_from),
            f"bir_{id[0] * 2 + 1}": int(new_to),
        }

        on_settings_change.send("plot", baseline=new_settings)
