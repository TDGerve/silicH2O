import os
import numpy as np
import pandas as pd

from typing import List, Optional, Tuple, Dict
import warnings as w

from . import settings
from .sample_processing import h2o_processor


class Sample_controller:
    def __init__(self):
        self.files: np.ndarray[str] = np.array([], dtype=str)
        self.names: np.ndarray[str] = np.array([], dtype=str)
        self.spectra: np.ndarray[h2o_processor] = np.array([], dtype=h2o_processor)

        self.settings: Optional[pd.DataFrame] = None
        self.results: Optional[pd.DataFrame] = None

        self._current_sample_index: Optional[str] = None

    @property
    def current_sample(self) -> h2o_processor:
        return self.retrieve_sample(self._current_sample_index)

    @current_sample.setter
    def current_sample(self) -> None:
        w.warn("Current sample is private")

    @property
    def current_sample_index(self):
        return self._current_sample_index

    @current_sample_index.setter
    def current_sample_index(self, index: int) -> None:
        idx_max = len(self.spectra)
        if (index < 0) or (index > idx_max):
            raise ValueError(f"Index outside range (0,{idx_max}): {index}")

        self._current_sample_index = index
        # Retrieve the saved settings
        self.current_sample.settings = self.settings.loc[
            self.current_sample.name
        ].copy()

    def read_files(self, files: List[str]) -> None:

        names = get_names_from_files(files)

        for i, _ in enumerate(names):
            occurences = names.count(names[i])
            if occurences < 2:
                continue
            names[i] = f"{names[i]}_{occurences}"

        new_settings = create_settings_df(names)
        new_results = create_results_df(names)

        self.files = np.append(self.files, files)
        self.names = np.append(self.names, names)

        for file, name in zip(files, names):
            x, y = np.genfromtxt(file, unpack=True)
            self.spectra = np.append(
                self.spectra, h2o_processor(name, x, y, new_settings.loc[name].copy())
            )

        if self.settings is None:
            self.settings = new_settings
            self.results = new_results

            self.current_sample_index = 0
            # self.current_sample.calculate()

        else:
            self.settings = pd.concat([self.settings, new_settings], axis=0)
            self.results = pd.concat([self.results, new_results], axis=0)

    def retrieve_sample(self, index: int) -> h2o_processor:
        return self.spectra[index]

    def calculate_sample(self):
        sample = self.current_sample

        sample.calculate_interpolation()
        birs = np.reshape(list(sample.birs.values()), (5, 2))
        sample.data.baselineCorrect(baseline_regions=birs)

        sample.data.calculate_SiH2Oareas()
        sample.results[["SiArea", "H2Oarea"]] = sample.data.SiH2Oareas
        sample.results["rWS"] = sample.results["H2Oarea"] / sample.results["SiArea"]

        return sample.results["rWS"]

    def change_sample_settings(
        self, birs: dict = None, interpolate: dict = None
    ) -> None:
        sample = self.current_sample
        if birs is not None:

            sample.set_birs(**birs)
        if interpolate is None:
            return
        sample.set_interpolation(interpolate)

    def get_sample_settings(self):
        return self.current_sample.retrieve_plot_data

    def save_sample(self) -> None:

        self.settings.loc[
            self.current_sample.name
        ] = self.current_sample.settings.copy()

        self.results.loc[self.current_sample.name] = self.current_sample.results.copy()

    def restore_sample(self) -> None:

        self.current_sample.settings = self.settings.loc[
            self.current_sample.name
        ].copy()

        self.current_sample.results = self.results.loc[self.current_sample.name].copy()

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


def create_settings_df(names: List) -> pd.DataFrame:

    birs, interpolate = settings.process

    birs_df = pd.concat([birs.copy()] * len(names), axis=1).T
    birs_df.index = names

    return birs_df


def create_results_df(names: List) -> pd.DataFrame:
    colnames = ["SiArea", "H2Oarea", "rWS"]
    return pd.DataFrame(index=names, columns=colnames, dtype=float)


def get_names_from_files(files: List) -> List:
    separator = settings.general["name_separator"]
    names = []

    for file in files:
        name = os.path.basename(file)
        if separator not in name:
            names.append(name)
        else:
            names.append(name[: name.index(separator)])

    return names
