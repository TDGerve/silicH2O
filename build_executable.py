import pathlib
import shutil
import sys

"""
When bundeling for Mac, pyinstaller will probably finish with a warning that the app could not be signed.
To fix that run these commands (from the project folder) in a terminal

first delete all .DS_Store files in the app bundle
    find dist/silich2o.app -name .DS_Store -delete

then sign:
    codesign -s - --force --all-architectures --timestamp --deep dist/SilicH2O.app
"""

import PyInstaller.__main__

if "win32" in sys.platform:
    sep = ";"
else:
    # unix
    sep = ":"

name = "SilicH2O"
theme_folder = pathlib.Path(__file__).parents[0] / "src/theme"

# temp_folder = pathlib.Path(__file__).parents[0] / "src/temp"
calibration_folder = pathlib.Path(__file__).parents[0] / "src/calibration/"
config_folder = pathlib.Path(__file__).parents[0] / "src/app_configuration"
examples_folder = pathlib.Path(__file__).parents[0] / "examples"


dist = pathlib.Path(__file__).parents[0] / "dist"

data_folders = {
    # "temp": temp_folder,
    "calibration": calibration_folder,
    "configuration": config_folder,
    # "theme": theme_folder,
    "examples": examples_folder,
}


if __name__ == "__main__":
    PyInstaller.__main__.run(
        [
            f"--name={name}",
            "--onedir",
            "--clean",
            "--noconfirm",
            f"--add-data={theme_folder}{sep}theme",
            "--exclude-module=.git",
            "--log-level=WARN",
            "--debug=all",
            "--noconsole",
            # "--windowed",
            "run_silicH2O.py",
        ]
    )

    for name, folder in data_folders.items():
        destination = dist / name
        shutil.copytree(
            folder,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.py"),
        )
