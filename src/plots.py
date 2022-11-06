from typing import Protocol

import matplotlib.pyplot as plt


class Plot(Protocol):
    def update(self):
        ...

    def add_line(self):
        ...


class single_plot(Plot):
    def __init__(self, height, width):

        self.fig, self.ax = plt.subplots(figsize=(height, width))
        self.lines = []

    def update(self):
        pass

    def add_line(self, x, y, *args, **kwargs):
        line = self.ax.plot(x, y, "-" * args, **kwargs)
        self.lines.append(line)
