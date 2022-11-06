import json
import pandas as pd


def get_process_settings():
    with open(f"{__path__[0]}/process_settings.json") as f:
        process = json.load(f)
    process = {k: pd.Series(v) for k, v in process.items()}
    return pd.concat(process)


with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)

with open(f"{__path__[0]}/general_settings.json") as f:
    general = json.load(f)


import pathlib

path = pathlib.Path(__file__)
path = path.parents[0]

with open(f"{path}/process_settings.json") as f:
    process = json.load(f)
process = {k: pd.Series(v) for k, v in process.items()}
t = pd.concat(process)