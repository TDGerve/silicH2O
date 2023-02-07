from typing import Dict, List, Optional

import blinker as bl

from .. import app_configuration
from ..interface import Gui


class Gui_listener:

    on_mouse_movement = bl.signal("mouse moved")
    on_display_message = bl.signal("display message")
    on_change_bir_widgets = bl.signal("change bir widgets")

    def __init__(self, gui: Gui):

        self.gui = gui

        self.subscribe_to_signals()

    def send_plot_coordinates(self, *args, **kwargs):
        # print(kwargs)
        self.gui.update_variables(**kwargs)

    def display_message(self, *args, message: str, duration: Optional[int] = 2):
        # clear current message
        self.gui.update_variables(infobar={"info": ""})
        # construct new message
        message = f"{message:<50}"
        kwargs = {"infobar": {"info": message}}
        self.gui.update_variables(**kwargs)
        if duration is None:
            return
        self.gui.window.after(
            int(duration * 1e3), lambda: self.gui.update_variables(infobar={"info": ""})
        )

    def update_bir_widgets(self, *args, bir_amount):
        self.gui.window.reset_baseline_widgets(bir_amount=bir_amount)

    def subscribe_to_signals(self):

        self.on_mouse_movement.connect(self.send_plot_coordinates)
        self.on_display_message.connect(self.display_message)
        self.on_change_bir_widgets.connect(self.update_bir_widgets)
