import sys

import blinker as bl

from .event_management import (
    Calculation_listener,
    Database_listener,
    Gui_listener,
    Plot_listener,
)
from .interface import App_interface
from .spectral_processing import Database_controller

on_clean_temp_files = bl.signal("clean temp files")


class Raman_app:
    def __init__(self, title):

        self.samples = Database_controller()
        self.gui = App_interface(title=title)

        self.calulcation_listener = Calculation_listener(self.samples, self.gui)
        self.database_listener = Database_listener(self.samples, self.gui)
        self.plot_listener = Plot_listener(self.gui.plots)
        self.gui_listener = Gui_listener(self.gui)

    def run(self) -> None:

        on_clean_temp_files.send()
        self.gui.window.protocol("WM_DELETE_WINDOW", self.close)
        self.gui.window.mainloop()

    def close(self):
        """
        Runs on close
        """

        # self.clean_files()
        on_clean_temp_files.send()
        # close everything
        sys.exit()

    # def clean_files(self):

    #     file = pathlib.Path(__file__)
    #     tempdir = file.parents[0] / "temp"

    #     # delete temporary files
    #     for root, dirs, files in os.walk(tempdir):

    #         for f in files:
    #             os.unlink(os.path.join(root, f))

    #         for d in dirs:
    #             try:
    #                 shutil.rmtree(os.path.join(root, d))
    #             except PermissionError:
    #                 time.sleep(0.5)
    #                 shutil.rmtree(os.path.join(root, d))


def run_raman_app():

    app = Raman_app()
    app.run()
