import sys
from typing import Protocol, Tuple, Union


class Screen(Protocol):
    resolution: Tuple[int, int]
    scaling: Union[int, float]
    dpi: Union[int, float]
    test: int


class Computer_screen:
    def __init__(
        self,
        resolution: Tuple[int, int],
        dpi: Union[int, float],
    ):
        self.scaling = self.get_scaling()
        self._resolution_x: int = resolution[0] * self.scaling
        self._resolution_y: int = resolution[1] * self.scaling
        self.dpi = dpi * self.scaling

    @property
    def resolution(self) -> Tuple[int, int]:
        return self._resolution_x, self._resolution_y

    def get_scaling(self):
        if "win32" in sys.platform:
            scaling = 1

            # For windows
            import ctypes

            from PySide2 import QtGui

            # Set dpi scaling awareness
            try:  # Windows 8.1 and later
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception as e:
                pass
            try:  # Before Windows 8.1
                ctypes.windll.user32.SetProcessDPIAware()
            except:  # Windows 8 or before
                pass

            # Get scaling factor
            screen = QtGui.QGuiApplication().primaryScreen()
            scaling = screen.devicePixelRatio()

        else:
            # dpi scaling awareness does not seem to be available for other platforms
            scaling = 1

        return scaling
