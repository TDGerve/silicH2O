import pandas as pd

settings_columns = (
    "baseline_smoothing",
    "interpolation",
    "interpolation_smoothing",
)

baseline_columns = pd.MultiIndex.from_tuples(
    [
        ("0", "from"),
        ("0", "to"),
        ("1", "from"),
        ("1", "to"),
        ("2", "from"),
        ("2", "to"),
        ("3", "from"),
        ("3", "to"),
        ("4", "from"),
        ("4", "to"),
    ],
)

interpolation_columns = pd.MultiIndex.from_tuples(
    [("0", "from"), ("0", "to")],
)

results_columns = ("SiArea", "H2Oarea", "rWS", "noise", "Si_SNR", "H2O_SNR")


class Settings_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            columns=settings_columns,
            **kwargs,
        )


class Baseline_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, columns=baseline_columns, dtype="float32", **kwargs)


class Interpolation_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, columns=interpolation_columns, dtype="float32", **kwargs
        )


class Results_DF(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, columns=results_columns, dtype="float32", **kwargs)
