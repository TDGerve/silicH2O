from enum import Enum, auto
from typing import Protocol


class App(Protocol):
    def set_state(self):
        ...

    def update_variables(self):
        ...

    def activate_widgets(self):
        ...

    def run(self):
        ...


class App_state(Enum):
    DISABLED = auto()
    ACTIVE = auto()
