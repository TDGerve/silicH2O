import blinker as bl

from ..spectral_processing import Sample_controller
from ..interface import Gui, GUI_state

from typing import List
import pathlib


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_samples_removed = bl.signal("samples removed")
    on_save_project_as = bl.signal("save project as")

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

    def save_project_as(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem

        self.sample_controller.save_project_as(filepath=filepath, name=name)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)

        self.on_save_project_as.connect(self.save_project_as)
