import tkinter as tk

from typing import Dict

from .main_window import Main_window
from .plots import Plot


class App_interface:
    def __init__(
        self,
        title: str,
        variables: Dict[str, any],
        widgets: Dict[str, any],
        plots: Dict[str, Plot],
    ):

        self.main_window: tk.Tk = Main_window(title=title)
        self.main_window.create_navigation_frame(variables, widgets)

        self.main_window.create_main_frame()
        self.main_window.create_tabs(variables, widgets, plots)

        self.set_plot_background_color(plots)

        self.main_window.create_menus()

    def set_plot_background_color(self, plots):
        # calculate background color to something matplotlib understands
        background_color = tuple(
            (c / 2**16 for c in self.main_window.background_color)
        )

        for plot in plots.values():
            plot.fig.patch.set_facecolor(background_color)
