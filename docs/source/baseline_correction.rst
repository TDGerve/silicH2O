.. include:: ./substitutions.rst

===================
Baseline correction
===================
This tool calculates background signal baselines and subtracts them from the raw signal.
Baseline interpolation regions (*BIRs*, grey bars in the plots) are used to calculate baselines with the :py:meth:`baselineCorrect() <ramcoh:ramCOH.raman.baseclass.RamanProcessing.baselineCorrect>` method
from `ramCOH <https://ramcoh.readthedocs.io/en/latest>`_. Exact *BIR* positions are shown in the :ref:`settings bar </getting_started.rst#settings-and-results>`, with numbered *BIRs* in rows and their start and end coordinates in columns.
With the plus and minus buttons next to the coordinates, *BIRs* can be added or removed, where new *BIRs* are placed to the right of the one where the button was pressed.

.. figure:: /images/baseline_correction/baseline_settings.png
    :alt: baseline correction settings
    :width: 300

    baseline settings.

.. figure:: /images/baseline_correction/remove_add_birs.gif
    :alt: remove or add birs
    :width: 800

    Removing and adding *BIRs*.

BIR positions
-------------
.. note:: 
    Default *BIRs* can be changed, see :ref:`settings <menus_settings>`.
By default |silich2o| uses five *BIRs*:
one at the end and start of the spectrum, one in between the silicate and |h2o| regions and two intermediate in the silicate region.

Their positions can be adjusted for each sample in two ways:

    * by typing exact values in the settings bar.
    * by clicking and dragging directly in the plot.

In the settings bar, boundary positions are changed by typing a new value in one of the cells and confirming by pressing the *Enter* key.

In the plot, *BIR* boundaries are moved by clicking and dragging them left or right:

.. figure:: /images/baseline_correction/move_birs.gif
    :alt: move bir boundaries
    :width: 800

    Moving *BIR* boundary positions.

By clicking and dragging from inside a *BIR* the entire *BIR* can be moved around:

.. figure:: /images/baseline_correction/move_birs_2.gif
    :alt: move birs
    :width: 800

    Moving *BIR* positions.


Baseline correction settings (*BIR* positions and smoothing settings) can be copied with the keyboard shortcut *Ctrl+q* and applied to a different sample by pasting with *Ctrl+w*


Baseline smoothing
------------------
Baseline smoothing is adjusted via the smoothing parameter in the settings bar, with values between 0 and 100. At values close to zero the baseline will be linear, while at high values it will closely follow 
the datapoints in the *BIRs*
Default smoothing is set to 1.0, which generally works well for silicate glasses.
Smoothing values are passed to the the ``smooth_factor`` parameter of the :py:meth:`baselineCorrect() <ramcoh:ramCOH.raman.baseclass.RamanProcessing.baselineCorrect>` method.

Results
-------
Baseline corrections produce two types of results: 

    * signal-to-noise ratios, calculated with :py:meth:`ramCOH.Glass.calculate_SNR() <ramcoh:ramCOH.raman.glass.Glass.calculate_SNR>`
    * integrated peak areas, calculated with :py:meth:`ramCOH.Glass.calculate_SiH2Oareas() <ramcoh:ramCOH.raman.glass.Glass.calculate_SiH2Oareas>`
  
both are updated in the :ref:`results bar </getting_started.rst#settings-and-results>` in real-time as parameters are adjusted:

.. figure:: /images/baseline_correction/baseline_results.png
    :alt: baseline correction results
    :width: 300

    baseline correction results.

Signal strength is calculated separately for silicate and |h2o|, as the maximum baseline corrected intensity within each region. Noise
is calculated from datapoints within the *BIRs* as two standard deviations on the baseline corrected signal. Keep in mind that this only produces realistic noise values
if these regions are free from peaks.

Peak areas are calculated for the silicate and |h2o| regions, with boundaries from :py:meth:`ramCOH.Glass._get_Si_H2O_regions() <ramcoh:ramCOH.raman.glass.Glass._get_Si_H2O_regions>`.
If a :ref:`calibration </h2o_calibration.rst>` is linked to the active project, sample |h2o| contents are shown in the bottom right corner.

.. figure:: /images/baseline_correction/h2o.png
    :alt: calculated h2o
    :width: 300

    calculated |h2o| contents.