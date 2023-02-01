import blinker as bl

"""
from:
https://stackoverflow.com/questions/71024919/how-to-capture-prints-in-real-time-from-function
"""


class Message_processor:
    def __init__(self):
        self.buf = ""
        self.on_display_message = bl.signal("display message")

    def write(self, buffer):
        # emit on each return
        while buffer:
            try:
                newline_index = buffer.index("\r")
            except ValueError:
                # no return, buffer for next call
                self.buf += buffer
                break
            # get data to next return and combine with any buffered data
            data = self.buf + buffer[: newline_index + 1]
            self.buf = ""
            buffer = buffer[newline_index + 1 :]
            # post event
            self.on_display_message.send(message=data)
