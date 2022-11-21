import tkinter as tk

from typing import Dict, Any
import blinker as bl

from .main_window import Main_window
from .GUIS import GUI_state
from ..plots import Plot, Baseline_correction_plot

on_plots_initialised = bl.signal("plots initialised")


class App_interface:
    def __init__(
        self,
        title: str,
    ):
        self.plots: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.widgets: Dict[str, Any] = {}
        # rRot
        self.window: tk.Tk = Main_window(
            title=title, variables=self.variables, widgets=self.widgets
        )

        self.create_plots()

        self.state = GUI_state.DISABLED

    def set_state(self, state: GUI_state) -> None:
        self.state = state

    def update_variables(self, **kwargs) -> None:
        for name, values in kwargs.items():
            if name not in self.variables.keys():
                return
            if name == "birs":

                repeat = []
                for index, value in values.items():
                    widget = self.widgets["birs"][int(index)]
                    # Hack to make sure, validation is triggered for the bir widets
                    widget.focus_set()

                    variable = self.variables["birs"][int(index)]
                    variable.set(int(value))

            else:
                for variable, value in zip(self.variables[name], values):
                    variable.set(value)

            self.window.focus()

    def activate_widgets(self) -> None:
        for widgets in self.widgets.values():
            for w in widgets:
                try:
                    w.configure(state=tk.NORMAL)
                except AttributeError:
                    for i in w:
                        i.configure(state=tk.NORMAL)

    def create_plots(self):
        self.plots["baseline_correction"] = Baseline_correction_plot(self.window.screen)
        self.add_plots()

    def add_plots(self):

        for name, plot in self.plots.items():
            frame = self.window.tabs.nametowidget(name)
            self.set_plot_background_color(plot)
            frame.draw_plot(plot)

    def set_plot_background_color(self, plot: Plot):
        # calculate background color to something matplotlib understands
        background_color = tuple((c / 2**16 for c in self.window.background_color))
        plot.fig.patch.set_facecolor(background_color)
