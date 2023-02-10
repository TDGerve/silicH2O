from typing import Dict, Tuple

import blinker as bl
import pandas as pd
import ramCOH as ram

on_display_message = bl.signal("display message")


class Interference_processor:
    def __init__(self, sample: ram.RamanProcessing, settings: pd.Series):

        self.sample = sample
        self.settings = settings

    def apply_settings(self, **kwargs) -> None:
        names = ("smoothing", "spectrum", "use")
        for name in names:
            val = kwargs.pop(name, None)
            if val is None:
                continue
            self.settings[name] = val

        for ID, new_value in kwargs.items():
            location = ["left", "right"][int(ID[-2:]) % 2]
            self.settings[f"boundary_{location}"] = new_value

    def get_settings(self) -> Dict:
        boundary_left, boundary_right = self.get_minimisation_region()
        return {
            "bir_00": boundary_left,
            "bir_01": boundary_right,
            "smoothing": self.settings["smoothing"],
            "spectrum": self.settings["spectrum"],
            "use": self.settings["use"],
        }

    def get_minimisation_region(self) -> Tuple[float, float]:
        return tuple(self.settings.loc[["boundary_left", "boundary_right"]])

    def get_interference_spectrum(self, interference: ram.RamanProcessing) -> None:

        spectrum_name = self.settings["spectrum"]

        spectrum = interference.data.signal.get(spectrum_name)
        if spectrum is None:
            return None

        return self.sample.signal.interpolate_spectrum(
            old_x=interference.data.signal.x,
            old_y=spectrum,
        )

    def calculate(self, interference: ram.RamanProcessing) -> bool:

        interference = self.get_interference_spectrum(interference)
        if interference is None:
            on_display_message.send(message="interference not found", duration=5)
            return False

        settings = self.get_subtraction_parameters()
        settings["interval"] = [settings.pop(key) for key in ("bir_00", "bir_01")]

        self.data.subtract_interference(interference=interference, **settings)
        return True
