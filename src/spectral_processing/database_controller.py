import pathlib
import warnings as w
from typing import Dict, List, Optional

import blinker as bl
import numpy as np
import pandas as pd

from .. import app_configuration
from ..Dataframes import (
    Baseline_DF,
    Results_DF,
    Settings_DF,
    _insert_row,
    _match_columns,
)
from .sample_processing import h2o_processor

on_display_message = bl.signal("display message")


class Database_controller:
    def __init__(self):
        self.files: np.ndarray = np.array([], dtype=str)
        self.names: np.ndarray = np.array([], dtype=str)
        self.spectra: np.ndarray = np.array([], dtype=h2o_processor)

        self.settings: pd.DataFrame = Settings_DF()

        self.baseline_regions: pd.DataFrame = Baseline_DF(bir_amount=5)
        self.interpolation_regions: pd.DataFrame = Baseline_DF(bir_amount=1)

        self.interference_settings = {
            "settings": None,
            "baseline_interpolation_regions": None,
        }

        self.results: pd.DataFrame = Results_DF()

        self.current_sample_index: Optional[int] = None

        self.project = None

    @property
    def current_sample(self) -> h2o_processor:
        return self.get_sample(self.current_sample_index)

    @current_sample.setter
    def current_sample(self) -> None:
        w.warn("attribute is read only")

    @property
    def sample_saved(self):
        sample = self.current_sample
        name = sample.name
        return np.array_equal(self.results.loc[name], sample.results)

    @sample_saved.setter
    def sample_saved(self):
        print("attribute is read only")

    def read_files(
        self, files: List, names: List[str], settings: Optional[Dict] = None
    ) -> None:

        if settings is None:
            new_settings, (
                new_birs,
                new_interpolation_regions,
            ) = app_configuration.get_default_settings(names, type="glass")

        else:
            new_settings = settings["settings"]
            new_birs = settings["baseline_interpolation_regions"]
            new_interpolation_regions = settings["interpolation_regions"]

        new_results = Results_DF(index=names)

        old_files = len(self.files)

        self.files = np.append(self.files, files)
        self.names = np.append(self.names, names)

        self.settings = pd.concat(_match_columns(self.settings, new_settings), axis=0)

        self.baseline_regions = pd.concat(
            _match_columns(self.baseline_regions, new_birs), axis=0
        )
        self.interpolation_regions = pd.concat(
            _match_columns(self.interpolation_regions, new_interpolation_regions),
            axis=0,
        )

        self.results = pd.concat([self.results, new_results], axis=0)

        for idx, (file, name) in enumerate(
            zip(self.files[old_files:], self.names[old_files:])
        ):
            try:
                with np.load(file) as f:
                    x = f["x"]
                    y = f["y"]
            except ValueError:
                x, y = np.genfromtxt(file, unpack=True)
            self.spectra = np.append(
                self.spectra,
                h2o_processor(
                    name,
                    x,
                    y,
                    new_settings.loc[name].copy(),
                    new_birs.loc[name].copy(),
                    new_interpolation_regions.loc[name].copy(),
                ),
            )
            self.calculate_sample(idx)
            self.save_sample(idx=idx)

    def add_interference(
        self, file: str, name: Optional[str] = None, settings: Optional[Dict] = None
    ):
        if name is None:
            current_sample = self.current_sample
            name = current_sample.name
        else:
            idx = np.where(self.names == name)[0][0]
            current_sample = self.get_sample(idx)

        if settings is not None:
            for key in settings.keys():
                self.interference_settings[key] = settings[key]

        else:
            if self.interference_settings["settings"] is None:
                (
                    self.interference_settings["settings"],
                    (self.interference_settings["baseline_interpolation_regions"], *_),
                ) = app_configuration.get_default_settings(
                    self.names, type="interference"
                )
            elif name not in self.interference_settings.index:
                new_settings, new_birs = app_configuration.get_default_settings(
                    [name], type="interference"
                )
                self.interference_settings[name] = new_settings
                self.interference_settings[
                    "baseline_interpolation_regions"
                ] = _insert_row(
                    self.interference_settings["baseline_interpolation_regions"],
                    new_birs,
                )

        settings, birs, = (
            self.interference_settings["settings"].loc[name],
            self.interference_settings["baseline_interpolation_regions"].loc[name],
        )

        try:
            with np.load(file) as f:
                x = f["x"]
                y = f["y"]
        except ValueError:
            x, y = np.genfromtxt(file, unpack=True)

        current_sample.set_interference(x, y, settings, birs)

    def get_sample(self, index: int) -> h2o_processor:

        return self.spectra[index]

    def calculate_sample(self, idx=None):
        if idx is None:
            sample = self.current_sample
        else:
            sample = self.get_sample(idx)

        current_tab = app_configuration.gui["current_tab"]

        if (current_tab == "interference") & (sample.interference is not None):
            sample.interference.calculate_baseline()
            return
        elif current_tab == "interpolation":
            return

        sample.calculate_baseline()
        sample.calculate_noise()
        sample.calculate_areas()

    def change_birs(self, action: str, index: int):

        current_tab = app_configuration.gui["current_tab"]

        sample = {
            "baseline": self.current_sample,
            "interference": self.current_sample.interference,
        }[current_tab]
        func = {"remove": sample.remove_bir, "add": sample.add_bir}[action]

        func(index=index)

    def calculate_interpolation(self):
        sample = self.current_sample

        sample.calculate_interpolation()

    def change_sample_settings(self, **kwargs) -> None:
        sample = self.current_sample

        func_dict = {
            "baseline": sample.set_baseline,
            "interpolate": sample.set_interpolation,
        }
        if sample.interference:
            func_dict["interference"] = sample.interference.set_baseline

        for key, value in kwargs.items():
            func_dict[key](value)

    def get_sample_settings(self):

        sample = self.current_sample

        baseline = sample.get_birs()
        baseline["smoothing"] = sample.settings[("baseline", "smoothing")]

        interpolation = {}

        if sample.interference:
            interference = sample.interference.get_birs()
            interference["smoothing"] = sample.interference.settings[
                ("baseline", "smoothing")
            ]
        else:
            interference = {}

        # interference_deconvolution = {}
        # baseline_smoothing = [self.current_sample.settings["baseline_smoothing"]]

        return {
            "baseline": baseline,
            "interpolation": interpolation,
            "interference": interference,
            # "interference_deconvolution": interference_deconvolution
            # "baseline_smoothing": baseline_smoothing,
        }

    def get_all_settings(self):
        settings = [
            self.settings,
            self.baseline_regions.dropna(axis="columns", how="all"),
            self.interpolation_regions.dropna(axis="columns", how="all"),
        ]
        if self.interference_settings:
            settings.extend(self.interference_settings.values())
        return settings

    # def get_all_interference_settings(self):

    def get_sample_results(self):

        all_results = list(self.current_sample.results.values)
        names = ["silicate", "H2O", "H2OSi"]
        areas = {}
        for name, value in zip(names, all_results[:3]):
            if abs(value) < 20:
                value = round(value, 2)
            else:
                value = int(value)
            areas[name] = value

        names = ["noise", "Si_SNR", "H2O_SNR"]
        signal = {name: round(value, 2) for name, value in zip(names, all_results[3:])}

        return {"areas": areas, "signal": signal}

    def get_sample_plotdata(self):

        sample = self.current_sample

        return sample.get_plotdata()

    def save_interference(self, idx: Optional[int] = None):
        if idx is None:
            sample = self.current_sample.interference
        else:
            sample = self.get_sample(idx).interference
        name = sample.name

        # save current settings
        self.interference_settings["settings"].loc[name] = sample.settings.copy()

        self.interference_settings["baseline_interpolation_regions"] = _insert_row(
            self.interference_settings["baseline_interpolation_regions"],
            sample.baseline_regions,
        )

    def save_sample(self, idx=None) -> None:
        """
        ADD INTERFERENCE
        """

        if idx is None:
            sample = self.current_sample
        else:
            sample = self.get_sample(idx)
        name = sample.name

        # save current settings
        self.settings.loc[name] = sample.settings.copy()

        self.baseline_regions = _insert_row(
            self.baseline_regions, sample.baseline_regions
        )
        self.interpolation_regions = _insert_row(
            self.interpolation_regions, sample.interpolation_regions
        )

        self.results.loc[name] = sample.results.copy()

        # missing_baseline_cols = sample.baseline_regions.index.difference(
        #     self.baseline_regions.columns
        # )
        # if len(missing_baseline_cols) > 0:
        #     self.baseline_regions[missing_baseline_cols] = np.nan
        # self.baseline_regions.loc[name] = sample.baseline_regions.copy()
        # missing_interpolation_cols = sample.interpolation_regions.index.difference(
        #     self.interpolation_regions.columns
        # )
        # if len(missing_interpolation_cols) > 0:
        #     self.interpolation_regions[missing_interpolation_cols] = np.nan
        # self.interpolation_regions.loc[name] = sample.interpolation_regions.copy()

        # self.results.loc[name] = sample.results.copy()

        if sample.interference:
            self.save_interference()

    def save_all_samples(self) -> None:

        for sample_idx in range(self.results.shape[0]):
            self.save_sample(sample_idx)

    def reset_sample(self) -> None:

        sample = self.current_sample
        name = sample.name

        current_tab = app_configuration.gui["current_tab"]

        if current_tab == "baseline":
            # restore previous settings
            sample.settings = self.settings.loc[name].copy()
            sample.baseline_regions = self.baseline_regions.loc[name].copy()
        elif current_tab == "interpolation":
            sample.interpolation_regions = self.interpolation_regions.loc[name].copy()
        elif current_tab == "interference":
            sample.interference.settings = self.interference_settings["settings"]
            sample.interference.baseline_regions = self.interference_settings[
                "baseline_interpolation_regions"
            ]

        on_display_message.send(message="sample reset")

    def remove_samples(self, index: List[int]) -> None:

        current_sample = self.files[self.current_sample_index]
        remove_samples = self.names[index]

        data = [self.spectra, self.files, self.names]
        for idx in range(len(data)):
            data[idx] = np.delete(data[idx], index)
        self.spectra, self.files, self.names = data

        dataframes = [
            self.results,
            self.settings,
            self.baseline_regions,
            self.interpolation_regions,
        ]
        for idx in range(len(dataframes)):
            dataframes[idx].drop(labels=remove_samples, axis=0, inplace=True)

    def set_project(self, filepath: str):
        self.project = filepath

    @property
    def has_project(self):
        return self.project is not None

    def export_results(
        self, folder: pathlib.Path, name: str, incl_settings: bool = True
    ):
        try:
            pd.concat([self.settings, self.results], axis=1).to_csv(
                folder / f"{name}.csv"
            )
        except PermissionError:
            on_display_message.send(message=f"{name}.csv is open!", duration=10)
            return

        if not incl_settings:
            return

        baseline_settings = []

        for setting, data in zip(
            ("baseline_regions", "interpolation_regions"),
            (self.baseline_regions, self.interpolation_regions),
        ):
            baseline_settings.append(
                pd.concat({setting: data}, names=["setting"], axis=1)
            )

        baseline_settings = pd.concat(baseline_settings, axis=1)

        try:
            baseline_settings.to_csv(folder / f"{name}_baselines.csv")
        except PermissionError:
            on_display_message.send(
                message=f"{name}_baselines.csv is open!", duration=10
            )
            return


# def get_default_settings(names: List, type: str) -> pd.DataFrame:

#     baseline_correction, interpolation, interference = app_configuration.data_processing[type]
#     bir_amount = len(baseline_correction["baseline_interpolation_regions"].index) // 2

#     baseline_regions = Baseline_DF(
#         bir_amount, [baseline_correction["baseline_interpolation_regions"].values] * len(names), index=names
#     ).squeeze()

#     itp_amount = len(interpolation["baseline_interpolation_regions"].index) // 2
#     interpolation_regions = Baseline_DF(
#         itp_amount, [interpolation["baseline_interpolation_regions"].values] * len(names), index=names
#     ).squeeze()

#     itf_bir_amount = len(interference["baseline_interpolation_regions"].index) // 2
#     interference_baseline_regions =

#     data = [
#         [
#             baseline_correction["smoothing"],
#             interpolation["use"],
#             interpolation["smoothing"],
#         ]
#     ] * len(names)

#     settings = Settings_DF(data, index=names).squeeze()

#     return settings, birs, interpolation_regions
