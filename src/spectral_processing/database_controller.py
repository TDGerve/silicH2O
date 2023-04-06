import pathlib
import warnings as w
from typing import Callable, Dict, List, Optional

import blinker as bl
import numpy as np
import pandas as pd

from .. import app_configuration
from .Dataframes import (
    Baseline_DF,
    Results_DF,
    Settings_DF,
    _insert_row,
    _match_columns,
)
from .sample_processing import Sample_proccessor, h2o_processor

on_display_message = bl.signal("display message")


class Database_controller:
    def __init__(self):
        self.files: np.ndarray = np.array([], dtype=str)
        self.names: np.ndarray = np.array([], dtype=str)
        self.spectra: np.ndarray = np.array([], dtype=h2o_processor)

        self.current_sample_index: Optional[int] = None

        self.settings: pd.DataFrame = Settings_DF()
        self.baseline_regions: pd.DataFrame = Baseline_DF(bir_amount=5)
        self.interpolation_regions: pd.DataFrame = Baseline_DF(bir_amount=1)

        self.interference_settings = {
            "settings": Settings_DF(),
            "baseline_interpolation_regions": Baseline_DF(bir_amount=3),
            # "deconvolution": None,
        }

        self.results: pd.DataFrame = Results_DF()

        self.calibration: Optional[str] = None
        self.calculate_H2O: Callable = lambda *args, **kwargs: None

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

    # @property
    # def H2Oreference(self):
    #     # pd.Series(
    #     #     {sample.name: sample.H2Oreference for sample in self.spectra}, name="H2Oref"
    #     # )
    #     return self.settings[("calibration", "H2Oreference")]

    def set_calibration(self, name: str, calibration: Callable):
        self.calibration = name
        self.calculate_H2O = calibration

    def reset_calibration(self):
        self.calibration = None
        self.calculate_H2O = lambda *args, **kwargs: None

    def get_sample(self, index: int) -> h2o_processor:

        return self.spectra[index]

    def change_birs(self, action: str, index: int, tab: str):

        if tab in ("baseline", "interpolation"):
            sample = self.current_sample
        elif tab == "interference":
            sample = self.current_sample.interference_sample

        if tab in ("baseline", "interference"):
            func = {"remove": sample.remove_bir, "add": sample.add_bir}[action]
        elif tab == "interpolation":
            func = {
                "remove": sample.remove_interpolation_region,
                "add": sample.add_interpolation_region,
            }[action]

        func(index=index)

    def get_all_settings(self):
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

    def get_all_interference_settings(self):
        return {
            name: df.dropna(axis="columns", how="all")
            for name, df in self.interference_settings.items()
        }

    def read_files(
        self,
        files: List,
        names: List[str],
        settings: Optional[Dict] = None,
        calculate_results=True,
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
                spectrum = pd.read_csv(
                    file, delimiter="\t|,", header=None, engine="python"
                )
                x, y = [spectrum.iloc[:, col].to_numpy() for col in spectrum]
                # x, y = np.genfromtxt(file, unpack=True)

            self.spectra = np.append(
                self.spectra,
                h2o_processor(
                    name=name,
                    x=x,
                    y=y,
                    settings=self.settings.loc[name].copy(),
                    baseline_regions=self.baseline_regions.loc[name].copy(),
                    interpolation_regions=self.interpolation_regions.loc[name].copy(),
                ),
            )
            if calculate_results:
                self.spectra[idx].calculate_results()

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
            self.interference_settings["settings"].loc[name].copy(),
            self.interference_settings["baseline_interpolation_regions"]
            .loc[name]
            .copy(),
        )

        try:
            with np.load(file) as f:
                x = f["x"]
                y = f["y"]
        except ValueError:
            # x, y = np.genfromtxt(file, unpack=True)
            spectrum = pd.read_csv(file, delimiter="\t|,", header=None, engine="python")
            x, y = [spectrum.iloc[:, col].to_numpy() for col in spectrum]

        current_sample.set_interference(
            x=x,
            y=y,
            settings=settings,
            baseline_regions=birs,
        )

    def add_processed_spectra(self, files: List[str], names: List[str]):
        for file, name in zip(files, names):

            idx = np.where(self.names == name)[0][0]
            sample = self.get_sample(idx)

            with np.load(file, allow_pickle=True) as f:
                keys = f.keys()
                for key in keys:
                    sample.sample.signal.add(name=key, values=f[key])

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
            sample = self.current_sample.interference_sample
        else:
            sample = self.get_sample(idx).interference_sample
        name = sample.name

        # save current settings
        self.interference_settings["settings"].loc[name] = sample.settings.copy()

        self.interference_settings["baseline_interpolation_regions"] = _insert_row(
            self.interference_settings["baseline_interpolation_regions"],
            sample.baseline.interpolation_regions.series,
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
            self.baseline_regions, sample.baseline.interpolation_regions.series
        )
        self.interpolation_regions = _insert_row(
            self.interpolation_regions, sample.interpolation.regions.series
        )

        if sample.interference_sample is not None:
            self.save_interference(idx=idx)

        self.results.loc[name] = sample.results.copy()
        self.results.loc[name, "H2O"] = self.calculate_H2O(sample.results["rWS"])

        # Not a great way to save H2O, would be better to do that inside the sample processor
        self.results.loc[name, "H2O"] = self.calculate_H2O(
            self.results.loc[name, "rWS"]
        )

    def save_all_samples(self) -> None:

        for sample_idx in range(self.results.shape[0]):
            self.save_sample(idx=sample_idx)

    def reset_sample(self, tab: str) -> None:

        sample = self.current_sample
        name = sample.name

        sample.apply_settings(settings=self.settings.loc[name], groups=[tab])

        if tab == "baseline":

            sample.baseline.interpolation_regions.set_series(
                self.baseline_regions.loc[name]
            )
        elif tab == "interpolation":

            sample.interpolation.regions.set_series(
                self.interpolation_regions.loc[name]
            )
        elif tab == "interference":

            sample.interference_sample.apply_settings(
                self.interference_settings["settings"].loc[name],
                groups=["baseline", "deconvolution"],
            )

            sample.interference_sample.baseline.interpolation_regions.set_series(
                self.interference_settings["baseline_interpolation_regions"].loc[name]
            )

        on_display_message.send(message="sample reset")

    def remove_samples(self, index: List[int]) -> None:

        # current_sample = self.files[self.current_sample_index]
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

    def save_results(self):
        for sample in self.spectra:
            name = sample.name
            sample.calculate_results()
            self.results.loc[name] = sample.results.copy()
            self.results.loc[name, "H2O"] = self.calculate_H2O(sample.results["rWS"])

    def export_results(
        self, folder: pathlib.Path, name: str, incl_settings: bool = True
    ):
        self.save_results()

        try:
            results = pd.concat([self.settings, self.results], axis=1).dropna(
                axis=1, how="all"
            )

            results.to_csv(folder / f"{name}.csv")
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

    def export_sample(
        self, filepath: pathlib.Path, sample: Optional[Sample_proccessor] = None
    ):
        if sample is None:
            sample = self.current_sample

        data = pd.DataFrame(
            {**{"x": sample.sample.signal.x}, **sample.sample.signal.all}
        )
        data.to_csv(filepath, index=False)

    def export_all(self, folderpath: pathlib.Path):

        folderpath.mkdir(parents=True, exist_ok=True)

        for sample in self.spectra:
            name = sample.name
            filepath = folderpath / f"{name}.csv"
            self.export_sample(filepath=filepath, sample=sample)
