import tkinter as tk
from typing import Any, Dict

import blinker as bl

from ..plots import (
    Baseline_correction_plot,
    Calibration_plot,
    Interpolation_plot,
    Plot,
    Subtraction_plot,
)
from .GUIS import GUI_state
from .main_window import Main_window
from .windows import Calibration_window

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
        self.window: Main_window = Main_window(
            title=title, variables=self.variables, widgets=self.widgets
        )

        self.create_plots()

        self.state = GUI_state.DISABLED

    def set_state(self, state: GUI_state) -> None:
        self.state = state

    def clear_variables(self):
        for group, variables in self.variables.items():
            for name, var in variables.items():
                try:
                    var.set("")
                except tk.TclError:
                    var.set(False)

                try:
                    widget = self.widgets[group][name]
                    widget.delete(0, tk.END)
                    widget.insert(0, "")
                except (KeyError, AttributeError):
                    pass

    def update_variables(self, **kwargs) -> None:
        for name, values in kwargs.items():
            if name not in self.variables.keys():
                return
            if values is None:
                return

            for var_name, value in values.items():
                variable = self.variables[name][var_name]

                try:
                    widget = self.widgets[name][var_name]

                    widget.focus_set()
                    widget.delete(0, tk.END)
                    widget.insert(0, f"{value}")

                except (KeyError, AttributeError):
                    pass
                try:
                    variable.set(value)
                except TypeError:
                    variable.set(str(value))

                self.window.focus_set()

    def activate_widgets(self) -> None:
        for frame in self.widgets.values():
            for widget in frame.values():
                # for w in widgets:
                try:
                    widget.configure(state=tk.NORMAL)
                except AttributeError:
                    for i in widget:
                        i.configure(state=tk.NORMAL)

    def calibration_window_popup(self):
        calibration = Calibration_window(
            parent=self.window,
            title="Calibration",
            widgets=self.widgets,
            variables=self.variables,
        )
        self.plots["calibration"] = Calibration_plot(self.window.screen)
        self.set_plot_background_color(plot=self.plots["calibration"])
        calibration.draw_plot(self.plots["calibration"])

    def create_plots(self):
        self.plots["baseline"] = Baseline_correction_plot(self.window.screen)
        self.plots["interpolation"] = Interpolation_plot(self.window.screen)
        self.plots["interference"] = Subtraction_plot(self.window.screen)
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
