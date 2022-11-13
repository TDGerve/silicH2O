from enum import Enum, auto
from typing import Protocol


class App(Protocol):
    def run(self):
        ...
