from typing import Protocol


class Plot(Protocol):
    def update(self):
        ...

    def plot_lines(self):
        ...

    def plot_birs(self):
        ...
