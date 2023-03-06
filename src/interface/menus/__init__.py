import tkinter as tk

from .calibration_menu import Calibration_menu
from .io_menu import IO_menu
from .settings_menu import Settings_menu


class Menubar(tk.Menu):
    def __init__(self, parent, name):

        super().__init__(parent, name=name)

        IO_menu(parent=self)
        Settings_menu(parent=self)
        Calibration_menu(parent=self)
