from contextlib import redirect_stdout
from typing import Dict, Optional

import blinker as bl

from .. import app_configuration
from ..interface.GUIS import Gui
from ..spectral_processing import Calibration_processor, Database_controller


class Calculation_listener:

    on_sample_change = bl.signal("sample change")
    on_settings_change = bl.signal("settings change")

    on_Ctrl_c = bl.signal("copy birs")
    on_Ctrl_v = bl.signal("paste birs")
    on_Ctrl_z = bl.signal("ctrl+z")

    on_plot_change = bl.signal("refresh plot")
    on_interference_added = bl.signal("show interference")
    on_switch_tab = bl.signal("switch tab")
    on_reset_sample = bl.signal("reset sample")

    on_remove_interference = bl.signal("remove interference")
    on_deconvolve_interference = bl.signal("deconvolve interference")
    on_subtract_interference = bl.signal("subtract interference")

    on_set_processing = bl.signal("set processing")
    on_set_H2Oreference = bl.signal("set H2O reference")
    on_set_calibration_std = bl.signal("set calibration std")

    on_add_bir = bl.signal("add bir")
    on_delete_bir = bl.signal("delete bir")

    on_display_message = bl.signal("display message")
    on_update_gui_variables = bl.signal("update gui variables")

    on_change_bir_widgets = bl.signal("change bir widgets")

    copied_birs = None
    bir_amount: int = 10

    def __init__(
        self,
        database_controller: Database_controller,
        calibration: Calibration_processor,
        # gui: Gui,
    ):
        self.database_controller = database_controller
        self.calibration = calibration
        # self.gui = gui

        self.subscribe_to_signals()

    @property
    def current_tab(self):
        return app_configuration.gui["current_tab"]

    @property
    def sample(self):
        return self.database_controller.current_sample

    def calculate_sample(self, idx: Optional[int] = None):
        if idx is None:
            sample = self.sample
        else:
            sample = self.get_sample(idx)

        if self.current_tab == "interference":
            sample.calculate_interpolation(
                interference=(self.current_tab == "interference")
            )
            interference = sample.interference_sample
            if interference is not None:
                sample.interference_sample.calculate_baseline()
            return
        elif self.current_tab == "interpolation":
            sample.calculate_interpolation(
                interference=(self.current_tab == "interference")
            )
            return

        sample.calculate_baseline()
        sample.calculate_noise()
        sample.calculate_areas()

    def display_sample(self, *args):
        try:
            self.calculate_sample()
        except AttributeError:
            return

        settings = self.get_sample_settings()

        settings = settings[self.current_tab]

        new_bir_amount = self._calculate_bir_amount()
        self.update_bir_widgets(new_bir_amount)

        # self.gui.update_variables(**settings)
        self.on_update_gui_variables.send(**settings)
        self.update_gui_results()

        self.refresh_plots()

    def set_reference_H2O(self, *args, sample_index: int, H2O: float):
        # if sample_name is not None:
        #     sample_idx = self.database_controller.names.index(sample_name)
        #     sample = self.database_controller.get_sample(sample_idx)
        # else:
        #     sample = self.sample

        # sample._H2Oreference = H2O
        self.calibration.H2Oreference.iloc[sample_index] = H2O

    def set_calibration_std(self, *args, sample_index: int, use: bool):
        self.calibration.use.iloc[sample_index] = not self.calibration.use.iloc[
            sample_index
        ]

    def get_sample_settings(self):  # move #CH

        sample = self.sample

        baseline_settings = sample.get_baseline_settings()
        interpolation_settings = sample.get_interpolation_settings()
        interference_settings = sample.get_interference_settings()

        return {
            "baseline": {"baseline": baseline_settings},
            "interpolation": {"interpolation": interpolation_settings},
            "interference": interference_settings,
        }

    def copy_birs(self, *args, store=True, message="copied birs"):

        try:
            birs = self.get_sample_birs(type=self.current_tab)
            self.on_display_message.send(message=message)
        except AttributeError:
            return
        if store:
            self.copied_birs = birs
            return
        return birs

    def paste_birs(self, *args, birs: Optional[Dict] = None, message="pasted birs"):
        if (self.copied_birs is None) & (birs is None):
            return
        if birs is None:
            birs = self.copied_birs

        new_bir_amount = len(birs.keys()) - 1
        self.update_bir_widgets(new_bir_amount)

        self.update_from_plot(**{self.current_tab: birs})
        self.refresh_plots("settings change")
        self.on_display_message.send(message=message)

    def add_bir(self, *args, index: int):
        self.database_controller.change_birs(
            action="add", index=index, tab=self.current_tab
        )

        self.bir_amount_changed = True
        birs = self.copy_birs(store=False, message="")
        self.paste_birs(birs=birs, message="")

    def delete_bir(self, *args, index: int):
        self.database_controller.change_birs(
            action="remove", index=index, tab=self.current_tab
        )

        self.bir_amount_changed = True
        birs = self.copy_birs(store=False, message="")
        self.paste_birs(birs=birs, message="")

    def _calculate_bir_amount(self):

        settings = self.get_sample_birs(type=self.current_tab)
        number_of_birs = sum(["bir" in name for name in settings.keys()])
        return number_of_birs

    def get_sample_birs(self, type: str):  # move #CH
        sample = self.sample
        get_birs = {
            "baseline": sample.get_baseline_settings,
            "interpolation": sample.get_interpolation_settings,
            "interference": dict,
        }
        if sample.interference_sample is not None:
            get_birs["interference"] = sample.interference_sample.get_baseline_settings

        get_birs = get_birs[type]

        return get_birs()

    def update_bir_widgets(self, new_bir_amount: int):
        if new_bir_amount == self.bir_amount:
            return
        self.bir_amount = new_bir_amount
        self.on_change_bir_widgets.send(bir_amount=new_bir_amount // 2)

    def switch_sample(self, *args, index: int):

        self.database_controller.current_sample_index = index

        self.display_sample()

    def change_settings(self, *args, **kwargs):
        sample = self.sample

        func_dict = {
            "baseline": sample.set_baseline,
            "interpolation": sample.set_interpolation,
            "subtraction": sample.set_subtraction_parameters,
        }
        if sample.interference_sample is not None:
            func_dict["interference"] = sample.interference_sample.set_baseline
            func_dict[
                "deconvolution"
            ] = sample.interference_sample.set_deconvolution_settings

        for key, value in kwargs.items():
            func_dict[key](value)

        self.calculate_sample()

    def set_spectrum_processing(self, *args, type: str, value: bool):
        group = {
            "interpolated": "interpolation",
            "interference_corrected": "subtraction",
        }[type]

        if (type == "interference_corrected") & (
            self.sample.sample.signal.get(type) is None
        ):
            value = False
            # self.gui.update_variables(**{group: {"use": value}})
            self.on_update_gui_variables.send(**{group: {"use": value}})
        else:
            self.sample.set_spectrum_processing(types=[type], values=[value])

        self.change_settings(**{group: {"use": value}})

    def deconvolve_interference(self, *args):
        self.on_display_message.send(message="deconvolving ...", duration=None)
        # with redirect_stdout(Message_processor()):
        sample = self.current_sample
        interference = sample.interference_sample
        if interference is None:
            return

        interference.deconvolve()

        self.on_display_message.send(message="deconvolution complete!", duration=5)
        self.refresh_plots()

    def subtract_interference(self, *args, **kwargs):
        self.on_display_message.send(message="subtracting ...", duration=5)
        # with redirect_stdout(Message_processor()):
        if not self.sample.subtract_interference():
            return

        self.on_display_message.send(message="subtraction complete!", duration=5)
        self.refresh_plots()

    def remove_interference(self, *args):
        self.sample.remove_interference()
        self.display_sample()

    def update_gui_results(self):

        if self.current_tab != "baseline":
            return

        results = self.get_sample_results()
        self.on_update_gui_variables.send(**results)
        # self.gui.update_variables(**results)

    def get_sample_results(self):  # move #CH

        all_results = list(self.sample.results.values)
        names = ["silicate", "H2O", "H2OSi"]
        areas = {}
        for name, value in zip(names, all_results[:3]):
            if abs(value) < 20:
                value = round(value, 2)
            else:
                value = int(value)
            areas[name] = value

        names = ["noise", "Si_SNR", "H2O_SNR"]
        signal = {name: round(value, 2) for name, value in zip(names, all_results[3:])}

        return {"areas": areas, "signal": signal}

    def update_from_plot(self, *args, **settings):

        self.change_settings(**settings)
        self.on_update_gui_variables.send(**settings)
        # self.gui.update_variables(**settings)
        self.update_gui_results()

        # self.refresh_plots("settings change")

    def update_from_widgets(self, *args, **kwargs):

        self.change_settings(**kwargs)
        self.update_gui_results()

        self.refresh_plots("settings change")

    def refresh_plots(self, message: Optional[str] = None):
        try:
            plotdata = self.get_sample_plotdata()
        except AttributeError:
            return
        self.on_plot_change.send(message, **plotdata)

    def get_sample_plotdata(self) -> Dict:  # move #CH

        return self.sample.get_plotdata()

    def reset_sample(self, *args):

        self.database_controller.reset_sample(tab=self.current_tab)
        self.display_sample()

    def tab_change(self, *args):
        self.copied_birs = None
        self.bir_amount = self._calculate_bir_amount
        self.display_sample()

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample, sender="navigator")
        self.on_settings_change.connect(self.update_from_plot, sender="plot")
        self.on_settings_change.connect(self.update_from_widgets, sender="widget")

        self.on_interference_added.connect(self.display_sample)
        self.on_remove_interference.connect(self.remove_interference)
        self.on_deconvolve_interference.connect(self.deconvolve_interference)
        self.on_subtract_interference.connect(self.subtract_interference)

        self.on_set_processing.connect(self.set_spectrum_processing)

        self.on_add_bir.connect(self.add_bir)
        self.on_delete_bir.connect(self.delete_bir)

        self.on_Ctrl_c.connect(self.copy_birs)
        self.on_Ctrl_v.connect(self.paste_birs)
        self.on_Ctrl_z.connect(self.reset_sample)

        self.on_reset_sample.connect(self.reset_sample)
        self.on_switch_tab.connect(self.tab_change)
