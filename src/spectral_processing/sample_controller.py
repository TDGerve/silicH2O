import os
import pathlib
import tarfile
import warnings as w
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .. import app_settings
from ..Dataframes import Baseline_DF, Interpolation_DF, Results_DF, Settings_DF
from .sample_processing import h2o_processor


class Sample_controller:
    def __init__(self):
        self.files: np.ndarray = np.array([], dtype=str)
        self.names: np.ndarray = np.array([], dtype=str)
        self.spectra: np.ndarray = np.array([], dtype=h2o_processor)

        self.settings: pd.DataFrame = Settings_DF()
        self.baseline_regions: pd.DataFrame = Baseline_DF()
        self.interpolation_regions: pd.DataFrame = Interpolation_DF()

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
            new_settings, new_birs, new_interpolation_regions = get_default_settings(
                names
            )

        else:
            new_settings = settings["general"]
            new_birs = settings["baseline_regions"]
            new_interpolation_regions = settings["interpolation_regions"]

        new_results = Results_DF(index=names)  # create_results_df(names)

        old_files = len(self.files)

        self.files = np.append(self.files, files)
        self.names = np.append(self.names, names)

        # new_files = len(self.files)

        # if self.settings is None:
        #     self.settings = new_settings
        #     self.baseline_regions = new_birs
        #     self.interpolation_regions = new_interpolation_regions

        #     self.results = new_results

        #     self.current_sample_index = 0
        #     # self.current_sample.calculate()

        # else:
        self.settings = pd.concat([self.settings, new_settings], axis=0)
        self.baseline_regions = pd.concat([self.baseline_regions, new_birs], axis=0)
        self.interpolation_regions = pd.concat(
            [self.interpolation_regions, new_interpolation_regions], axis=0
        )

        self.results = pd.concat([self.results, new_results], axis=0)

        # for idx in np.arange(old_files, new_files):
        #     self.save_sample(idx=idx)

        for idx, (file, name) in enumerate(
            zip(self.files[old_files:], self.names[old_files:])
        ):
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

    def get_sample(self, index: int) -> h2o_processor:
        return self.spectra[index]

    def calculate_sample(self, idx=None):
        if idx is None:
            sample = self.current_sample
        else:
            sample = self.get_sample(idx)

        sample.calculate_baseline()
        sample.calculate_noise()
        sample.calculate_areas()

    def calculate_interpolation(self):
        sample = self.current_sample

        sample.calculate_interpolation()

    def change_sample_settings(self, **kwargs) -> None:
        sample = self.current_sample

        func_dict = {
            "baseline": sample.set_baseline,
            "interpolate": sample.set_interpolation,
        }

        for key, value in kwargs.items():
            func_dict[key](value)

        # if birs is not None:

        #     sample.set_birs(**birs)
        # if baseline_smoothing is not None:
        #     sample.set_baseline_smoothing(baseline_smoothing)

        # if interpolate is None:
        #     return
        # sample.set_interpolation(interpolate)

    def get_sample_settings(self):

        baseline = self.current_sample.get_birs()

        baseline["smoothing"] = self.current_sample.settings["baseline_smoothing"]

        # baseline_smoothing = [self.current_sample.settings["baseline_smoothing"]]

        return {
            "baseline": baseline,
            # "baseline_smoothing": baseline_smoothing,
        }

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

    def save_sample(self, idx=None) -> None:

        if idx is None:
            sample = self.current_sample
        else:
            sample = self.get_sample(idx)
        name = sample.name

        # save current settings
        self.settings.loc[name] = sample.settings.copy()
        self.baseline_regions.loc[name] = sample.baseline_regions.copy()
        self.interpolation_regions.loc[name] = sample.interpolation_regions.copy()

        self.results.loc[name] = sample.results.copy()

    def save_all_samples(self) -> None:

        for sample_idx in range(self.results.shape[0]):
            self.save_sample(sample_idx)

    def reset_sample(self) -> None:

        sample = self.current_sample
        name = sample.name

        # restore previous settings
        sample.settings = self.settings.loc[name].copy()
        sample.baseline_regions = self.baseline_regions.loc[name].copy()
        sample.interpolation_regions = self.interpolation_regions.loc[name].copy()

    def remove_samples(self, index: List[int]) -> None:

        current_sample = self.files[self.current_sample_index]
        remove_samples = self.names[index]

        self.spectra = np.delete(self.spectra, index)
        self.files = np.delete(self.files, index)
        self.names = np.delete(self.names, index)

        self.results = self.results.drop(labels=remove_samples, axis=0)
        self.settings = self.settings.drop(labels=remove_samples, axis=0)

        try:
            current_sample_index, _ = np.where(self.files == current_sample)
            self.current_sample_index = int(current_sample_index)
        except TypeError:
            self.current_sample_index = 0

    def save_project_as(self, filepath: pathlib.Path, name: str):

        # project folder
        temp_path = pathlib.Path(__file__).parents[1] / "temp" / name
        temp_path.mkdir(parents=True, exist_ok=True)
        # data folder
        temp_datapath = temp_path / "data"
        temp_datapath.mkdir(exist_ok=True)

        for sample in self.spectra:
            data = np.column_stack([sample.data.signal.x, sample.data.signal.raw])
            np.savetxt(temp_datapath / f"{sample.name}.sp", data)

        fnames = ["settings", "baseline_regions", "interpolation_regions"]
        data = [self.settings, self.baseline_regions, self.interpolation_regions]
        for f, name in zip(data, fnames):
            f.to_csv(temp_path / f"{name}.csv")

        with tarfile.open(filepath, mode="w") as tar:
            tar.add(temp_path, arcname="")

        self.project = filepath

    # def load_project(self, filepath):

    #     with tarfile.open(filepath, "r") as tar:
    #         names = [member.name for member in tar]
    #         # csvs = [name for name in names if name.endswith(".csv")]
    #         spectra = [name for name in names if name.endswith(".sp")]
    #         spectrum_files = [tar.extractfile(spectrum) for spectrum in spectra]

    #         self.settings = pd.read_csv(tar.extractfile("settings.csv"), index_col=[0])
    #         self.baseline_regions = pd.read_csv(
    #             tar.extractfile("baseline_regions.csv"), index_col=[0], header=[0, 1]
    #         )
    #         self.interpolation_regions = pd.read_csv(
    #             tar.extractfile("interpolation_regions.csv"),
    #             index_col=[0],
    #             header=[0, 1],
    # )

    def export_results(
        self, folder: pathlib.Path, name: str, incl_settings: bool = True
    ):
        print(folder, "\n", name)
        pd.concat([self.settings, self.results], axis=1).to_csv(folder / f"{name}.csv")

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

        baseline_settings.to_csv(folder / f"{name}_baselines.csv")


def get_default_settings(names: List) -> pd.DataFrame:

    baseline_correction, interpolation = app_settings.process

    # birs = pd.concat([baseline_correction["birs"].copy()] * len(names), axis=1).T
    # birs.index = names

    birs = Baseline_DF([baseline_correction["birs"].copy()] * len(names), index=names)

    # interpolation_regions = pd.concat(
    #     [interpolation["regions"].copy()] * len(names), axis=1
    # ).T
    # interpolation_regions.index = names

    interpolation_regions = Interpolation_DF(
        [interpolation["regions"].copy()] * len(names), index=names
    )

    data = [
        [
            baseline_correction["smoothing"],
            interpolation["use"],
            interpolation["smoothing"],
        ]
    ] * len(names)

    settings_df = Settings_DF(data, index=names)

    # settings_df = pd.DataFrame(
    #     {
    #         "baseline_smoothing": baseline_correction["smoothing"],
    #         "interpolation": interpolation["use"],
    #         "interpolation_smoothing": interpolation["smoothing"],
    #     },
    #     index=names,
    # )

    return settings_df, birs, interpolation_regions


# def create_results_df(names: List) -> pd.DataFrame:
#     colnames = ["SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR"]
#     return pd.DataFrame(index=names, columns=colnames, dtype=float)
