import tkinter as tk

from typing import Dict

from .main_window import Main_window
from .plots import Plot


class App_interface:
    def __init__(
        self,
        title: str,
        variables: Dict[str, any],
        widgets: Dict[str, any],
        plots: Dict[str, Plot],
    ):
        # rRot
        self.main_window: tk.Tk = Main_window(title=title)
        # Root frames
        self.main_window.create_navigation_frame(variables, widgets)
        self.main_window.create_main_frame()
        # Tabs
        self.main_window.create_tabs(variables, widgets)

        # Menus
        self.main_window.create_menus()
