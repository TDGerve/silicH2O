import pathlib
import shutil
import sys

import PyInstaller.__main__

r"""
File "C:\Users\u0123694\miniforge3\envs\py310\lib\site-packages\win32ctypes\pywin32\pywintypes.py", line 37, in pywin32error
    raise error(exception.winerror, exception.function, exception.strerror)
win32ctypes.pywin32.pywintypes.error: (110, 'EndUpdateResource', 'The system cannot open the device or file specified')


https://stackoverflow.com/questions/57180580/pyinstaller-win32ctypes-pywin32-pywintypes-error-1920-loadlibraryexw-syst

https://stackoverflow.com/questions/57932432/pyinstaller-win32ctypes-pywin32-pywintypes-error-2-loadlibraryexw-the-sys

https://stackoverflow.com/questions/41870727/pyinstaller-adding-data-files


"""

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


dist = pathlib.Path(__file__).parents[0] / "dist"

data_folders = {
    "temp": temp_folder,
    "calibration": calibration_folder,
    "configuration": config_folder,
    "theme": theme_folder,
}

for name, folder in data_folders.items():
    destination = dist / name
    shutil.copytree(
        folder, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.py")
    )
