import blinker as bl
import tkinter as tk

from ..sample_handlers import Sample_handler
from ..app import App, App_state

from typing import List


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_samples_removed = bl.signal("samples removed")

    def __init__(self, sample_handler: Sample_handler, app: App):
        self.sample_handler = sample_handler
        self.app = app

        self.subscribe_to_signals()

    def remove_samples(self, *args, index: List[int]) -> None:
        self.sample_handler.remove_samples(index)

        names = list(self.sample_handler.names)
        self.app.update_variables(sample_list=names)

    def add_samples(self, *args, files: List[str]) -> None:

        self.sample_handler.read_files(files)

        names = list(self.sample_handler.names)
        self.app.update_variables(sample_list=names)

        if self.app.state == App_state.DISABLED:
            self.app.activate_widgets()
            self.app.set_state(App_state.ACTIVE)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)
