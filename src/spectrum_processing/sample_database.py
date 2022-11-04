import pandas as pd
import numpy as np

import os, pathlib, ast
from typing import List
import tkinter as tk

import ramCOH as ram

from .. import settings


class samples:

    baseline_smoothing = 1
    files = []
    names = []
    sample_idx: int | None = None
    sample: ram.H2O | None = None
    results: pd.DataFrame | None = None

    def add_files(self, filenames: str | List):

        if not isinstance(filenames, (list, tuple)):
            filenames = [filenames]

        self.files += filenames
        self.names += get_names_from_files(filenames)

        if not self.results:
            self.initialise_results(self.names)
            self.sample_idx = 0
            self.process_spectrum()

    def initialise_results(self, names: List):
        colnames = [
            "name",
            "SiArea",
            "H2Oarea",
            "rWS",
            "interpolate",
            "interp_left",
            "interp_right",
            "interp_smoothing",
            "Si_bir",
            "h2o_left",
            "h2o_right",
        ]
        self.results = pd.DataFrame(np.nan, index=names, columns=colnames)
        self.results["interpolate"] = False
        self.results["interp_smoothing"] = settings.process["interpolation_smoothing"]
        self.results["h2o_left"] = int(settings.process["H2O_left"])
        self.results["h2o_right"] = int(settings.process["H2O_right"])
        self.results["Si_bir"] = f"{settings.birs}"

    def select_sample(self, idx, *args, **kwargs):
        self.sample_idx = idx
        self.process_spectrum(*args, **kwargs)

    def process_spectrum(self, Si_birs=None, h2o_boundaries=None):
        file = self.files[self.sample_idx]
        name = self.names[self.sample_idx]
        laser = settings.process["laser_wavelength"]

        if Si_birs is None:
            Si_birs = ast.literal_eval(self.results.loc[name, "Si_bir"])
            print(Si_birs, type(Si_birs))
        if h2o_boundaries is None:
            h2o_boundaries = self.results.loc[name, ["h2o_left", "h2o_right"]]

        x, y = np.genfromtxt(file, unpack=True)
        self.sample = ram.H2O(x, y, laser=laser)
        self.sample.baselineCorrect(
            Si_birs=Si_birs,
            H2O_boundaries=h2o_boundaries,
            smooth_factor=self.baseline_smoothing,
        )
        self.sample.calculate_SiH2Oareas()

    def save_results(self):
        name = self.names[self.sample_idx]
        Si_area, H2O_area = self.sample.SiH2Oareas

        self.results.loc[name, ["Si_area", "H2O_area"]]
        self.results.loc[name, ["rWS"]] = H2O_area / Si_area


def get_names_from_files(files):
    separator = settings.process["name_separator"]
    names = tuple()

    for file in files:
        name = os.path.basename(file)
        if separator not in name:
            names = names + tuple([name])
        else:
            names = names + tuple([name[: name.find(separator)]])

    return names
