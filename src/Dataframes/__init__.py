from itertools import product
from typing import Union

import numpy as np
import pandas as pd

settings_columns = pd.MultiIndex.from_tuples(
    [
        ("baseline", "smoothing"),
        ("interpolation", "use"),
        ("interpolation", "smoothing"),
        ("interference", "use"),
        ("interference", "boundary_left"),
        ("interference", "boundary_right"),
        ("interference", "smoothing"),
        ("interference", "peak_prominence"),
        ("interference", "noise_threshold"),
        ("interference", "fit_window"),
        ("interference", "baseline_smoothing"),
    ],
)


def baseline_multiindex(bir_amount: int):
    index = []
    for i, j in product(range(bir_amount), ("from", "to")):
        index.append((str(i), j))
    return pd.MultiIndex.from_tuples(index)


results_columns = ("SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR")


class Settings_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            columns=settings_columns,
            **kwargs,
        )


class Baseline_DF(pd.DataFrame):
    def __init__(self, bir_amount, *args, **kwargs):
        super().__init__(
            *args, columns=baseline_multiindex(bir_amount), dtype="int16", **kwargs
        )


class Results_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, columns=results_columns, dtype="float32", **kwargs)


def _match_columns(left: pd.DataFrame, right: Union[pd.DataFrame, pd.Series]):

    if isinstance(right, pd.DataFrame):
        right_names = right.columns
    elif isinstance(right, pd.Series):
        right_names = right.index

    missing_right = left.columns.difference(right_names)
    missing_left = right_names.difference(left.columns)

    new_left = left.copy()
    new_right = right.copy()

    new_left[missing_left] = np.nan
    new_right[missing_right] = np.nan

    return [new_left, new_right]


def _insert_row(df: pd.DataFrame, row: pd.Series):

    df_new, row_new = _match_columns(df, row)

    df_new.loc[row_new.name] = row_new

    return df_new
