import sys

from .sample_handlers import Sample_handler
from .event_management import Calculation_listener, Database_listener, Plot_listener

from .interface import App_interface


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


class Raman_app:
    def __init__(self, title):

        self.samples = Sample_handler()
        self.gui = App_interface(title=title)

        self.calulcation_listener = Calculation_listener(self.samples, self.gui)
        self.database_listener = Database_listener(self.samples, self.gui)
        self.plot_listener = Plot_listener(self.gui.main_window, self.gui.plots)

        self.gui.create_plots()

    def run(self) -> None:
        # Make sure the matplotlib backend also closes
        self.gui.main_window.protocol("WM_DELETE_WINDOW", sys.exit)
        self.gui.main_window.mainloop()


def run_raman_app():

    app = Raman_app()
    app.run()
