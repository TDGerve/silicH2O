import json
import pandas as pd
import numpy as np

from itertools import product


def get_process_settings():
    with open(f"{__path__[0]}/process_settings.json") as f:
        process = json.load(f)

    baseline_correction = process["baseline_correction"]
    index = pd.MultiIndex.from_tuples(
        (int(i), j) for i, j in product(baseline_correction["birs"], ("from", "to"))
    )
    values = np.concatenate(list(baseline_correction["birs"].values()))

    birs = pd.Series(values, index=index)
    baseline_correction["birs"] = birs

    interpolation = process["interpolation"]
    interpolation["regions"] = pd.Series(
        interpolation["regions"]["0"], index=((0, "from"), (0, "to"))
    )

    return baseline_correction, interpolation


with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)

with open(f"{__path__[0]}/general_settings.json") as f:
    general = json.load(f)


process = get_process_settings()
