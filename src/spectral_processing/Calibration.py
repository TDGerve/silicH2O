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
        self._H2Oreference = pd.Series(dtype=float, name="H2Oref")
        self.use = pd.Series(dtype=bool, name="use")

        self._calibration: Optional[stat.LinregressResult] = None
        self.name: Optional[str] = None
        self.use_calibration = False

        self._database_controller = None

    @property
    def names(self):
        return list(self._H2OSi.index)

    @property
    def initialised(self):
        return len(self._H2OSi) > 0

    def calibrate_with_project(self, database_controller: Database_controller):
        database_controller.save_results()
        self._database_controller = database_controller
        self._H2OSi = self._database_controller.results["rWS"]
        self._H2Oreference = pd.Series(
            np.nan, index=self._H2OSi.index, name="H2Oreference"
        )
        self.use = pd.Series(False, index=self._H2OSi.index, name="use")

    def import_calibration(
        self, name: str, H2OSi: pd.Series, H2Oreference: pd.Series, use: pd.Series
    ):
        self.import_calibration_data(
            H2OSi=H2OSi.copy(), H2Oreference=H2Oreference.copy(), use=use.copy()
        )

        self.name = name

    def import_calibration_data(self, **kwargs):
        data = {
            "H2OSi": "_H2OSi",
            "H2Oreference": "_H2Oreference",
            "use": "use",
            "name": "name",
        }
        for name, attr in data.items():
            vals = kwargs.pop(name, None)
            if vals is None:
                continue
            setattr(self, attr, vals)

    @property
    def H2OSi(self) -> pd.Series:
        return self._H2OSi[self.use].dropna()

    @property
    def H2Oreference(self) -> pd.Series:
        return self._H2Oreference[self.use].dropna()

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
    def SEE(self) -> float:
        try:
            SEE = np.sqrt(
                met.mean_squared_error(
                    self.H2Oreference, self._calculate_H2O(self.H2OSi)
                )
            )
        except (TypeError, ValueError):
            SEE = 0
        return SEE

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
        if len(self.H2OSi) < 2:
            return self.on_display_message.send(
                message="Not enough samples in calibration!"
            )

        self._calibration = stat.linregress(self.H2OSi, self.H2Oreference)

    def _calculate_H2O(self, H2OSi):
        if self._calibration is None:
            return None

        return np.round(self.calibration.intercept + H2OSi * self.calibration.slope, 3)

    # def get_calibration_line(self) -> Callable:

    #     if self._calibration is None:
    #         return None

    #     intercept, slope = self.coefficients

    #     def calibration_line(H2OSi):
    #         return intercept + H2OSi * slope

    #     calibration_line.__name__ = "" if not self.name else self.name

    #     return calibration_line

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
            "SEE": f"{self.SEE: .2f}",
            "p_value": f"{self.p_value:.2e}",
            "intercept": f"{self.coefficients[0]: .2f} \u00B1 {self.errors_coefficient[0]: .2f}",
            "slope": f"{self.coefficients[1]: .2f} \u00B1 {self.errors_coefficient[1]: .2f}",
            "use_calibration": self.use_calibration,
        }

    def get_plotdata(self) -> Dict:
        return {
            "standards": (self.H2OSi, self.H2Oreference),
            "calibration_line": self._calculate_H2O,
            "name": self.name,
        }
