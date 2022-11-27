import os
import numpy as np
import pandas as pd

from typing import List, Optional, Dict, Union
import pathlib, tarfile
import warnings as w

from .. import app_settings
from .sample_processing import h2o_processor


class Sample_controller:
    def __init__(self):
        self.files: np.ndarray = np.array([], dtype=str)
        self.names: np.ndarray = np.array([], dtype=str)
        self.spectra: np.ndarray = np.array([], dtype=h2o_processor)

        self.settings: Optional[pd.DataFrame] = None
        self.baseline_regions: Optional[pd.DataFrame] = None
        self.interpolation_regions: Optional[pd.DataFrame] = None

        self.results: Optional[pd.DataFrame] = None

        self.current_sample_index: Optional[int] = None

        self.project = None

    @property
    def current_sample(self) -> h2o_processor:
        return self.get_sample(self.current_sample_index)

    @current_sample.setter
    def current_sample(self) -> None:
        w.warn("attribute is read only")

    # @property
    # def current_sample_index(self):
    #     return self._current_sample_index

    # @current_sample_index.setter
    # def current_sample_index(self, index: int) -> None:
    #     idx_max = len(self.spectra)
    #     if (index < 0) or (index > idx_max):
    #         raise ValueError(f"Index outside range (0,{idx_max}): {index}")

    #     self._current_sample_index = index

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

        # names = get_names_from_files(files)

        # for i, _ in enumerate(names):
        #     occurences = names.count(names[i])
        #     if occurences < 2:
        #         continue
        #     names[i] = f"{names[i]}_{occurences}"

        if settings is None:
            new_settings, new_birs, new_interpolation_regions = get_settings(names)

        else:
            new_settings = settings["general"]
            new_birs = settings["baseline_regions"]
            new_interpolation_regions = settings["interpolation_regions"]

        new_results = create_results_df(names)

        self.files = np.append(self.files, files)
        self.names = np.append(self.names, names)

        for file, name in zip(files, names):
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

        if self.settings is None:
            self.settings = new_settings
            self.baseline_regions = new_birs
            self.interpolation_regions = new_interpolation_regions

            self.results = new_results

            self.current_sample_index = 0
            # self.current_sample.calculate()

        else:
            self.settings = pd.concat([self.settings, new_settings], axis=0)
            self.baseline_regions = pd.concat([self.settings, new_birs], axis=0)
            self.interpolation_regions = pd.concat(
                [self.settings, new_interpolation_regions], axis=0
            )

            self.results = pd.concat([self.results, new_results], axis=0)

    def get_sample(self, index: int) -> h2o_processor:
        return self.spectra[index]

    def calculate_sample(self):
        sample = self.current_sample

        sample.calculate_baseline()
        sample.calculate_noise()
        sample.calculate_areas()

    def calculate_interpolation(self):
        sample = self.current_sample

        sample.calculate_interpolation()

    def change_sample_settings(self, **kwargs) -> None:
        sample = self.current_sample

        func_dict = {
            "birs": sample.set_birs,
            "baseline_smoothing": sample.set_baseline_smoothing,
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

        birs = self.current_sample.get_birs()

        baseline_smoothing = [self.current_sample.settings["baseline_smoothing"]]

        return {
            "birs": birs,
            "baseline_smoothing": baseline_smoothing,
        }

    def get_sample_results(self):

        all_results = list(self.current_sample.results.values)
        areas = all_results[:3]
        areas[:2] = [int(i) for i in all_results[:2]]
        areas[2] = round(all_results[2], 2)

        signal = all_results[3:]

        return {"areas": areas, "signal": signal}

    def get_sample_plotdata(self):

        sample = self.current_sample
        return sample.get_plot_data()

    def save_sample(self) -> None:

        sample = self.current_sample
        name = sample.name

        # save current settings
        self.settings.loc[name] = sample.settings.copy()
        self.baseline_regions.loc[name] = sample.baseline_regions.copy()
        self.interpolation_regions.loc[name] = sample.interpolation_regions.copy()

        self.results.loc[name] = sample.results.copy()

    def save_all_samples(self) -> None:
        pass

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

    def load_project(self, filepath):

        with tarfile.open(filepath, "r") as tar:
            names = [member.name for member in tar]
            # csvs = [name for name in names if name.endswith(".csv")]
            spectra = [name for name in names if name.endswith(".sp")]
            spectrum_files = [tar.extractfile(spectrum) for spectrum in spectra]

            self.settings = pd.read_csv(tar.extractfile("settings.csv"), index_col=[0])
            self.baseline_regions = pd.read_csv(
                tar.extractfile("baseline_regions.csv"), index_col=[0], header=[0, 1]
            )
            self.interpolation_regions = pd.read_csv(
                tar.extractfile("interpolation_regions.csv"),
                index_col=[0],
                header=[0, 1],
            )


def get_settings(names: List) -> pd.DataFrame:

    baseline_correction, interpolation = app_settings.process

    birs = pd.concat([baseline_correction["birs"].copy()] * len(names), axis=1).T
    birs.index = names

    interpolation_regions = pd.concat(
        [interpolation["regions"].copy()] * len(names), axis=1
    ).T
    interpolation_regions.index = names

    settings_df = pd.DataFrame(
        {
            "baseline_smoothing": baseline_correction["smoothing"],
            "interpolation": interpolation["use"],
            "interpolation_smoothing": interpolation["smoothing"],
        },
        index=names,
    )

    return settings_df, birs, interpolation_regions


def create_results_df(names: List) -> pd.DataFrame:
    colnames = ["SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR"]
    return pd.DataFrame(index=names, columns=colnames, dtype=float)


def get_names_from_files(files: List) -> List:
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

    return names
