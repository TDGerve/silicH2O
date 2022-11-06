from enum import Enum, auto
from typing import List
import blinker as bl


class status(Enum):
    SAMPLE_CHANGE = auto()
    SAMPLE_ADDED = auto()
    SETTINGS_CHANGE = auto()
    UNCHANGED = auto()


class sample_info:

    state = status.UNCHANGED
    idx: int = None
    files: List[str] = None

    signal = bl.signal("status_change")

    @classmethod
    def set_state(cls, state: status):
        if state == status.UNCHANGED:
            return
        cls.state = state

        status_str = str(state.name)
        cls.signal.send(status_str)

    @classmethod
    def set_idx(cls, idx: int):
        if cls.idx == idx:
            return
        cls.idx = idx
        cls.set_state(status.SAMPLE_CHANGE)

    @classmethod
    def set_files(cls, files: List[str]):
        if cls.files == files:
            return
        cls.files += files
        cls.set_state(status.SAMPLE_ADDED)
