import pathlib
import shutil
import sys

import PyInstaller.__main__

name = "SilicH2O"
theme_folder = pathlib.Path(__file__).parents[0] / "src/theme"


if "win" in sys.platform:
    sep = ";"
else:
    sep = ":"

if __name__ == "__main__":
    PyInstaller.__main__.run(
        [
            f"--name={name}",
            "--onedir",
            "--clean",
            f"--add-data={theme_folder}{sep}theme",
            "--exclude-module=.git",
            "--log-level=WARN",
            "--noconsole",
            "run_silicH2O.py",
        ]
    )

temp_folder = pathlib.Path(__file__).parents[0] / "src/temp"
calibration_folder = pathlib.Path(__file__).parents[0] / "src/calibration/"
config_folder = pathlib.Path(__file__).parents[0] / "src/app_configuration"
examples_folder = pathlib.Path(__file__).parents[0] / "examples"


dist = pathlib.Path(__file__).parents[0] / "dist"

data_folders = {
    "temp": temp_folder,
    "calibration": calibration_folder,
    "configuration": config_folder,
    "theme": theme_folder,
    "examples": examples_folder,
}

for name, folder in data_folders.items():
    destination = dist / name
    shutil.copytree(
        folder, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.py")
    )
