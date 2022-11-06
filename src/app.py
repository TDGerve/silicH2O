import tkinter as tk

from typing import List


from .spectrum_processing import sample_processing
from .sample_updates import sample_info, status
from .plots import Plot

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


class raman_app:
    def __init__(self):
        self.root = tk.Tk()

        self.sample_info = sample_info

        self.samples = sample_processing(self.sample_info)
        self.plots: List[Plot] = None

        self.sample_info.set_idx(5)

    def update(self):

        for plot in self.plots:
            plot.update()

        self.samples.update()

    def add_plot(self, plot):
        self.plots.append(plot)

    def set_sample(self, idx):
        if self.samples.sample_idx == idx:
            return
        self.sample.idx = idx
        self.sample.set_state(status.SAMPLE_CHANGE)
        self.update()

    def run(self):
        self.root.mainloop()
