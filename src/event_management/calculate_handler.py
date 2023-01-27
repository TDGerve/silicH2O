import blinker as bl

from .. import app_configuration
from ..interface import Gui
from ..spectral_processing import Database_controller


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

    on_add_bir = bl.signal("add bir")
    on_delete_bir = bl.signal("delete bir")

    on_display_message = bl.signal("display message")
    on_change_bir_widgets = bl.signal("change bir widgets")

    copied_birs = None
    bir_amount: int = 10

    def __init__(self, database_controller: Database_controller, gui: Gui):
        self.database_controller = database_controller
        self.gui = gui

        self.subscribe_to_signals()

    def display_sample(self, message: str):
        try:
            self.database_controller.calculate_sample()
        except AttributeError:
            return

        settings = self.database_controller.get_sample_settings()

        current_tab = app_configuration.gui["current_tab"]
        settings = settings[current_tab]

        new_bir_amount = self._calculate_bir_amount()
        self.update_bir_widgets(new_bir_amount)

        self.gui.update_variables(**{current_tab: settings})
        self.update_gui_results()

        self.refresh_plots(message)

    def copy_birs(self, *args, message="copied birs"):
        current_tab = app_configuration.gui["current_tab"]
        try:
            self.copied_birs = self.database_controller.get_sample_settings()[
                current_tab
            ]
            self.on_display_message.send(message=message)
        except AttributeError:
            pass

    def paste_birs(self, *args, message="pasted birs"):
        if self.copied_birs is None:
            pass

        new_bir_amount = len(self.copied_birs.keys()) - 1
        self.update_bir_widgets(new_bir_amount)

        current_tab = app_configuration.gui["current_tab"]

        self.update_from_plot(**{current_tab: self.copied_birs})
        self.refresh_plots("settings change")
        self.on_display_message.send(message=message)

    def add_bir(self, *args, index: int):
        self.database_controller.change_birs(action="add", index=index)

        self.bir_amount_changed = True
        self.copy_birs(message="")
        self.paste_birs(message="")

    def delete_bir(self, *args, index: int):
        self.database_controller.change_birs(action="remove", index=index)

        self.bir_amount_changed = True
        self.copy_birs(message="")
        self.paste_birs(message="")

    def _calculate_bir_amount(self):
        current_tab = app_configuration.gui["current_tab"]
        settings = self.database_controller.get_sample_settings()[current_tab]
        number_of_birs = sum(["bir" in name for name in settings.keys()])
        return number_of_birs

    def update_bir_widgets(self, new_bir_amount: int):
        if new_bir_amount == self.bir_amount:
            return
        self.bir_amount = new_bir_amount
        self.on_change_bir_widgets.send(bir_amount=new_bir_amount // 2)

    def switch_sample(self, *args, index: int):

        self.database_controller.current_sample_index = index

        self.display_sample("sample change")

    def change_settings(self, *args, **kwargs):

        self.database_controller.change_sample_settings(**kwargs)
        self.database_controller.calculate_sample()

    def update_gui_results(self):

        results = self.database_controller.get_sample_results()
        self.gui.update_variables(**results)

    def update_from_plot(self, *args, **settings):

        self.change_settings(**settings)
        self.gui.update_variables(**settings)
        self.update_gui_results()

        # self.refresh_plots("settings change")

    def update_from_widgets(self, *args, **kwargs):

        self.change_settings(**kwargs)
        self.update_gui_results()

        self.refresh_plots("settings change")

    def refresh_plots(self, message: str):
        try:
            plot_data = self.database_controller.get_sample_plotdata()
        except AttributeError:
            return
        self.on_plot_change.send(message, **plot_data)

    def reset_sample(self, *args):

        self.database_controller.reset_sample()
        self.display_sample("sample reset")

    def tab_change(self, *args):
        self.copied_birs = None
        self.bir_amount = self._calculate_bir_amount
        self.display_sample(*args)

    def subscribe_to_signals(self):
        self.on_sample_change.connect(self.switch_sample, sender="navigator")
        self.on_settings_change.connect(self.update_from_plot, sender="plot")
        self.on_settings_change.connect(self.update_from_widgets, sender="widget")
        self.on_interference_added.connect(self.display_sample)

        self.on_add_bir.connect(self.add_bir)
        self.on_delete_bir.connect(self.delete_bir)

        self.on_Ctrl_c.connect(self.copy_birs)
        self.on_Ctrl_v.connect(self.paste_birs)
        self.on_Ctrl_z.connect(self.reset_sample)

        self.on_reset_sample.connect(self.reset_sample)
        self.on_switch_tab.connect(self.tab_change)
