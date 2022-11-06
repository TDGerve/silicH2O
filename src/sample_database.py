import os
import numpy as np
import pandas as pd

from typing import List, Optional
import warnings as w

from . import settings
from .sample_processing import h2o_processor


class Sample_database:
    def __init__(self):
        self.files: List[str] = []
        self.names: List[str] = []
        self.spectra: List[h2o_processor] = []

        self.settings: Optional[pd.DataFrame] = None
        self.results: Optional[pd.DataFrame] = None

        self._current_sample_index: Optional[str] = None

    @property
    def current_sample(self) -> h2o_processor:
        return self.retrieve_sample(self.current_sample_index)

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

    def read_files(self, files: List[str]) -> None:

        names = get_names_from_files(files)

        for file, name in zip(files, names):
            x, y = np.genfromtext(file, unpack=True)
            self.spectra.append(h2o_processor(name, x, y))

        self.files += files
        self.names += names

        new_settings = create_settings_df(names)
        new_results = create_results_df(names)

        if not self.settings:
            self.settings = new_settings
            self.results = new_results

            self.set_current_sample(0)

        else:
            self.settings = pd.concat([self.settings, new_results], axis=0)
            self.results = pd.concat([self.results, new_results], axis=0)

    def retrieve_sample(self, index: int) -> h2o_processor:
        sample = self.spectra[index]
        sample.settings = self.settings.loc[sample.name].copy()

        return sample

    def save_current_sample(self) -> None:

        self.settings.loc[
            self.current_sample.name
        ] = self.current_sample.settings.copy()

        self.results.loc[self.current_sample.name] = self.current_sample.results.copy()

    def restore_current_sample(self) -> None:

        self.current_sample.settings = self.settings.loc[
            self.current_sample.name
        ].copy()

        self.current_sample.results = self.results.loc[self.current_sample.name].copy()


def create_settings_df(names: List) -> pd.DataFrame:

    settings_df = pd.DataFrame(
        np.nan, index=names, columns=settings.process.index, dtype=object
    )

    settings_df["birs"] = settings.process["birs"]
    settings_df["interpolate"] = settings.process["interpolate"]

    return settings_df


def create_results_df(names: List) -> pd.DataFrame:
    colnames = ["SiArea", "H2Oarea", "rWS"]
    return pd.DataFrame(index=names, columns=colnames, dtype=float)


def get_names_from_files(files: List) -> List:
    separator = settings.general["name_separator"]
    names = tuple()

    for file in files:
        name = os.path.basename(file)
        if separator not in name:
            names = names + tuple([name])
        else:
            names = names + tuple([name[: name.find(separator)]])

    return names
