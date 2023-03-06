import os
import pathlib
import sys

import blinker as bl

from ..spectral_processing import Calibration_processor, Database_controller

if getattr(sys, "frozen", False):
    EXE_LOCATION = pathlib.Path(os.path.dirname(sys.executable))  # cx_Freeze frozen
    calibration_folder = EXE_LOCATION.parents[0] / "calibration"

else:

    calibration_folder = pathlib.Path(__file__).parents[1] / "calibration"


class Calibration_listener:

    on_import_calibration_project = bl.signal("project calibration")
    on_import_calibration_file = bl.signal("import calibration file")

    on_reset_calibration_standards = bl.signal("reset calibration standards")

    on_set_H2Oreference = bl.signal("set H2O reference")
    on_use_calibration_std = bl.signal("use calibration std")
    on_get_calibration_info = bl.signal("get calibration info")
    on_use_calibration = bl.signal("use calibration")

    on_refresh_calibration_data = bl.signal("refresh calibration data")
    on_update_gui_variables = bl.signal("update gui variables")
    on_calibration_plot_change = bl.signal("refresh calibration plot")

    on_plot_change = bl.signal("refresh plot")

    on_display_message = bl.signal("display message")

    def __init__(
        self,
        database_controller: Database_controller,
        calibration: Calibration_processor,
    ):
        self.database_controller = database_controller
        self.calibration = calibration
        # self.gui = gui

        self.subscribe_to_signals()

    def refresh_calibration_data(self, *args):
        if not self.calibration._database_controller:
            return

        self.database_controller.save_results()

    def calibrate_with_project(self, *args, update_gui=True):
        self.calibration.calibrate_with_project(
            database_controller=self.database_controller
        )
        if update_gui:
            self.reset_calibration_gui()

        self.calibrate(update_gui=update_gui)
        self.use_calibration(use=False)

        self.on_display_message.send(message="Project imported as calibration")

    def calibrate_with_file(self, *args, update_gui=True, **kwargs):

        self.calibration.import_calibration_data(**kwargs)

        if update_gui:
            self.reset_calibration_gui()

        self.calibrate(update_gui=update_gui)
        self.use_calibration(use=True)

        self.on_display_message.send(message="Calibration imported from file")

    def reset_calibration_gui(self, *args):
        sample_amount = len(self.calibration._H2OSi)

        self.on_reset_calibration_standards.send(sample_amount=sample_amount)

    def send_calibration_info(self, *args):

        self.reset_calibration_gui()

        self.send_sample_info()
        self.send_calibration_statistics()

    def send_sample_info(self):

        sample_info = self.calibration.get_sampleinfo_gui()
        self.on_update_gui_variables.send(calibration=sample_info)

    def send_calibration_statistics(self):

        calibration_params = self.calibration.get_calibration_parameters_gui()
        self.on_update_gui_variables.send(calibration_statistics=calibration_params)

    def set_reference_H2O(self, *args, sample_index: int, H2O: float):

        self.calibration.set_H2Oreference(sample_index=sample_index, H2O=H2O)
        sample_name = self.calibration.names[sample_index]
        self.database_controller.settings.loc[
            sample_name, ("calibration", "H2Oreference")
        ] = H2O

        if self.calibration.use.iloc[sample_index]:
            self.calibrate()

    def use_calibration_std(self, *args, sample_index: int):

        self.calibration.use.iloc[sample_index] = not self.calibration.use.iloc[
            sample_index
        ]
        self.calibrate()

    def calibrate(self, update_gui=True):

        self.calibration.calibrate()

        if not update_gui:
            return

        self.send_sample_info()
        self.send_calibration_statistics()

        self.refresh_plot()

    def use_calibration(self, *args, use: bool):
        if not self.calibration.name:
            self.on_update_gui_variables.send(
                calibration_statistics={"use_calibration": False}
            )
            self.on_display_message.send(message="Save calibration first!")

        if use:
            self.database_controller.set_calibration(
                name=self.calibration.name, calibration=self.calibration._calculate_H2O
            )
        else:
            self.database_controller.reset_calibration()

        self.calibration.use_calibration = use

    def refresh_plot(self, *args):

        plotdata = self.calibration.get_plotdata()
        self.on_plot_change.send(plot="calibration", plotdata=plotdata)

    # def save_project_as_calibration(self, *args, name: str):

    #     self.on_display_message.send(message="saving calibration...", duration=None)

    #     filepath = calibration_folder / f"{name}.ch2o"

    #     self.save_project_data(filepath=filepath, name=name)
    #     self.on_display_message.send(message="saved calibration")

    #     self.database_controller.set_project(filepath=filepath)

    # def _make_calibration_folders(self, name: str) -> Dict:

    #     paths = {"project": calibration_folder / "temp" / name}
    #     paths["data"] = paths["project"] / "data"
    #     paths["processed"] = paths["data"] / "processed"
    #     paths["interference"] = paths["data"] / "interference"

    #     for dir in paths.values():
    #         if dir.is_dir():
    #             continue
    #         dir.mkdir(parents=True, exist_ok=True)

    #     return paths

    # def save_project_data(self, filepath: pathlib.Path, name: str):

    #     paths = self._make_project_folders(name)

    #     has_interference = False

    #     pd.concat(
    #         [
    #             self.calibration._H2OSi,
    #             self.calibration._H2Oreference,
    #             self.calibration.use,
    #         ],
    #         axis=1,
    #     )

    #     for processor in self.database_controller.spectra:
    #         # data = np.column_stack([sample.sample.signal.x, sample.sample.signal.raw])
    #         file = paths["data"] / f"{processor.name}"
    #         if not file.is_file():
    #             np.savez(
    #                 file,
    #                 x=processor.sample.signal.get("x"),
    #                 y=processor.sample.signal.get("raw"),
    #             )

    #         file_processed = paths["processed"] / f"{processor.name}"
    #         names = ("interference_corrected", "interpolated")
    #         data = [processor.sample.signal.get(name) for name in names]
    #         processed = {
    #             name: vals for name, vals in zip(names, data) if vals is not None
    #         }

    #         if len(processed) > 0:
    #             np.savez(file_processed, **processed)

    #         if not processor.interference_sample:
    #             continue

    #         has_interference = True
    #         file_interference = paths["interference"] / f"{processor.name}"
    #         np.savez(
    #             file_interference,
    #             x=processor.interference_sample.sample.signal.get("x"),
    #             y=processor.interference_sample.sample.signal.get("raw"),
    #         )

    #     if has_interference:
    #         interference_settings = (
    #             self.database_controller.get_all_interference_settings()
    #         )
    #         for name, f in interference_settings.items():
    #             f.to_parquet(paths["interference"] / f"{name}.parquet")

    #     settings = self.database_controller.get_all_settings()

    #     for name, f in settings.items():
    #         f.to_parquet(paths["project"] / f"{name}.parquet")

    #     with tarfile.open(filepath, mode="w") as tar:
    #         tar.add(paths["project"], arcname="")

    def subscribe_to_signals(self):
        self.on_import_calibration_project.connect(self.calibrate_with_project)
        self.on_import_calibration_file.connect(self.calibrate_with_file)

        self.on_get_calibration_info.connect(self.send_calibration_info)
        self.on_set_H2Oreference.connect(self.set_reference_H2O)

        self.on_use_calibration_std.connect(self.use_calibration_std)
        self.on_use_calibration.connect(self.use_calibration)

        self.on_calibration_plot_change.connect(self.refresh_plot)
        self.on_refresh_calibration_data.connect(self.refresh_calibration_data)
