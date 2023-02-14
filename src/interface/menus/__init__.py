import tkinter as tk

from .io_menu import *
from .settings_menu import *


class Menubar:
    def __init__(self, menubar):

        io_menu(parent=menubar)
        settings_menu(parent=menubar)
