from .Interpolation import Interpolation_processor


class Interference:
    def __init__(self, glass, interference):
        # self.interference = Sample_processor()
        ...

    def apply_settings(self):
        ...

    def get_settings(self):
        ...

    def set_subtraction_parameters(self, kwargs: Dict):
        names = ("smoothing", "spectrum", "use")
        self._set_parameters(group="interference", parameters=kwargs, names=names)

        for ID, new_value in kwargs.items():
            location = ["left", "right"][int(ID[-2:]) % 2]
            self.settings[("interference", f"boundary_{location}")] = new_value

    def get_subtraction_region(self):
        return self.settings.loc[
            (["interference"], ["boundary_left", "boundary_right"])
        ].values

    def get_subtraction_parameters(self):
        boundary_left, boundary_right = self.get_subtraction_region()
        return {
            "bir_00": boundary_left,
            "bir_01": boundary_right,
            "smoothing": self.settings[("interference", "smoothing")],
            "spectrum": self.settings[("interference", "spectrum")],
            "use": self.settings[("interference", "use")],
        }

    def get_interference_spectrum(self):

        spectrum_name = self.settings[("interference", "spectrum")]
        interference = self.interference

        spectrum = interference.data.signal.get(spectrum_name)
        if spectrum is None:
            return None

        return self.data.signal.interpolate_spectrum(
            old_x=interference.data.signal.x,
            old_y=spectrum,
        )

    def subtract_interference(self) -> bool:

        interference = self.get_interference_spectrum()
        if interference is None:
            on_display_message.send(message="interference not found", duration=5)
            return False

        settings = self.get_subtraction_parameters()
        settings["interval"] = [settings.pop(key) for key in ("bir_00", "bir_01")]

        self.data.subtract_interference(interference=interference, **settings)
        return True
