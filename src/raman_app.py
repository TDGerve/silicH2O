import sys

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
        # Make sure the matplotlib backend also closes
        self.gui.main_window.protocol("WM_DELETE_WINDOW", sys.exit)
        self.gui.main_window.mainloop()


def run_raman_app():

    app = Raman_app()
    app.run()
