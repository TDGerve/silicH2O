import json
import shutil
from itertools import product
from typing import Dict, List, Tuple

import numpy as np
import numpy.typing as npt
import pandas as pd

from ..Dataframes import Baseline_DF


def make_bir_series(birs: Dict[str, Tuple[int, int]]):
    index = pd.MultiIndex.from_tuples(
        (int(i), j) for i, j in product(birs, ("from", "to"))
    )
    values = np.concatenate(list(birs.values()))

    return pd.Series(values, index=index)


def get_settings_from_json(type: str):
    with open(f"{__path__[0]}/{type}_settings.json") as f:
        process = json.load(f)

    names = process.keys()

    return names, process.values()


# GUI SETTINGS
with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)
gui["background_color"] = None
gui["current_tab"] = "baseline"

# GENERAL SETTINGS
with open(f"{__path__[0]}/general_settings.json") as f:
    general = json.load(f)
# data_processing["processing_settings"] = get_settings_from_json("processing_settings")


def get_default_settings(
    names: List[str], type: str
) -> Tuple[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:

    setting_names, dicts = get_settings_from_json(type)

    baseline_interpolation_regions = []
    for dic in dicts:
        birs = dic.pop("baseline_interpolation_regions", None)
        if birs is None:
            continue
        bir_amount = len(birs.keys())
        values = np.array(list(birs.values())).flatten()

        baseline_interpolation_regions.append(
            Baseline_DF(bir_amount, [values] * len(names), index=names).squeeze()
        )

    settings = []
    for name, dic in zip(
        setting_names,
        dicts,
    ):

        df = pd.DataFrame(dic, index=names)
        df.columns = pd.MultiIndex.from_product([[name], df.columns])
        settings.append(df)

    settings = pd.concat(settings, axis=1)

    return settings, baseline_interpolation_regions


def set_glass_settings(
    baseline_interpolation_regions: npt.NDArray,
    interpolation_regions: npt.NDArray,
    settings: Dict,
):
    baseline_settings = settings.pop("baseline")
    interpolation_settings = settings.pop("interpolation")

    baseline_interpolation_regions = {
        i: list(region) for i, region in enumerate(baseline_interpolation_regions)
    }

    interpolation_regions = {
        str(i): list(region) for i, region in enumerate(interpolation_regions)
    }
    settings = {
        "baseline": {
            "baseline_interpolation_regions": baseline_interpolation_regions,
            **baseline_settings,
        },
        "interpolation": {
            "baseline_interpolation_regions": interpolation_regions,
            **interpolation_settings,
        },
        "interference": settings["interference"].to_dict(),
    }

    with open(f"{__path__[0]}/glass_settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def set_interference_settings(baseline_interpolation_regions: Dict, settings: Dict):
    baseline_settings = settings.pop("baseline")

    baseline_interpolation_regions = {
        i: list(region) for i, region in enumerate(baseline_interpolation_regions)
    }

    settings = {
        "baseline": {
            "baseline_interpolation_regions": baseline_interpolation_regions,
            **baseline_settings,
        },
        "deconvolution": settings["deconvolution"].to_dict(),
    }

    with open(f"{__path__[0]}/interference_settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def reset_default_settings(type: str):
    if type not in ("glass", "interference"):
        raise ValueError(f"{type} not recognised as type")
    basepath = __path__[0]
    shutil.copyfile(
        src=f"{basepath}/{type}_settings_default.json",
        dst=f"{basepath}/{type}_settings.json",
    )
