import pathlib
import shutil
import sys

"""
When bundeling for Mac, you will probably run into signing issues and the app not working on other people's computers
since apple doesn't trust the app.
To fix that run these commands (from the project folder) in a terminal

first delete all .DS_Store files in the app bundle
    find dist/silich2o.app -name .DS_Store -delete

OPTIONALLY create your own local certificate:
    Open Keychain Access

    Go to the menu at the top of the screen and select Keychain Access > Certificate Assistant > Create a Certificate

    In the window that appears change Certificate Type to Code Signing , select Create and note the name of the certificate

Create an entitlements.plist file in the main folder:
    see: https://haim.dev/posts/2020-08-08-python-macos-app/


then sign:

    with certificate and entitlements:
        codesign -s CERTIFICATE-NAME --timestamp --deep --force --entitlements entitlements.plist  ./dist/silicH2O.app

    -> this may take a few mins

    or without local certificate:
        codesign -s - --force --all-architectures --timestamp --deep --entitlements entitlements.plist dist/SilicH2O.app


The app should now run on your local computer and can be shared with others via usb


HOWEVER, When downloading SilicH2O from GitHub or elsewhere on the internet, MacOS puts all files in quarantine and the app will not run.
Remove all files from the bundle from quarantine with:
    sudo xattr -r -d com.apple.quarantine ./silicH2O.app

note that you need admin rights to do this.
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
