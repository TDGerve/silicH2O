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
            "settings": Settings_DF(),
            "baseline_interpolation_regions": Baseline_DF(bir_amount=3),
            # "deconvolution": None,
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

    def get_sample(self, index: int) -> h2o_processor:

        return self.spectra[index]

    def calculate_sample(self, tab: str, idx=None):  # move #CH
        if idx is None:
            sample = self.current_sample
        else:
            sample = self.get_sample(idx)

        if tab == "interference":
            sample.calculate_interpolation(tab=tab)
            interference = sample.interference
            if interference is not None:
                sample.interference.calculate_baseline()
            return
        elif tab == "interpolation":
            sample.calculate_interpolation(tab=tab)

        # if sample.settings[("interference", "use")]:
        #     sample.subtract_interference()

        sample.calculate_baseline()
        sample.calculate_noise()
        sample.calculate_areas()

    def deconvolve_interference(self):  # move #CH
        sample = self.current_sample
        interference = sample.interference
        if interference is None:
            return

        interference.deconvolve()
        # sample.data.signal.set_with_interpolation(
        #     name="interference_deconvoluted",
        #     x=interference.data.signal.x,
        #     y=interference.data.signal.get("deconvoluted"),
        # )

    def subtract_interference(self) -> bool:  # move #CH
        sample = self.current_sample
        return sample.subtract_interference()

    def change_birs(self, action: str, index: int, tab: str):

        sample = {
            "baseline": self.current_sample,
            "interference": self.current_sample.interference,
        }[tab]
        func = {"remove": sample.remove_bir, "add": sample.add_bir}[action]

        func(index=index)

    def calculate_interpolation(self):  # move #CH
        sample = self.current_sample

        sample.calculate_interpolation()

    def change_sample_settings(self, **kwargs) -> None:  # move #CH
        sample = self.current_sample

        func_dict = {
            "baseline": sample.set_baseline,
            "interpolation": sample.set_interpolation,
            "subtraction": sample.set_subtraction_parameters,
        }
        if sample.interference is not None:
            func_dict["interference"] = sample.interference.set_baseline
            func_dict["deconvolution"] = sample.interference.set_deconvolution_settings

        for key, value in kwargs.items():
            func_dict[key](value)

    def get_sample_birs(self, type: str):  # move #CH
        sample = self.current_sample
        get_birs = {
            "baseline": sample.get_baseline_settings,
            "interpolation": sample.get_interpolation_settings(),
            "interference": dict,
        }
        if sample.interference is not None:
            get_birs["interference"] = sample.interference.get_baseline_settings

        get_birs = get_birs[type]

        return get_birs()

    def get_sample_settings(self):  # move #CH

        sample = self.current_sample

        baseline_settings = sample.get_baseline_settings()
        interpolation_settings = sample.get_interpolation_settings()
        interference_settings = sample.get_interference_settings()

        return {
            "baseline": {"baseline": baseline_settings},
            "interpolation": {"interpolation": interpolation_settings},
            "interference": interference_settings,
        }

    def get_all_settings(self):  # move #CH
        settings = {
            "settings": self.settings,
            "baseline_interpolation_regions": self.baseline_regions.dropna(
                axis="columns", how="all"
            ),
            "interpolation_regions": self.interpolation_regions.dropna(
                axis="columns", how="all"
            ),
        }

        return settings

    def get_all_interference_settings(self):  # move #CH
        return {
            name: df.dropna(axis="columns", how="all")
            for name, df in self.interference_settings.items()
        }

    def get_sample_results(self):  # move #CH

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

    def get_sample_plotdata(self):  # move #CH

        sample = self.current_sample

        return sample.get_plotdata()

    def read_files(
        self, files: List, names: List[str], settings: Optional[Dict] = None
    ) -> None:

        old_files = len(self.files)

        self.files = np.append(self.files, files)
        self.names = np.append(self.names, names)

        self.add_settings_results(names=names, settings=settings)

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
                    self.settings.loc[name].copy(),
                    self.baseline_regions.loc[name].copy(),
                    self.interpolation_regions.loc[name].copy(),
                ),
            )
            # self.calculate_sample(idx)
            # self.save_sample(idx=idx)

    def add_interference(
        self, file: str, name: Optional[str] = None, settings: Optional[Dict] = None
    ):
        if name is None:
            current_sample = self.current_sample
            name = current_sample.name
        else:
            idx = np.where(self.names == name)[0][0]
            current_sample = self.get_sample(idx)

        if self.interference_settings["settings"].shape[0] < 1:
            self.add_interference_settings(names=self.names, settings=settings)
        elif name not in self.interference_settings["settings"].index:
            self.add_interference_settings(names=[name], settings=settings)

        settings, birs = (
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

    def add_processed_spectra(self, files: List[str], names: List[str]):
        for file, name in zip(files, names):

            idx = np.where(self.names == name)[0][0]
            sample = self.get_sample(idx)

            with np.load(file, allow_pickle=True) as f:
                keys = f.keys()
                for key in keys:
                    sample.data.signal.add(name=key, values=f[key])

    def add_settings_results(self, names: List[str], settings: Optional[Dict] = None):

        if settings is None:
            new_settings, (
                new_birs,
                new_interpolation_regions,
            ) = app_configuration.get_default_settings(names, type="glass")

        else:
            new_settings = settings["settings"]
            new_birs = settings["baseline_interpolation_regions"]
            new_interpolation_regions = settings["interpolation_regions"]

        self.settings = pd.concat(_match_columns(self.settings, new_settings), axis=0)
        self.baseline_regions = pd.concat(
            _match_columns(self.baseline_regions, new_birs), axis=0
        )
        self.interpolation_regions = pd.concat(
            _match_columns(self.interpolation_regions, new_interpolation_regions),
            axis=0,
        )

        new_results = Results_DF(index=names)
        self.results = pd.concat([self.results, new_results], axis=0)

    def add_interference_settings(
        self, names: Optional[List[str]], settings: Optional[Dict] = None
    ):

        if not settings:
            (
                new_settings,
                (new_birs, *_),
            ) = app_configuration.get_default_settings(names, type="interference")
        else:
            new_settings = settings["settings"].copy()
            new_birs = settings["baseline_interpolation_regions"].copy()

        self.interference_settings["settings"] = pd.concat(
            _match_columns(self.interference_settings["settings"], new_settings),
            axis=0,
        )
        self.interference_settings["baseline_interpolation_regions"] = pd.concat(
            _match_columns(
                self.interference_settings["baseline_interpolation_regions"],
                new_birs,
            ),
            axis=0,
        )

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
        """ """

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

        if sample.interference:
            self.save_interference()

        self.results.loc[name] = sample.results.copy()

    def save_all_samples(self) -> None:

        for sample_idx in range(self.results.shape[0]):
            self.save_sample(sample_idx)

    def reset_sample(self, tab: str) -> None:  # CHANGE SETTINGS PER TAB

        sample = self.current_sample
        name = sample.name

        if tab == "baseline":
            # restore previous settings
            sample.settings = self.settings.loc[name].copy()
            # ONLY RESTORE BASELINE SETTINGS ETC #CH
            sample.baseline_regions = self.baseline_regions.loc[name].copy()
        elif tab == "interpolation":
            sample.interpolation_regions = self.interpolation_regions.loc[name].copy()
        elif tab == "interference":
            sample.interference.settings = (
                self.interference_settings["settings"].loc[name].copy()
            )
            sample.interference.baseline_regions = (
                self.interference_settings["baseline_interpolation_regions"]
                .loc[name]
                .copy()
            )

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
