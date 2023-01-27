from itertools import product

import pandas as pd

settings_columns = (
    "baseline_smoothing",
    "interpolation",
    "interpolation_smoothing",
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
            *args, columns=baseline_multiindex(bir_amount), dtype="float32", **kwargs
        )


# class Interpolation_DF(pd.DataFrame):
#     def __init__(self, bir_amount, *args, **kwargs):
#         super().__init__(
#             *args, columns=baseline_multiindex(bir_amount), dtype="float32", **kwargs
#         )


class Results_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, columns=results_columns, dtype="float32", **kwargs)
