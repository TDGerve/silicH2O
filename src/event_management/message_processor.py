import sys

import blinker as bl

"""
from:
https://stackoverflow.com/questions/71024919/how-to-capture-prints-in-real-time-from-function
"""
real_stdout_for_test = sys.stdout


class Message_processor:

    on_display_message = bl.signal("display message")

    def __init__(self):
        self.buf = ""

    def write(self, buf):
        # emit on each newline
        while buf:
            try:
                newline_index = buf.index("\n")
            except ValueError:
                # no newline, buffer for next call
                self.buf += buf
                break
            # get data to next newline and combine with any buffered data
            data = self.buf + buf[:newline_index]
            self.buf = ""
            buf = buf[newline_index + 1 :]
            real_stdout_for_test.write("fiddled with " + data)
            self.on_display_message.send(message=data, duration=None)
