from typing import Protocol
from enum import Enum, auto


class Gui(Protocol):
    def update_variables(self):
        ...

    def activate_widgets(self):
        ...


class GUI_state(Enum):
    DISABLED = auto()
    ACTIVE = auto()
