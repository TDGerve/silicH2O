.. include:: ./substitutions.rst

=============
Interpolation
=============
.. note:: 
    interpolation should only be applied when unwanted peaks are clearly defined and when interpreting the original unaffected signal is straightforward.
    For spectra with with strong interference the unmixing tool is potentially a better suited option.

With this tool you can get rid of regions with unwanted peaks by replacing them with interpolations. One or more regions can be selected by the user, across which interpolations are calculated with 
the :py:meth:`interpolate() <ramcoh:ramCOH.raman.baseclass.RamanProcessing.interpolate>` method from `ramCOH <https://ramcoh.readthedocs.io/en/latest>`_.
The algorithm is similar to the one used for calculating :ref:`baselines </baseline_correction.rst>` and its settings are adjusted similarly as well. 

Interpolation regions are set

    * by typing absolute boundary values the :ref:`settings bar </getting_started.rst#settings-and-results>` or
    * by clicking and dragging the grey bars in the plot.

.. figure:: /images/interpolation/interpolation_settings.png
    :alt: interpolation settings
    :width: 300

    interpolation settings.

.. figure:: /images/interpolation/interpolation.gif
    :alt: remove or add birs
    :width: 800

    Removing olivine (790--870 |cm-1|) and resin peaks (1390--1640 and 2800--3130 |cm-1|) by interpolating.


Smoothing of the interpolated signal is set the same as :ref:`baseline smoothing </baseline_correction.rst#baseline-smoothing>`.
Interpolated signals are shown as blue lines and are recalculated in real-time and adjusted with each parameter change. If you are happy with the results, click the `use` tickbox in the :ref:`settings bar </getting_started.rst#settings-and-results>`
to continue using the interpolated spectrum in the :ref:`baseline correction tool </baseline_correction.rst>`.
Only the datapoints inside the interpolation regions will be replaced by interpolated signal, the rest of the spectrum stays intact.

