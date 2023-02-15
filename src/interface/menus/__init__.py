import tkinter as tk

from .calibration_menu import Calibration_menu
from .io_menu import IO_menu
from .settings_menu import Settings_menu


class Menubar:
    def __init__(self, menubar):

        IO_menu(parent=menubar)
        Settings_menu(parent=menubar)
        Calibration_menu(parent=menubar)
