import glob
import os
import pathlib
import shutil
import tarfile
from typing import List, Optional

import blinker as bl
import numpy as np
import pandas as pd
import pyarrow as pa

from .. import app_configuration
from ..interface import Gui, GUI_state
from ..spectral_processing import Database_controller

temp_folder = pathlib.Path(__file__).parents[1] / "temp"


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_load_project = bl.signal("load project")
    on_new_project = bl.signal("new project")

    on_samples_removed = bl.signal("samples removed")

    on_save_all = bl.signal("save all")
    on_save_sample = bl.signal("save sample")

    on_save_project = bl.signal("save project")
    on_export_results = bl.signal("export results")

    on_clear_plot = bl.signal("clear plot")
    on_plot_change = bl.signal("refresh plot")
    on_display_message = bl.signal("display message")

    on_Ctrl_s = bl.signal("ctrl+s")

    def __init__(self, database_controller: Database_controller, gui: Gui):
        self.database_controller = database_controller
        self.gui = gui

        self.subscribe_to_signals()

    def remove_samples(self, *args, index: List[int]) -> None:

        if self.database_controller.has_project:
            names = self.database_controller.names[index]
            if isinstance(names, str):
                names = [names]
            self.remove_data(names=names)

        self.database_controller.remove_samples(index)

        names = list(self.database_controller.names)
        self.gui.update_variables(sample_navigation={"samplelist": names})

    def remove_data(self, names: List[str]):

        temp_path = temp_folder / self.database_controller.project.stem
        temp_datapath = temp_path / "data"

        for name in names:
            filepath = temp_datapath / f"{name}.sp"
            filepath.unlink()

    def add_samples(self, *args, files: List[str]) -> None:

        previous_names = list(self.database_controller.names)
        names = get_names_from_files(files, previous_names=previous_names)
        total_names = previous_names + names

        self.database_controller.read_files(files, names=names)

        self.gui.update_variables(sample_navigation={"samplelist": total_names})

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def add_interference(self, *args, file: str):

        self.database_controller.add_interference(file)

    def new_project(self, *args):

        self.database_controller.__init__()
        self.gui.clear_variables()
        self.on_clear_plot.send("new project")

    def save_project(self, *args, filepath: Optional[str] = None):

        self.on_display_message.send(message="saving project...", duration=None)

        if filepath is not None:
            filepath = pathlib.Path(filepath)
            name = filepath.stem
        else:
            try:
                filepath = self.database_controller.project
                name = filepath.stem
            except AttributeError:
                self.on_display_message(message="project not found", duration=10)
                return

        self.save_project_data(filepath=filepath, name=name)
        self.on_display_message.send(message="saved project")

        self.database_controller.set_project(filepath=filepath)

    def save_project_data(self, filepath: pathlib.Path, name: str):

        # project folder
        temp_path = temp_folder / name
        temp_datapath = temp_path / "data"
        if not temp_datapath.is_dir():
            temp_datapath.mkdir(parents=True, exist_ok=True)
        # data folder

        for sample in self.database_controller.spectra:
            # data = np.column_stack([sample.data.signal.x, sample.data.signal.raw])
            file = temp_datapath / f"{sample.name}"
            if not file.is_file():
                np.savez(file, x=sample.data.signal.x, y=sample.data.signal.raw)

        fnames = ["settings", "baseline_regions", "interpolation_regions"]
        data = self.database_controller.get_all_settings()

        for f, name in zip(data, fnames):
            f.to_parquet(temp_path / f"{name}.parquet")

        with tarfile.open(filepath, mode="w") as tar:
            tar.add(temp_path, arcname="")

    def export_results(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem
        folder = filepath.parents[0]

        self.database_controller.export_results(folder=folder, name=name)

    def move_project_files(self, filepath, name):

        temp_path = temp_folder / name
        temp_datapath = temp_path / "data"

        if not temp_datapath.is_dir():
            temp_datapath.mkdir(parents=True, exist_ok=True)

        with tarfile.open(str(filepath), "r") as tar:

            for info in tar:
                path = pathlib.Path(info.name)

                suffix = path.suffix

                if len(suffix) == 0:
                    continue

                name = path.stem

                to_path = {
                    ".parquet": str(temp_path / path.name),
                    ".csv": str(temp_path / path.name),
                    ".sp": str(temp_datapath / path.name),
                    ".npz": str(temp_datapath / path.name),
                }[suffix]

                tar.extract(info)
                shutil.move(str(path), to_path)

    def load_project(self, *args, filepath: str):

        self.on_clear_plot.send("new project")

        filepath = pathlib.Path(filepath)
        name = filepath.stem

        temp_path = temp_folder / name
        temp_datapath = temp_path / "data"

        self.move_project_files(filepath=filepath, name=name)

        setting_files = glob.glob(f"{temp_path}\\*.parquet")
        setting_files.extend(glob.glob(f"{temp_path}\\*.csv"))
        spectrum_files = glob.glob(f"{temp_datapath}\\*.sp")
        spectrum_files.extend(glob.glob(f"{temp_datapath}\\*.npz"))
        names = [pathlib.Path(spectrum).stem for spectrum in spectrum_files]

        settings_dict = {}
        for setting in setting_files:
            name = pathlib.Path(setting).stem
            try:
                settings_dict[name] = pd.read_parquet(str(setting))
            except pa.ArrowInvalid:
                header = [[0, 1], "infer"][name == "settings"]
                settings_dict[name] = pd.read_csv(
                    str(setting), index_col=[0], header=header
                )

        self.database_controller.__init__()
        self.database_controller.read_files(
            spectrum_files, names=names, settings=settings_dict
        )

        self.database_controller.set_project(filepath=filepath)
        self.gui.update_variables(sample_navigation={"samplelist": names})

        if self.gui.state == GUI_state.DISABLED:
            self.gui.activate_widgets()
            self.gui.set_state(GUI_state.ACTIVE)

    def save_sample(self, *args):

        self.database_controller.save_sample()
        self.on_display_message.send(message="sample saved")

    def save_all_samples(self, *args):

        self.database_controller.save_all_samples()
        self.on_display_message.send(message="saved all")

    def save_samples_to_project(self, *args):
        self.save_all_samples()
        if self.database_controller.has_project:
            self.save_project()

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)

        self.on_new_project.connect(self.new_project)
        self.on_save_project.connect(self.save_project)
        self.on_load_project.connect(self.load_project)
        self.on_export_results.connect(self.export_results)

        self.on_save_sample.connect(self.save_sample)
        self.on_save_all.connect(self.save_all_samples)
        self.on_Ctrl_s.connect(self.save_samples_to_project)


def get_names_from_files(files: List, previous_names: List[str] = []) -> List:
    separator = app_configuration.data_processing["name_separator"]
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
