import sys, shutil, os, pathlib, atexit

from .spectral_processing import Sample_controller
from .event_management import Calculation_listener, Database_listener, Plot_listener

from .interface import App_interface


class Raman_app:
    def __init__(self, title):

        self.samples = Sample_controller()
        self.gui = App_interface(title=title)

        self.calulcation_listener = Calculation_listener(self.samples, self.gui)
        self.database_listener = Database_listener(self.samples, self.gui)
        self.plot_listener = Plot_listener(self.gui.plots)

    def run(self) -> None:

        self.clean_files()
        self.gui.window.protocol("WM_DELETE_WINDOW", self.close)
        self.gui.window.mainloop()

    def close(self):
        """
        Runs on close
        """

        self.clean_files()
        # close everything
        sys.exit()

    def clean_files(self):

        file = pathlib.Path(__file__)
        tempdir = file.parents[0] / "temp"

        # delete temporary files
        for root, dirs, files in os.walk(tempdir):

            for f in files:
                os.unlink(os.path.join(root, f))

            for d in dirs:
                shutil.rmtree(os.path.join(root, d))


def run_raman_app():

    app = Raman_app()
    app.run()
