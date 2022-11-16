import tkinter as tk

from typing import Dict, Protocol
import blinker as bl
import numpy as np

from .main_window import Main_window
from .GUIs import GUI_state
from .plots import Plot, Baseline_correction_plot

on_plots_initialised = bl.signal("plots initialised")


class App_interface:
    def __init__(
        self,
        title: str,
    ):
        self.plots: Dict[Plot] = {}
        self.variables: Dict[str, any] = {}
        self.widgets: Dict[str, any] = {}
        # rRot
        self.main_window: tk.Tk = Main_window(title=title)
        # Root frames
        self.main_window.create_navigation_frame(self.variables, self.widgets)

        # Tabs
        self.main_window.populate_tabs(self.variables, self.widgets)

        # Menus
        self.main_window.create_menus()

        self.state = GUI_state.DISABLED

    def set_state(self, state: GUI_state) -> None:
        self.state = state

    def update_variables(self, **kwargs) -> None:
        for name, values in kwargs.items():
            if name not in self.variables.keys():
                return
            if name == "birs":
                for index, value in values.items():
                    variable = self.variables["birs"][int(index)]
                    variable.set(int(value))
            else:
                for variable, value in zip(self.variables[name], values):
                    variable.set(value)

    def activate_widgets(self) -> None:
        for widgets in self.widgets.values():
            for w in widgets:
                try:
                    w.configure(state=tk.NORMAL)
                except AttributeError:
                    for i in w:
                        i.configure(state=tk.NORMAL)

    def create_plots(self):
        self.plots["baseline_correction"] = Baseline_correction_plot(
            self.main_window.screen
        )
        on_plots_initialised.send("plots created")
