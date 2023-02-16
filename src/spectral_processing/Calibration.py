from typing import Callable, Dict, Optional, Tuple

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
        self._H2OSi = pd.Series(dtype=float)
        self._H2Oreference = pd.Series(dtype=float)
        self.use = pd.Series(dtype=bool)

        self._calibration: Optional[stat.LinregressResult] = None

    @property
    def initialised(self):
        return len(self._H2OSi) > 0

    def calibrate_with_project(self, database_controller: Database_controller):
        database_controller.save_results()
        self._database_controller = database_controller
        self._H2OSi = self._database_controller.results["rWS"]
        self._H2Oreference = self._database_controller.H2Oreference.copy()
        self.use = pd.Series(False, index=self._H2OSi.index)

    def import_calibration(
        self, H2OSi: pd.Series, H2Oreference: pd.Series, use: pd.Series
    ):
        self._H2OSi = H2OSi.copy()
        self._H2Oreference = H2Oreference.copy()
        self.use = use.copy()

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
    def coefficients(self) -> Tuple[float, float]:
        try:
            return self.calibration.intercept, self.calibration.slope
        except AttributeError:
            return 0, 0

    @property
    def RMSE(self) -> float:
        try:
            np.sqrt(
                met.mean_squared_error(
                    self.H2Oreference, self._calculate_H2O(self.H2OSi)
                )
            )
        except AttributeError:
            return 0

    @property
    def R2(self) -> float:
        try:
            return self.calibration.rvalue**2
        except AttributeError:
            return 0

    @property
    def p_value(self) -> float:
        try:
            return self.calibration.pvalue
        except AttributeError:
            return 0

    @property
    def errors_coefficient(self) -> Tuple[float, float]:
        try:
            return self.calibration.intercept_stderr, self.calibration.stderr

        except AttributeError:
            return 0, 0

    def set_H2Oreference(self, sample_index, H2O):
        self._H2Oreference.iloc[sample_index] = H2O

    def set_use_sample(self, sample_name: str, use: bool) -> None:
        if self.H2Oreference[sample_name] == np.nan:
            return self.on_display_message.send(message="No H2O set!")
        self.use[sample_name] = use

    def calibrate(self) -> None:
        if sum(self.use) < 2:
            return self.on_display_message.send(
                message="Not enough samples in calibration!"
            )

        self._calibration = stat.linregress(self.H2OSi, self.H2Oreference)

    def _calculate_H2O(self, H2OSi):
        return self.calibration.intercept + H2OSi * self.calibration.slope

    def get_calibration_line(self, name: str) -> Callable:

        intercept, slope = self.calibration_parameters.values()

        def calibration_line(H2OSi):
            return intercept + H2OSi * slope

        calibration_line.__name__ = name

        return calibration_line

    def get_sampleinfo_gui(self) -> Dict:
        return {
            **{
                f"samplename_{i:02d}": f"{name[:15]:<17}"
                for i, name in enumerate(self._H2OSi.index)
            },
            **{
                f"h2oSi_{i:02d}": f"{h2oSi: .2f}" for i, h2oSi in enumerate(self._H2OSi)
            },
            **{
                f"h2o_{i:02d}": f"{h2o: .2f}"
                for i, h2o in enumerate(self._H2Oreference)
            },
            **{f"use_{i:02d}": use for i, use in enumerate(self.use)},
        }

    def get_calibration_parameters_gui(self) -> Dict:
        return {
            "R2": f"{self.R2: .2f}",
            "RMSE": f"{self.RMSE: .2f}",
            "p_value": f"{self.p_value:.2e}",
            "intercept": f"{self.coefficients[0]: .2f} \u00B1 {self.errors_coefficient[0]: .2f}",
            "slope": f"{self.coefficients[1]: .2f} \u00B1 {self.errors_coefficient[1]: .2f}",
        }
