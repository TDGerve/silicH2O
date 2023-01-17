import os
import pathlib
import tarfile
from typing import List, Optional

import blinker as bl
import pandas as pd

from .. import app_settings
from ..interface import Gui, GUI_state
from ..spectral_processing import Sample_controller


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_load_project = bl.signal("load project")

    on_samples_removed = bl.signal("samples removed")

    on_save_project_as = bl.signal("save project as")
    on_export_results = bl.signal("export results")

    def __init__(self, sample_controller: Sample_controller, gui: Gui):
        self.sample_controller = sample_controller
        self.gui = gui

        self.subscribe_to_signals()

    def remove_samples(self, *args, index: List[int]) -> None:
        self.sample_controller.remove_samples(index)

        names = list(self.sample_controller.names)
        self.gui.update_variables(sample_navigation={"samplelist": names})

    def add_samples(self, *args, files: List[str]) -> None:

        previous_names = list(self.sample_controller.names)
        names = get_names_from_files(files, previous_names=previous_names)
        total_names = previous_names + names

        self.sample_controller.read_files(files, names=names)

        self.gui.update_variables(sample_navigation={"samplelist": total_names})

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def save_project_as(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem

        self.sample_controller.save_project_as(filepath=filepath, name=name)

    def export_results(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem
        folder = filepath.parents[0]

        self.sample_controller.export_results(folder=folder, name=name)

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

            self.sample_controller.__init__()
            self.sample_controller.read_files(
                spectrum_files, names=names, settings=settings_dict
            )

        self.sample_controller.project = filepath
        self.gui.update_variables(sample_navigation={"samplelist": names})

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)

        self.on_save_project_as.connect(self.save_project_as)
        self.on_load_project.connect(self.load_project)
        self.on_export_results.connect(self.export_results)


def get_names_from_files(files: List, previous_names: List[str] = []) -> List:
    separator = app_settings.general["name_separator"]
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

    names = remove_duplicate_names(names, previous_names=previous_names)

    return names


def remove_duplicate_names(
    names: List[str], previous_names: List[str] = []
) -> List[str]:

    new_names = names.copy()
    if len(previous_names) > 0:
        previous_names = [name[:-2] if "@" in name else name for name in previous_names]

    for i, _ in enumerate(new_names):
        occurences = (new_names + previous_names).count(new_names[i])
        if occurences < 2:
            continue
        new_names[i] = f"{new_names[i]}@{occurences - 1}"

    return new_names


# def get_settings(names: List) -> pd.DataFrame:

#     baseline_correction, interpolation = app_settings.process

#     birs = pd.concat([baseline_correction["birs"].copy()] * len(names), axis=1).T
#     birs.index = names

#     interpolation_regions = pd.concat(
#         [interpolation["regions"].copy()] * len(names), axis=1
#     ).T
#     interpolation_regions.index = names

#     settings_df = pd.DataFrame(
#         {
#             "baseline_smoothing": baseline_correction["smoothing"],
#             "interpolation": interpolation["use"],
#             "interpolation_smoothing": interpolation["smoothing"],
#         },
#         index=names,
#     )

#     return settings_df, birs, interpolation_regions


# def create_results_df(names: List) -> pd.DataFrame:
#     colnames = ["SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR"]
#     return pd.DataFrame(index=names, columns=colnames, dtype=float)
