from tkinter import ttk
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from toolbar_vertical import vertical_toolbar


class interpolation(ttk.Frame):
    # plot x limits
    xmin = 250
    xmax = 1400
    interpolation_colors = ["grey", "darkgreen"]

    # Initiate variables
    raw_spectrum = None
    interpolated = None
    interpolation_region = None
    # Object to store lines to be dragged
    _dragging_line = None
    # Store the id of the interpolation boundary being dragged, 0 for left, 1 for right
    _dragging_line_id = None

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.sample_info = None

        font = app.font
        fontsize = app.fontsize
        self.colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        # Create frames
        plot_frame = ttk.Frame(self)
        toolbar_frame = ttk.Frame(self)
        settings_frame = ttk.Frame(self)
        # Put frames on a grid
        plot_frame.grid(row=0, column=0, sticky=("nesw"))
        toolbar_frame.grid(row=0, column=1, sticky=("nesw"))
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=("nesw"))
        # Configure resizing
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        settings_frame.rowconfigure(2, weight=1)
        settings_frame.columnconfigure(3, weight=1)

        # Create plot canvas
        self.fig, self.ax = plt.subplots(
            figsize=(5.8, 4.5), constrained_layout=True, dpi=80
        )
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))
        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, toolbar_frame)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky="ne")
        self.fig.canvas.draw()
        # Plot axes
        self.ax.set_xlabel(" ")
        self.ax.set_ylabel("Intensity (arbitr. units)")
        self.ax.set_yticks([])
        self.ax.set_xlim(self.xmin, self.xmax)
        self.fig.patch.set_facecolor(app.bgClr_plt)

        # Widgets with interpolation settings
        # Interpolation checkbox
        self.itp_var = tk.BooleanVar()
        checkbox_label = ttk.Label(
            settings_frame, text="Interpolate", font=(font, fontsize)
        )
        self.checkbox = ttk.Checkbutton(
            settings_frame,
            variable=self.itp_var,
            onvalue=True,
            offvalue=False,
            command=self.interpolate_check,
            state=tk.DISABLED,
        )
        self.checkbox.grid(row=1, column=0, sticky=("nesw"))
        checkbox_label.grid(row=0, column=0, sticky=("esw"))

        smoothing_label = ttk.Label(
            settings_frame, text="Interpolation smoothing", font=(font, fontsize)
        )
        self.smoothing_var = tk.StringVar()
        self.smoothing_var.set(1)
        self.smoothing_spinbox = ttk.Spinbox(
            settings_frame,
            from_=0.1,
            to=10,
            increment=0.1,
            validate="focus",
            validatecommand=(self.register(self.validate_smoothing), "%P"),
            invalidcommand=(self.register(self.invalid_smoothing), "%P"),
            textvariable=self.smoothing_var,
            takefocus=1,
            width=5,
            font=(font, fontsize, "italic"),
            state=tk.DISABLED,
        )
        self.smoothing_set = ttk.Button(
            settings_frame,
            text="Set",
            command=self.set_interpolation_smoothing,
            state=tk.DISABLED,
        )
        self.interpolation_reset = ttk.Button(
            settings_frame,
            text="Reset",
            command=self.reset_interpolation,
            state=tk.DISABLED,
        )
        self.interpolation_save = ttk.Button(
            settings_frame,
            text="Save",
            command=self.save_interpolation,
            state=tk.DISABLED,
        )
        smoothing_label.grid(row=0, column=1, columnspan=2, sticky=("s"))
        self.smoothing_spinbox.grid(row=1, column=1, sticky=("nsw"))
        self.smoothing_set.grid(row=1, column=2, sticky=("n"))
        self.interpolation_reset.grid(row=0, column=3, sticky=("e"))
        self.interpolation_save.grid(row=1, column=3, sticky=("ne"))

        for child in settings_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def initiate_plot(self):
        """ """
        # Enable all widgets
        for widget in [
            self.checkbox,
            self.smoothing_spinbox,
            self.smoothing_set,
            self.interpolation_reset,
            self.interpolation_save,
        ]:
            widget.configure(state=tk.NORMAL)

        self.sample_info = self.app.current_sample
        sample = self.sample_info.sample
        self.old_spectrum = sample._spectrumSelect
        self.smoothing_var.set(self.sample_info.interpolation_smoothing)
        self.itp_var.set(str(self.sample_info.interpolate))
        if not hasattr(sample.signal, "interpolated"):
            sample.interpolate(
                interpolate=[
                    self.sample_info.interpolate_left,
                    self.sample_info.interpolate_right,
                ],
                smooth_factor=self.sample_info.interpolation_smoothing,
                use=False,
            )

        self.interpolate_lines = [
            self.ax.axvline(x, color="k", linewidth=1, visible=False)
            for x in [self.sample_info.interpolate_left, self.sample_info.interpolate_right]
        ]

        # Calculate ymax and set axis limits
        idx_xaxis = np.logical_and(
            self.xmax > sample.x, sample.x > self.xmin
        )
        y_max = np.max(sample.signal.raw[idx_xaxis]) * 1.2
        self.ax.set_ylim(0, y_max * 1.05)
        self.ax.set_xlim(self.xmin, self.xmax)
        # indeces for interpolation
        idx_interpolate = np.logical_and(
            self.sample_info.interpolate_right > sample.x,
            sample.x > self.sample_info.interpolate_left,
        )
        # Plot spectra
        (self.raw_spectrum,) = self.ax.plot(
            sample.x,
            sample.signal.raw,
            color=self.colors[0],
            label="raw",
        )
        (self.interpolated,) = self.ax.plot(
            sample.x[idx_interpolate],
            sample.signal.interpolated[idx_interpolate],
            color=self.colors[3],
            alpha=0.6,
            label="interpolated",
            visible=True,
        )
        # plot interpolation region
        self.interpolation_region = self.ax.axvspan(
            self.sample_info.interpolate_left,
            self.sample_info.interpolate_right,
            alpha=0.3,
            color=self.interpolation_colors[self.sample_info.interpolate],
            edgecolor=None,
        )

        # Connect mouse events to callback functions
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        self.fig.canvas.mpl_connect("button_release_event", self._on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_motion)

        self.canvas.draw()

    def update_plot(self):
        """ """
        self.sample_info = self.app.current_sample
        sample = self.sample_info.sample
        self.old_spectrum = sample._spectrumSelect
        self.smoothing_var.set(self.sample_info.interpolation_smoothing)
        self.itp_var.set(str(self.sample_info.interpolate))
        if not hasattr(sample.signal, "interpolated"):
            self.sample_info.recalculate_interpolation()

        self.raw_spectrum.set_data(
            sample.x, sample.signal.raw
        )

        for line, x in zip(
            self.interpolate_lines,
            (self.sample_info.interpolate_left, self.sample_info.interpolate_right),
        ):
            line.set_xdata([x, x])

        # Calculate ymax and set axis limits
        idx_xaxis = np.logical_and(
            self.xmax > sample.x, sample.x > self.xmin
        )
        y_max = np.max(sample.signal.raw[idx_xaxis]) * 1.2
        self.ax.set_ylim(0, y_max * 1.05)
        self.ax.set_xlim(self.xmin, self.xmax)

        self.update_interpolation_regions()
        self.draw_interpolation()

    def update_interpolation_regions(self):
        """ """
        polygon = np.array(
            [
                [self.sample_info.interpolate_left, 0.0],
                [self.sample_info.interpolate_left, 1.0],
                [self.sample_info.interpolate_right, 1.0],
                [self.sample_info.interpolate_right, 0.0],
            ]
        )
        self.interpolation_region.set_xy(polygon)
        self.interpolation_region.set(
            color=self.interpolation_colors[self.sample_info.interpolate]
        )
        self.fig.canvas.draw_idle()

    def draw_interpolation(self):
        """ """
        sample = self.sample_info.sample
        idx_interpolate = np.logical_and(
            self.sample_info.interpolate_right > sample.x,
            sample.x > self.sample_info.interpolate_left,
        )
        self.sample_info.recalculate_interpolation()

        self.interpolated.set_data(
            sample.x[idx_interpolate],
            sample.signal.interpolated[idx_interpolate],
        )
        self.fig.canvas.draw_idle()

    def interpolate_check(self):
        """ """
        self.sample_info.interpolate = self.itp_var.get()
        self.interpolation_region.set(
            color=self.interpolation_colors[self.sample_info.interpolate]
        )
        self.fig.canvas.draw_idle()

    def save_interpolation(self):
        """ """
        
        if self.sample_info:
            sample = self.sample_info.sample
            self.sample_info.save_interpolation_settings()
            if self.sample_info.interpolate:
                sample._spectrumSelect = "interpolated"
            else:
                sample._spectrumSelect = self.old_spectrum
            sample.longCorrect()

    def reset_interpolation(self):
        """ """
        # Read old settings
        self.sample_info.read_interpolation()
        # Redraw complete plot
        self.update_plot()

    def validate_smoothing(self, value):
        """
        Return False if the value is not numeric and reset the validate command if not.
        Resetting validate is neccessary, because tkinter disables validation after changing
        the variable through the invalidate command in order to stop an infinte loop.

        If the value is numerical clip it to 0, 10
        """
        try:
            value_clipped = np.clip(float(value), 0, 1000)
            self.smoothing_var.set(value_clipped)
            valid = True
        except ValueError:
            valid = False
        if not valid:
            # self.bell()
            self.smoothing_spinbox.after_idle(
                lambda: self.smoothing_spinbox.config(validate="focus")
            )
        return valid

    def invalid_smoothing(self, value):
        """
        
        """
        self.smoothing_var.set(1)

    def set_interpolation_smoothing(self):
        """
        
        """
        if self.sample:
            smoothing = float(self.smoothing_var.get())
            self.sample_info.interpolation_smoothing = smoothing
            self.draw_interpolation()

    def _on_click(self, event):
        """
        callback method for mouse click event
        """
        # left click
        if event.button == 1 and event.inaxes in [self.ax]:
            line = self._find_neighbor_line(event)
            if line:
                self._dragging_line = line

    def _on_release(self, event):
        """
        Callback method for mouse release event
        """
        if event.button == 1 and event.inaxes in [self.ax] and self._dragging_line:
            new_x = event.xdata
            self.interpolate_lines[self._dragging_line_id] = self._dragging_line
            # self._dragging_line.remove()
            id = self._dragging_line_id
            if id == 0:
                self.sample_info.interpolate_left = round(new_x, -1)
            elif id == 1:
                self.sample_info.interpolate_right = round(new_x, -1)
            self._dragging_line = None
            self._dragging_line_id = None
            # Recalculate and refresh interpolation
            self.update_interpolation_regions()
            self.draw_interpolation()
            # Reset lines (they sometimes seem to move more than the interpolation regions)
            for line, x in zip(
                self.interpolate_lines,
                (self.sample_info.interpolate_left, self.sample_info.interpolate_right),
            ):
                line.set_xdata([x, x])

    def _on_motion(self, event):
        """
        callback method for mouse motion event
        """
        if self._dragging_line:
            new_x = event.xdata
            if new_x:
                # self.fig.canvas.draw_idle()
                id = self._dragging_line_id
                if id == 0:
                    if new_x > self.sample_info.interpolate_right:
                        new_x = self.sample_info.interpolate_right - 20
                    self.sample_info.interpolate_left = new_x
                elif id == 1:
                    if new_x < self.sample_info.interpolate_left:
                        new_x = self.sample_info.interpolate_left + 20
                    self.sample_info.interpolate_right = new_x
                y = self._dragging_line.get_ydata()
                self._dragging_line.set_data([new_x, new_x], y)
                # Recalculate and refresh interpolation
                self.update_interpolation_regions()
                self.draw_interpolation()

    def _find_neighbor_line(self, event):
        """
        Find lines around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 10
        nearest_line = None
        for i, line in enumerate(self.interpolate_lines):
            x = line.get_xdata()[0]
            distance = abs(event.xdata - x)
            if distance < distance_threshold:
                nearest_line = line
                self._dragging_line_id = i
        return nearest_line
