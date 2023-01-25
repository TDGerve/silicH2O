import json
from itertools import product

import numpy as np
import pandas as pd


def get_glass_settings():
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


def get_settings_from_json(file: str):
    with open(f"{__path__[0]}/{file}.json") as f:
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


# GUI SETTINGS
with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)
gui["background_color"] = None
gui["current_tab"] = None

# DATA PROCESSING SETTINGS
with open(f"{__path__[0]}/general_settings.json") as f:
    data_processing = json.load(f)
data_processing["glass"] = get_settings_from_json("glass_settings")
data_processing["interference"] = get_settings_from_json("interference_settings")
