from typing import Callable, Dict, Optional

import blinker as bl
import numpy as np
import pandas as pd
import scipy.stats as stat
import sklearn.metrics as met
from scipy.stats._stats_mstats_common import LinregressResult

from .database_controller import Database_controller


class Calibration_processor:

    on_display_message = bl.signal("display message")

    def __init__(self):
        self._H2OSi = None
        self._H2Oreference = None
        self.use = None

        self.initialised = False

        self._calibration: Optional[stat.LinregressResult] = None

    def calibrate_with_project(self, database_controller: Database_controller):
        self._database_controller = database_controller
        self._H2OSi = self._database_controller["H2OSi"]
        self._H2Oreference = self._database_controller.H2Oreference
        self.use = pd.Series(False, index=self.H2OSi.index)

        self.initialised = True

    def import_calibration(
        self, H2OSi: pd.Series, H2Oreference: pd.Series, use: pd.Series
    ):
        self._H2OSi = H2OSi.copy()
        self._H2Oreference = H2Oreference.copy()
        self.use = use.copy()

        self.initialised = True

    @property
    def H2OSi(self) -> pd.Series:
        return self._H2OSi[self.use]

    @property
    def H2Oreference(self) -> pd.Series:
        return self._H2Oreference[self.use]

    @property
    def calibration(self) -> LinregressResult:
        if self._calibration is None:
            self.calibrate()
        return self._calibration

    @property
    def get_calibration_parameters(self):
        return {
            "intercept": self.calibration.intercept,
            "slope": self.calibration.slope,
        }

    @property
    def RMSE(self) -> float:
        np.sqrt(
            met.mean_squared_error(self.H2Oreference, self._calculate_H2O(self.H2OSi))
        )

    @property
    def R2(self) -> float:
        return self.calibration.rvalue**2

    @property
    def p_value(self) -> float:
        return self.calibration.pvalue

    @property
    def errors_coefficient(self) -> Dict:
        return {
            "intercept": self.calibration.intercept_stderr,
            "slope": self.calibration.stderr,
        }

    def set_use_sample(self, sample_name: str, use: bool) -> None:
        if self.H2Oreference[sample_name] == np.nan:
            return self.on_display_message(message="No H2O set!")
        self.use[sample_name] = use

    def calibrate(self) -> None:
        if sum(self.use) < 2:
            return self.on_display_message(message="Not enough samples in calibration!")

        self._calibration = stat.linregress(self.H2OSi, self.H2Oreference)

    def _calculate_H2O(self, H2OSi):
        return self.calibration.intercept + H2OSi * self.calibration.slope

    def get_calibration_line(self, name: str) -> Callable:

        intercept, slope = self.calibration_parameters.values()

        def calibration_line(H2OSi):
            return intercept + H2OSi * slope

        calibration_line.__name__ = name

        return calibration_line

    def get_gui_variables(self) -> Dict:
        return {
            **{
                f"samplename_{i:02d}": f"{name[:15]:<17}"
                for i, name in enumerate(self.H2OSi.index)
            },
            **{f"h2oSi_{i:02d}": h2oSi for i, h2oSi in enumerate(self.H2OSi)},
            **{f"h2o_{i:02d}": h2o for i, h2o in enumerate(self.H2Oreference)},
            **{f"use_{i:02d}": use for i, use in enumerate(self.use)},
        }
