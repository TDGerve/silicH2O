import platform
import tkinter as tk
from tkinter import ttk

# from https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01


class ScrollFrame(tk.Frame):
    def __init__(self, parent, *args, width, background_color, **kwargs):

        super().__init__(parent, *args, **kwargs)  # create a frame (self)

        self.headers = tk.Frame(self)

        self.canvas = tk.Canvas(
            self,
            background=background_color,
            borderwidth=0,
            width=width,
            highlightthickness=0,
        )  # place canvas on self

        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.canvas.yview
        )  # place a scrollbar on self
        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )  # attach scrollbar action to scroll of canvas

        self.headers.grid(row=0, column=0, columnspan=2, sticky="nesw")
        self.canvas.grid(row=1, column=0, sticky="nesw")
        self.scrollbar.grid(row=1, column=1, sticky="nes")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw",  # add view port frame to canvas
            tags="self.inner_frame",
        )

        self.inner_frame.bind("<Configure>", self.set_initial_dimensions)

        self.canvas.bind(
            "<Configure>", self.onCanvasConfigure
        )  # bind an event whenever the size of the canvas frame changes.

        self.inner_frame.bind(
            "<Enter>", self.onEnter
        )  # bind wheel events when the cursor enters the control
        self.inner_frame.bind(
            "<Leave>", self.onLeave
        )  # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(
            None
        )  # perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def set_initial_dimensions(self, event):
        height = event.height
        width = event.width
        self.canvas.config(height=height, width=width)
        self.inner_frame.unbind("<Configure>")
        self.inner_frame.bind(
            "<Configure>", self.onFrameConfigure
        )  # bind an event whenever the size of the viewPort frame changes.

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )  # whenever the size of the frame changes, alter the scroll region respectively.
        self.after_idle(self.set_header_widths)

    def onCanvasConfigure(self, event):
        """Reset the inner frame to fit the canvas when required"""
        canvas_width = event.width
        self.canvas.itemconfig(
            self.canvas_window, width=canvas_width
        )  # whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        if platform.system() == "Windows":
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == "Darwin":
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        if platform.system() == "Linux":
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        if platform.system() == "Linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def get_column_widths(self):
        widths = []
        for column in range(self.inner_frame.grid_size()[0]):
            widths.append(self.inner_frame.grid_bbox(column, 0)[2])
        return widths

    def set_header_widths(self):
        column_widths = self.get_column_widths()
        for i, width in enumerate(column_widths):
            self.headers.columnconfigure(i, minsize=width)
