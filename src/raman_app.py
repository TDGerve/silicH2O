import sys
import blinker as bl

import tkinter as tk
from typing import Dict

from .sample_handlers import Sample_handler
from .event_management import Calculation_listener, Database_listener, Plot_listener

from .GUI.plots import Plot, Baseline_correction_plot
from .GUI import App_interface
from .app import App_state


"""
Decouple by with an event manager:

Blinker:
https://blinker.readthedocs.io/en/stable/#decoupling-with-named-signals

Pymitter:
https://github.com/riga/pymitter

Pydispatcher:
https://mcfletch.github.io/pydispatcher/

https://stackoverflow.com/questions/1092531/which-python-packages-offer-a-stand-alone-event-system

"""

on_plots_initialised = bl.signal("plots initialised")


class Raman_app:
    def __init__(self, title):

        self.samples = Sample_handler()
        self.variables: Dict[str, any] = {}
        self.widgets: Dict[str, any] = {}
        self.plots: Dict[Plot] = {}

        self.gui = App_interface(
            title=title,
            variables=self.variables,
            widgets=self.widgets,
            plots=self.plots,
        )

        self.calulcation_listener = Calculation_listener(self.samples)
        self.database_listener = Database_listener(self.samples, self)
        self.plot_listener = Plot_listener(self.gui.main_window, self.plots)

        self.create_plots()

        self.state = App_state.DISABLED

    def set_state(self, state: App_state) -> None:
        self.state = state

    def update_variables(self, **kwargs) -> None:

        for name, value in kwargs.items():
            if name not in self.variables.keys():
                return
            self.variables[name].set(value)

    def activate_widgets(self) -> None:
        for widgets in self.widgets.values():
            for w in widgets:
                w.configure(state=tk.NORMAL)

    def create_plots(self):
        self.plots["baseline_correction"] = Baseline_correction_plot(
            self.gui.main_window.screen
        )
        on_plots_initialised.send("plots created")

    def run(self) -> None:
        # Make sure the matplotlib backend also closes
        self.gui.main_window.protocol("WM_DELETE_WINDOW", sys.exit)
        self.gui.main_window.mainloop()


def run_raman_app():

    app = Raman_app()
    app.run()
