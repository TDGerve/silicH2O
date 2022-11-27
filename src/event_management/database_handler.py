import os
import blinker as bl
import pandas as pd

from ..spectral_processing import Sample_controller
from ..interface import Gui, GUI_state
from .. import settings

from typing import List
import pathlib, tarfile


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_samples_removed = bl.signal("samples removed")
    on_save_project_as = bl.signal("save project as")
    on_load_project = bl.signal("load project")

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def remove_samples(self, *args, index: List[int]) -> None:
        self.sample_controller.remove_samples(index)

        names = list(self.sample_controller.names)
        self.gui.update_variables(sample_navigation=[names])

    def add_samples(self, *args, files: List[str]) -> None:

        names = get_names_from_files(files)

        self.sample_controller.read_files(files, names=names)

        self.gui.update_variables(sample_navigation=[names])

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def save_project_as(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem

        self.sample_controller.save_project_as(filepath=filepath, name=name)

    def load_project(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)

        with tarfile.open(filepath, "r") as tar:

            general_settings = pd.read_csv(
                tar.extractfile("settings.csv"), index_col=[0]
            )
            baseline_regions = pd.read_csv(
                tar.extractfile("baseline_regions.csv"), index_col=[0], header=[0, 1]
            )
            interpolation_regions = pd.read_csv(
                tar.extractfile("interpolation_regions.csv"),
                index_col=[0],
                header=[0, 1],
            )

            settings_dict = {
                "general": general_settings,
                "baseline_regions": baseline_regions,
                "interpolation_regions": interpolation_regions,
            }

            filenames = [member.name for member in tar]
            spectra = [name for name in filenames if name.endswith(".sp")]
            names = [os.path.basename(file)[:-3] for file in spectra]

            spectrum_files = [tar.extractfile(spectrum) for spectrum in spectra]

            self.sample_controller.read_files(
                spectrum_files, names=names, settings=settings_dict
            )

        self.gui.update_variables(sample_navigation=[names])

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)

        self.on_save_project_as.connect(self.save_project_as)
        self.on_load_project.connect(self.load_project)


def get_names_from_files(files: List) -> List:
    separator = settings.general["name_separator"]
    names = []

    for file in files:
        try:
            name = os.path.basename(file)
        except TypeError:
            name = file.name
        if separator not in name:
            names.append(name)
        else:
            names.append(name[: name.index(separator)])

    return names
