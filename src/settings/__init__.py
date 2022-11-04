import json

with open(f"{__path__[0]}/birs.json") as f:
    birs = json.load(f)

with open(f"{__path__[0]}/process_settings.json") as f:
    process = json.load(f)

with open(f"{__path__[0]}/gui_settings.json") as f:
    gui = json.load(f)
