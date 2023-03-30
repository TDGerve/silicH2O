.. include:: ./substitutions.rst

=================
|h2o| calibration
=================
The calibration window is opened from the :ref:`Calibrate </getting_started.rst#calibration-window>` menu.
In this window new calibrations can be made with the results from the active project, or existing calibrations can
be imported and linked to the current project. The menu structure is explained on the :ref:`getting started <menus_calibration>` page.


Creating calibrations
---------------------
After importing results from the active project via the menu :ref:`Import<menus_calibration>` *→ current project*, all samples are listed in rows with data for :math:`\frac{{Area}_{silicate}}{{Area}_{H_2O}}` and reference |h2o| contents in columns.
|h2o| contents have to be set by the user by typing values in the appropriate cells. For each sample, you have to indicate wether to include the sample in the calibration
by clicking their respective ``use`` tickboxes. The calibration curve is updated in real-time and is calculated from
a linear regression of :math:`\frac{{Area}_{silicate}}{{Area}_{H_2O}}` against |h2o|, as:


.. math::

    H_2O = a + b \times \frac{{Area}_{silicate}}{{Area}_{H_2O}}

Results are plotted in real-time, where hovering over symbols shows the sample name. 
R\ :sup:`2`, p-value and standard error of estimate (SEE) statistics are also recalculated continuously and displayed
in the top right window corner, together with the fitted intercept and slope.

New calibrations are saved via the menu :ref:`File<menus_calibration>` *→ save as*. This saves the calibration
data in a `.cH2O` file and all underlying spectral data in a new project file (in the `.\\calibration` and `.\\calibration\\projects` folders respectively).
Saving to the activate calibration is done via the menu :ref:`File<menus_calibration>` *→ save* or with the `Ctrl+s` keyboard shortcut.
`.cH2O` files can be exchanged between users, but make sure to only apply calibrations to spectra from the same Raman instrument.

.. figure:: /images/h2o_calibration.gif
    :alt: h2o calibration
    :width: 800

    Setting up a new |h2o| calibration.

Applying calibrations
---------------------
Calibrations are linked to existing projects by importing their `.cH2O` file via the menu :ref:`Import<menus_calibration>`  *→ from file*.
They are applied to the active project by clicking the ``use`` tickbox below the regression statistics.

.. figure:: /images/calibration_stats.png
    :alt: h2o calibration
    :width: 300

    Regression statistics.