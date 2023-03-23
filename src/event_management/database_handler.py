import glob
import json
import os
import pathlib
import shutil
import sys
import tarfile
import time
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional

import blinker as bl
import numpy as np
import pandas as pd
import pyarrow as pa

from .. import app_configuration
from ..app_configuration import (
    reset_default_settings,
    set_glass_settings,
    set_interference_settings,
)

# from ..interface import Gui
from ..spectral_processing import Calibration_processor, Database_controller

on_display_message = bl.signal("display message")


if getattr(sys, "frozen", False):
    EXE_LOCATION = pathlib.Path(os.path.dirname(sys.executable))  # cx_Freeze frozen
    temp_folder = EXE_LOCATION.parents[0] / "temp"
    calibration_folder = EXE_LOCATION.parents[0] / "calibration"

else:
    temp_folder = pathlib.Path(__file__).parents[1] / "temp"
    calibration_folder = pathlib.Path(__file__).parents[1] / "calibration"


class Database_listener:

    on_samples_added = bl.signal("samples added")
    on_load_project = bl.signal("load project")
    on_new_project = bl.signal("new project")
    on_load_interference = bl.signal("load interference")
    on_interference_added = bl.signal("show interference")

    on_activate_widgets = bl.signal("activate_widgets")
    on_clear_gui_variables = bl.signal("clear variables")

    on_samples_removed = bl.signal("samples removed")

    on_save_all = bl.signal("save all")
    on_save_sample = bl.signal("save sample")

    on_set_default_glass_settings = bl.signal("set default glass")
    on_set_default_interference_settings = bl.signal("set default interference")
    on_restore_default_settings = bl.signal("restore default settings")

    on_save_project = bl.signal("save project")
    on_export_results = bl.signal("export results")
    on_export_sample = bl.signal("export sample")
    on_export_all = bl.signal("export all")

    on_save_calibration_as = bl.signal("save calibration as")
    on_read_calibration_file = bl.signal("read calibration file")
    on_import_calibration_file = bl.signal("import calibration file")

    on_clean_temp_files = bl.signal("clean temp files")
    on_clear_plot = bl.signal("clear plot")

    on_plot_change = bl.signal("refresh plot")
    on_display_message = bl.signal("display message")
    on_update_gui_variables = bl.signal("update gui variables")
    on_change_title = bl.signal("change_title")

    on_Ctrl_s = bl.signal("ctrl+s")

    def __init__(
        self,
        database_controller: Database_controller,
        calibration: Calibration_processor,
    ):
        self.database_controller = database_controller
        self.calibration = calibration
        # self.gui = gui

        self.subscribe_to_signals()

    def set_dafault_glass_settings(self, *args):
        sample = self.database_controller.current_sample

        settings = sample.settings
        baseline_interpolation_regions = (
            sample.baseline.interpolation_regions.nested_array
        )
        interpolation_regions = sample.interpolation.regions.nested_array
        set_glass_settings(
            baseline_interpolation_regions=baseline_interpolation_regions,
            interpolation_regions=interpolation_regions,
            settings=settings,
        )

    def set_default_interference_settings(self, *args):
        sample = self.database_controller.current_sample.interference_sample
        if sample is None:
            self.on_display_message.send(
                message="Sample has no interference!", duration=5
            )
            return

        settings = sample.settings
        baseline_interpolation_regions = (
            sample.baseline.interpolation_regions.nested_array
        )

        set_interference_settings(
            baseline_interpolation_regions=baseline_interpolation_regions,
            settings=settings,
        )

    def reset_default_settings(self, *args, type: str):
        reset_default_settings(type=type)

    def remove_samples(self, *args, index: List[int]) -> None:

        if self.database_controller.has_project:
            names = self.database_controller.names[index]
            if isinstance(names, str):
                names = [names]
            self.remove_data(names=names)

        self.database_controller.remove_samples(index)

        names = list(self.database_controller.names)
        # self.gui.update_variables(sample_navigation={"samplelist": names})
        self.on_update_gui_variables.send(sample_navigation={"samplelist": names})

    def remove_data(self, names: List[str]):

        temp_path = temp_folder / self.database_controller.project.stem
        temp_datapath = temp_path / "data"

        for name in names:
            for file in temp_datapath.rglob(f"{name}.npz"):
                file.unlink()

    def add_samples(self, *args, files: List[str], name_delimiter: str) -> None:

        previous_names = list(self.database_controller.names)
        names = get_names_from_files(
            files, previous_names=previous_names, delimiter=name_delimiter
        )
        total_names = previous_names + names

        self.database_controller.read_files(files, names=names)

        # self.gui.update_variables(sample_navigation={"samplelist": total_names})
        self.on_update_gui_variables.send(sample_navigation={"samplelist": total_names})
        self.on_activate_widgets.send()

        # if self.gui.state == GUI_state.DISABLED:
        #     self.gui.activate_widgets()
        #     self.gui.set_state(GUI_state.ACTIVE)

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
        self.calibration.__init__()
        self.on_change_title.send()
        # self.gui.clear_variables()
        self.on_clear_gui_variables.send()
        self.on_clear_plot.send("new project")

    def save_project(self, *args, filepath: Optional[str] = None):

        self.on_display_message.send(message="saving project...", duration=5)

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
        self.on_change_title.send(title=name)
        self.on_display_message.send(message="saved project")

        self.database_controller.set_project(filepath=filepath)

    def save_calibration_as(
        self, *args, name: Optional[str] = None, import_as_project=False
    ):

        if name is None:
            name = self.calibration.name

        if name is None:
            on_display_message.send(message="Save calibration as ... first!")
            return

        self.on_display_message.send(message="saving calibration...", duration=5)

        self.save_calibration_data(name=name)

        if self.calibration._database_controller:

            filepath = calibration_folder / "projects" / f"{name}.h2o"
            self.save_project_data(filepath=filepath, name=name)

            if self.database_controller.project != filepath:
                import_as_project = messagebox.askquestion(
                    message="Open calibration as project?"
                )

        self.on_display_message.send(message="saved calibration")
        self.calibration.name = name

        if import_as_project:
            self.on_change_title.send(title=name)
            self.database_controller.set_project(filepath=filepath)

    def _make_project_folders(self, name: str, base_folder=temp_folder) -> Dict:

        paths = {"project": base_folder / name}
        paths["data"] = paths["project"] / "data"
        paths["processed"] = paths["data"] / "processed"
        paths["interference"] = paths["data"] / "interference"

        for dir in paths.values():
            if dir.is_dir():
                continue
            dir.mkdir(parents=True, exist_ok=True)

        return paths

    def save_calibration_data(self, *args, name: Optional[str] = None):

        if name is None:
            name = self.calibration.name

        data_file = calibration_folder / f"{name}.cH2O"
        # coefficients_file = calibration_folder / "coefficients.json"

        calibration_data = pd.concat(
            [
                self.calibration._H2OSi.rename("H2OSi"),
                self.calibration._H2Oreference.rename("H2Oreference"),
                self.calibration.use.rename("use"),
            ],
            axis=1,
        )
        calibration_data.to_parquet(data_file)

        # calibration_coefficients = {
        #     name: val
        #     for name, val in zip(("intercept", "slope"), self.calibration.coefficients)
        # }

        # with open(coefficients_file, "w", encoding="utf-8") as f:
        #     json.dump(calibration_coefficients, f, ensure_ascii=False, indent=4)

        # files = (data_file, coefficients_file)
        # with tarfile.open(calibration_folder / f"{name}.ch2o", mode="w") as tar:
        #     for file in files:
        #         # Add file to tar
        #         tar.add(file)

        # Delete file
        # for file in files:
        #     os.unlink(file)

    # def read_calibration_file(self, *args, filepath: str, **kwargs):

    #     file = pathlib.Path(filepath)
    #     if not file.is_file():
    #         messagebox.showwarning(
    #             title="Silic-H2O", message="Calibration file not found!"
    #         )
    #         return

    #     name = file.stem
    #     calibration = pd.read_parquet(filepath)

    #     self.on_import_calibration_file.send(
    #         name=name,
    #         H2OSi=calibration["H2OSi"].copy(),
    #         H2Oreference=calibration["H2Oreference"].copy(),
    #         use=calibration["use"].copy(),
    #         **kwargs,
    #     )

    def read_calibration_file(
        self, *args, filepath: str, which: Optional[List[str]] = None, update_gui=True
    ):

        filepath = pathlib.Path(filepath)
        calibration_data, name = self.open_calibration_file(filepath=filepath)
        data = calibration_data.to_dict(orient="series")
        data["name"] = name

        if which is not None:
            data = {name: vals for name, vals in data.items() if name in which}

        self.on_import_calibration_file.send(update_gui=update_gui, **data)

    def open_calibration_file(self, filepath: pathlib.Path):

        name = filepath.stem

        if not filepath.is_file():
            messagebox.showwarning(
                title="Silic-H2O", message="Calibration file not found!"
            )
            return
        calibration_data = pd.read_parquet(calibration_folder / f"{name}.cH2O")
        return calibration_data, name

    def read_calibration_settings(self, projectpath: pathlib.Path):

        with open(projectpath / "calibration.json", "r") as f:
            calibration = json.load(f)
            if name := calibration.get("name", None):
                calibration_filepath = calibration_folder / f"{name}.cH2O"
                return calibration_filepath

    def save_calibration_to_project(self, projectpath):

        with open(projectpath / "calibration.json", "w") as f:
            data = {"name": self.calibration.name}
            json.dump(data, f, ensure_ascii=False, indent=4, allow_nan=True)

    def save_project_data(self, filepath: pathlib.Path, name: str):

        paths = self._make_project_folders(name)

        self.save_calibration_to_project(paths["project"])

        has_interference = False

        for processor in self.database_controller.spectra:
            # data = np.column_stack([sample.sample.signal.x, sample.sample.signal.raw])
            file = paths["data"] / f"{processor.name}"
            if not file.is_file():
                np.savez(
                    file,
                    x=processor.sample.signal.get("x"),
                    y=processor.sample.signal.get("raw"),
                )

            file_processed = paths["processed"] / f"{processor.name}"
            names = ("interference_corrected", "interpolated")
            data = [processor.sample.signal.get(name) for name in names]
            processed = {
                name: vals for name, vals in zip(names, data) if vals is not None
            }

            if len(processed) > 0:
                np.savez(file_processed, **processed)

            if not processor.interference_sample:
                continue

            has_interference = True
            file_interference = paths["interference"] / f"{processor.name}"
            np.savez(
                file_interference,
                x=processor.interference_sample.sample.signal.get("x"),
                y=processor.interference_sample.sample.signal.get("raw"),
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

        on_display_message.send(message="exporting results...", duration=5)

        filepath = pathlib.Path(filepath)
        name = filepath.stem
        folder = filepath.parents[0]

        self.database_controller.export_results(folder=folder, name=name)

        on_display_message.send(message="results exported!")

    def move_project_files(self, filepath, name):

        # temp_path = temp_folder / name
        # temp_datapath = temp_path / "data"
        # temp_interferencepath = temp_datapath / "interference"

        # if not temp_interferencepath.is_dir():
        #     temp_interferencepath.mkdir(parents=True, exist_ok=True)

        paths = self._make_project_folders(name)
        to_path = paths["project"]

        with tarfile.open(str(filepath), "r") as tar:

            for info in tar:
                path = pathlib.Path(info.name)

                suffix = path.suffix

                if len(suffix) == 0:
                    continue

                # name = path.stem

                tar.extract(info, path=to_path)
                # shutil.move(str(path), to_path)

        return paths

    def load_project(self, *args, filepath: str):

        self.on_clear_plot.send("new project")

        self.clean_temp_files()
        filepath = pathlib.Path(filepath)
        projectname = filepath.stem

        # temp_path = temp_folder / name
        # temp_datapath = temp_path / "data"
        # temp_interferencepath = temp_datapath / "interference"

        # paths = self._make_project_folders(name)

        paths = self.move_project_files(filepath=filepath, name=projectname)

        setting_files = glob.glob(f"{paths['project']}\\*.parquet")
        # setting_files.extend(glob.glob(f"{paths['project']}\\*.csv"))  # DELETE

        # spectrum_files = glob.glob(f"{paths['data']}\\*.sp")  # DELETE
        spectrum_files = glob.glob(f"{paths['data']}\\*.npz")

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
                # header = [[0, 1], "infer"][name == "settings"]  # DELETE
                settings_dict[name] = pd.read_csv(
                    str(setting), index_col=[0], header=[0, 1]
                )

        interference_settings_dict = {}
        for setting in interference_setting_files:
            name = pathlib.Path(setting).stem
            interference_settings_dict[name] = pd.read_parquet(str(setting))

        self.database_controller.__init__()
        # Add calibration

        calibration_filepath = self.read_calibration_settings(
            projectpath=paths["project"]
        )
        if calibration_filepath is not None:
            self.read_calibration_file(filepath=calibration_filepath, update_gui=False)
        # with open(paths["project"] / "calibration.json", "r") as f:
        #     calibration = json.load(f)
        #     if name := calibration.get("name", None):
        #         self.read_calibration_file(
        #             filepath=calibration_folder / f"{name}.cH2O", update_gui=False
        # )
        # Read samples
        self.database_controller.read_files(
            spectrum_files, names=names, settings=settings_dict, calculate_results=False
        )
        # Read processed spectra
        self.database_controller.add_processed_spectra(
            files=processed_files, names=processed_names
        )
        # Initialise results
        self.database_controller.save_results()
        # Read interference
        for file, name in zip(interference_files, interference_names):
            self.database_controller.add_interference(
                file=file,
                name=name,
                settings=interference_settings_dict,
            )

        self.database_controller.set_project(filepath=filepath)
        self.on_change_title.send(title=projectname)
        # self.gui.update_variables(sample_navigation={"samplelist": names})
        self.on_update_gui_variables.send(sample_navigation={"samplelist": names})
        self.on_activate_widgets.send()

        # if self.gui.state == GUI_state.DISABLED:
        #     self.gui.activate_widgets()
        #     self.gui.set_state(GUI_state.ACTIVE)

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
        for folder in (temp_folder, calibration_folder / "temp"):
            for root, dirs, files in os.walk(folder):

                for f in files:
                    os.unlink(os.path.join(root, f))

                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except PermissionError:
                        time.sleep(0.5)
                        shutil.rmtree(os.path.join(root, d))

    def export_sample(self, *args, filepath: str):
        filepath = pathlib.Path(filepath)
        self.database_controller.export_sample(filepath=filepath)

    def export_all(self, *args, folderpath: str):
        folderpath = pathlib.Path(folderpath)
        self.database_controller.export_all(folderpath=folderpath)

    def subscribe_to_signals(self) -> None:
        self.on_samples_added.connect(self.add_samples)
        self.on_samples_removed.connect(self.remove_samples)
        self.on_load_interference.connect(self.load_interference)

        self.on_new_project.connect(self.new_project)
        self.on_load_project.connect(self.load_project)

        self.on_set_default_glass_settings.connect(self.set_dafault_glass_settings)
        self.on_set_default_interference_settings.connect(
            self.set_default_interference_settings
        )
        self.on_restore_default_settings.connect(self.reset_default_settings)

        self.on_export_results.connect(self.export_results)
        self.on_export_sample.connect(self.export_sample)
        self.on_export_all.connect(self.export_all)

        self.on_save_project.connect(self.save_project)
        self.on_save_sample.connect(self.save_sample)
        self.on_save_all.connect(self.save_all_samples)

        self.on_save_calibration_as.connect(self.save_calibration_as)
        self.on_read_calibration_file.connect(self.read_calibration_file)

        self.on_Ctrl_s.connect(self.save_samples_to_project)

        self.on_clean_temp_files.connect(self.clean_temp_files)


def get_names_from_files(
    files: List, previous_names: List[str] = [], delimiter: Optional[str] = None
) -> List:
    if delimiter is None:
        delimiter = app_configuration.data_processing["name_separator"]
    names = []

    for file in files:
        try:
            name = os.path.basename(file)
        except TypeError:
            name = file.name
        if delimiter not in name:
            names.append(name)
        else:
            names.append(name[: name.index(delimiter)])

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
