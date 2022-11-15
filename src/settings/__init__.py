import json
import pandas as pd
import numpy as np

from itertools import product


def get_process_settings():
    with open(f"{__path__[0]}/process_settings.json") as f:
        process = json.load(f)

    index = pd.MultiIndex.from_tuples(
        (int(i), j) for i, j in product(process["birs"], ("from", "to"))
    )
    values = np.concatenate(list(process["birs"].values()))

    birs = pd.Series(values, index=index)

    interpolate = process["interpolate"]
    interpolate["region"] = pd.Series(
        *interpolate["region"], index=((0, "from"), (0, "to"))
    )

    return birs, interpolate


with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)

with open(f"{__path__[0]}/general_settings.json") as f:
    general = json.load(f)


process = get_process_settings()
