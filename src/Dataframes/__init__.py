from itertools import product
from typing import Union

import numpy as np
import pandas as pd
from numpy import dtype

settings_columns = pd.MultiIndex.from_tuples(
    [
        ("baseline", "smoothing"),
    ],
)


def baseline_multiindex(bir_amount: int):
    index = []
    for i, j in product(range(bir_amount), ("from", "to")):
        index.append((str(i), j))
    return pd.MultiIndex.from_tuples(index)


results_columns = ("SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR", "H2O")


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

    # if isinstance(right, pd.DataFrame):
    #     right_names = right.columns
    # elif isinstance(right, pd.Series):
    #     right_names = right.index

    new_left = left.copy()
    new_right = right.copy()

    if isinstance(right, pd.Series):
        new_right = pd.DataFrame(new_right).T

    right_names = new_right.columns

    missing_right = new_left.columns.difference(right_names)
    missing_left = right_names.difference(new_left.columns)

    if all([len(missing) < 1 for missing in (missing_left, missing_right)]):
        return [new_left, new_right]

    dtypes_left = right[missing_left].dtypes
    dtypes_right = left[missing_right].dtypes

    new_left[missing_left] = _get_fill_values(dtypes_left)
    # Loop in case 'right' is a series
    for missing, type in zip(missing_right, dtypes_right):
        new_right[missing] = _get_fill_values(type)

    return [new_left, new_right]


def _insert_row(df: pd.DataFrame, row: pd.Series):

    df_new, row_new = _match_columns(df, row)

    df_new.loc[row_new.name] = row_new

    return df_new


def _get_fill_values(dtypes):
    try:
        return [fill_values[type] for type in dtypes.values]
    except AttributeError:
        return fill_values[dtypes]


fill_values = {
    dtype("int16"): np.nan,
    dtype("int64"): np.nan,
    dtype("float64"): np.nan,
    dtype(bool): False,
    dtype("O"): np.nan,
}
