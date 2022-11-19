import blinker as bl
import tkinter as tk

from ..spectral_processing import Sample_controller
from ..interface import Gui, GUI_state

from typing import List


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_samples_removed = bl.signal("samples removed")

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def remove_samples(self, *args, index: List[int]) -> None:
        self.sample_controller.remove_samples(index)

        names = list(self.sample_controller.names)
        self.gui.update_variables(sample_navigation=[names])

    def add_samples(self, *args, files: List[str]) -> None:

        self.sample_controller.read_files(files)

        names = list(self.sample_controller.names)
        self.gui.update_variables(sample_navigation=[names])

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)
