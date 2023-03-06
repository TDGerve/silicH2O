from typing import Optional

import blinker as bl

from ..interface import App_interface, GUI_state


class Gui_listener:

    on_mouse_movement = bl.signal("mouse moved")
    on_display_message = bl.signal("display message")
    on_change_title = bl.signal("change_title")

    on_change_bir_widgets = bl.signal("change bir widgets")
    on_reset_calibration_standards = bl.signal("reset calibration standards")

    on_update_gui_variables = bl.signal("update gui variables")
    on_clear_gui_variables = bl.signal("clear variables")

    on_activate_widgets = bl.signal("activate_widgets")

    on_calibration_window = bl.signal("calibration window")
    on_get_calibration_info = bl.signal("get calibration info")

    def __init__(self, gui: App_interface):

        self.gui = gui

        self.subscribe_to_signals()

    def change_title(self, *args, title: Optional[str] = None):
        self.gui.change_title(title=title)

    def activate_widgets(self, *args):
        if self.gui.state != GUI_state.DISABLED:
            return
        self.gui.activate_widgets()
        self.gui.set_state(GUI_state.ACTIVE)

    # def send_plot_coordinates(self, *args, **kwargs):
    #     # print(kwargs)
    #     self.gui.update_variables(**kwargs)

    def update_variables(self, *args, **kwargs):
        self.gui.update_variables(**kwargs)

    def clear_variables(self, *args):
        self.gui.clear_variables()

    def display_message(self, *args, message: str, duration: Optional[int] = 2):
        # clear current message
        self.gui.update_variables(infobar={"info": ""})
        # construct new message
        message = f"{message:<50}"
        kwargs = {"infobar": {"info": message}}
        self.gui.update_variables(**kwargs)
        if duration is None:
            return
        self.gui.main_window.after(
            int(duration * 1e3), lambda: self.gui.update_variables(infobar={"info": ""})
        )

    def update_bir_widgets(self, *args, bir_amount):
        self.gui.reset_baseline_widgets(bir_amount=bir_amount)

    def reset_calibration_standards(self, *args, sample_amount: int):
        self.gui.reset_calibration_widgets(sample_amount=sample_amount)

    def calibration_window_popup(self, *args):
        self.gui.calibration_window_popup()
        # self.on_get_calibration_info.send()

    def subscribe_to_signals(self):

        self.on_mouse_movement.connect(self.update_variables)
        self.on_display_message.connect(self.display_message)

        self.on_change_bir_widgets.connect(self.update_bir_widgets)
        self.on_reset_calibration_standards.connect(self.reset_calibration_standards)

        self.on_update_gui_variables.connect(self.update_variables)
        self.on_clear_gui_variables.connect(self.clear_variables)

        self.on_activate_widgets.connect(self.activate_widgets)

        self.on_calibration_window.connect(self.calibration_window_popup)
        self.on_change_title.connect(self.change_title)
