import glob
import os
import pathlib
import shutil
import tarfile
import time
from tkinter import filedialog
from typing import Dict, List, Optional

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
    on_load_interference = bl.signal("load interference")
    on_interference_added = bl.signal("show interference")

    on_samples_removed = bl.signal("samples removed")

    on_save_all = bl.signal("save all")
    on_save_sample = bl.signal("save sample")

    on_save_project = bl.signal("save project")
    on_export_results = bl.signal("export results")

    on_clean_temp_files = bl.signal("clean temp files")

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

    def load_interference(self, *args):
        try:
            file = filedialog.askopenfilename(
                initialdir=os.getcwd(), filetypes=[("txt files", "*.txt")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        self.database_controller.add_interference(file)
        self.on_interference_added.send()

    def new_project(self, *args):

        self.clean_temp_files()
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

    def _make_project_folders(self, name: str) -> Dict:

        paths = {"project": temp_folder / name}
        paths["data"] = paths["project"] / "data"
        paths["processed"] = paths["data"] / "processed"
        paths["interference"] = paths["data"] / "interference"

        for dir in paths.values():
            if dir.is_dir():
                continue
            dir.mkdir(parents=True, exist_ok=True)

        return paths

    def save_project_data(self, filepath: pathlib.Path, name: str):

        paths = self._make_project_folders(name)

        has_interference = False

        for sample in self.database_controller.spectra:
            # data = np.column_stack([sample.data.signal.x, sample.data.signal.raw])
            file = paths["data"] / f"{sample.name}"
            if not file.is_file():
                np.savez(
                    file, x=sample.data.signal.get("x"), y=sample.data.signal.get("raw")
                )

            file_processed = paths["processed"] / f"{sample.name}"
            names = ("interference_corrected", "interpolated")
            data = [sample.data.signal.get(name) for name in names]
            processed = {
                name: vals for name, vals in zip(names, data) if vals is not None
            }

            if len(processed) > 0:
                np.savez(file_processed, **processed)

            if not sample.interference:
                continue

            has_interference = True
            file_interference = paths["interference"] / f"{sample.name}"
            np.savez(
                file_interference,
                x=sample.interference.data.signal.get("x"),
                y=sample.interference.data.signal.get("raw"),
            )

        if has_interference:
            interference_settings = (
                self.database_controller.get_all_interference_settings()
            )
            for name, f in interference_settings.items():
                f.to_parquet(paths["interference"] / f"{name}.parquet")

        settings = self.database_controller.get_all_settings()

        for name, f in settings.items():
            f.to_parquet(paths["project"] / f"{name}.parquet")

        with tarfile.open(filepath, mode="w") as tar:
            tar.add(paths["project"], arcname="")

    def export_results(self, *args, filepath: str):

        filepath = pathlib.Path(filepath)
        name = filepath.stem
        folder = filepath.parents[0]

        self.database_controller.export_results(folder=folder, name=name)

    def move_project_files(self, filepath, name):

        # temp_path = temp_folder / name
        # temp_datapath = temp_path / "data"
        # temp_interferencepath = temp_datapath / "interference"

        # if not temp_interferencepath.is_dir():
        #     temp_interferencepath.mkdir(parents=True, exist_ok=True)

        paths = self._make_project_folders(name)

        with tarfile.open(str(filepath), "r") as tar:

            for info in tar:
                path = pathlib.Path(info.name)

                suffix = path.suffix

                if len(suffix) == 0:
                    continue

                name = path.stem

                to_path = paths["project"] / path

                tar.extract(info)
                shutil.move(str(path), to_path)

    def load_project(self, *args, filepath: str):

        self.on_clear_plot.send("new project")

        filepath = pathlib.Path(filepath)
        name = filepath.stem

        # temp_path = temp_folder / name
        # temp_datapath = temp_path / "data"
        # temp_interferencepath = temp_datapath / "interference"

        paths = self._make_project_folders(name)

        self.move_project_files(filepath=filepath, name=name)

        setting_files = glob.glob(f"{paths['project']}\\*.parquet")
        setting_files.extend(glob.glob(f"{paths['project']}\\*.csv"))  # DELETE

        spectrum_files = glob.glob(f"{paths['data']}\\*.sp")  # DELETE
        spectrum_files.extend(glob.glob(f"{paths['data']}\\*.npz"))

        interference_files = glob.glob(f"{paths['interference']}\\*.npz")
        interference_setting_files = glob.glob(f"{paths['interference']}\\*.parquet")

        processed_files = glob.glob(f"{paths['processed']}\\*.npz")

        names = [pathlib.Path(s).stem for s in spectrum_files]
        interference_names = [pathlib.Path(s).stem for s in interference_files]
        processed_names = [pathlib.Path(s).stem for s in processed_files]

        settings_dict = {}
        for setting in setting_files:
            name = pathlib.Path(setting).stem
            try:
                settings_dict[name] = pd.read_parquet(str(setting))
            except pa.ArrowInvalid:
                header = [[0, 1], "infer"][name == "settings"]  # DELETE
                settings_dict[name] = pd.read_csv(
                    str(setting), index_col=[0], header=header
                )

        interference_settings_dict = {}
        for setting in interference_setting_files:
            name = pathlib.Path(setting).stem
            interference_settings_dict[name] = pd.read_parquet(str(setting))

        self.database_controller.__init__()
        self.database_controller.read_files(
            spectrum_files, names=names, settings=settings_dict
        )

        self.database_controller.add_processed_spectra(
            files=processed_files, names=processed_names
        )

        for file, name in zip(interference_files, interference_names):
            self.database_controller.add_interference(
                file=file,
                name=name,
                settings=interference_settings_dict,
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

    def clean_temp_files(self, *args):

        # delete temporary files
        for root, dirs, files in os.walk(temp_folder):

            for f in files:
                os.unlink(os.path.join(root, f))

            for d in dirs:
                try:
                    shutil.rmtree(os.path.join(root, d))
                except PermissionError:
                    time.sleep(0.5)
                    shutil.rmtree(os.path.join(root, d))

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)
        self.on_load_interference.connect(self.load_interference)

        self.on_new_project.connect(self.new_project)
        self.on_save_project.connect(self.save_project)
        self.on_load_project.connect(self.load_project)
        self.on_export_results.connect(self.export_results)

        self.on_save_sample.connect(self.save_sample)
        self.on_save_all.connect(self.save_all_samples)
        self.on_Ctrl_s.connect(self.save_samples_to_project)

        self.on_clean_temp_files.connect(self.clean_temp_files)


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
