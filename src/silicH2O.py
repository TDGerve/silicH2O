import sys

import blinker as bl

from .event_management import (
    Calculation_listener,
    Calibration_listener,
    Database_listener,
    Gui_listener,
    Plot_listener,
)
from .interface import App_interface
from .spectral_processing import Calibration_processor, Database_controller

on_clean_temp_files = bl.signal("clean temp files")


class silicH2O:
    def __init__(self):

        self.samples = Database_controller()
        self.calibration = Calibration_processor()
        self.gui = App_interface(title="Silic-H2O by Thomas van Gerve")

        self.database_listener = Database_listener(
            database_controller=self.samples, calibration=self.calibration
        )
        self.calulcation_listener = Calculation_listener(
            database_controller=self.samples
        )
        self.calibration_listener = Calibration_listener(
            database_controller=self.samples, calibration=self.calibration
        )

        self.plot_listener = Plot_listener(self.gui.plots)
        self.gui_listener = Gui_listener(self.gui)

    def run(self) -> None:

        on_clean_temp_files.send()
        self.gui.main_window.protocol("WM_DELETE_WINDOW", self.close)
        self.gui.main_window.mainloop()

    def close(self):
        """
        Runs on close
        """
        # self.clean_files()
        on_clean_temp_files.send()
        # close everything
        sys.exit()
