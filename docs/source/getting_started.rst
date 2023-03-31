.. include:: ./substitutions.rst


===============
Getting started
===============

Installation
------------
PC
**
|silich2o| is installed by extracting the zipfile downloaded from the latest release on `GitHub <https://github.com/TDGerve/silicH2O>`_ to any location on your computer.
The following folder structure should stay intact:

.. code-block:: bash

    calibration/
    ├─ projects/
    configuration/
    ├─ general_settings.json
    ├─ glass_settings.json
    ├─ glass_settings_default.json
    ├─ interference_settings.json
    ├─ interference_settings_default.json
    SilicH2O/
    ├─ silicH2O.exe
    temp/
    theme/
    silicH2O.exe shortcut

`.\\calibration` 
    `.cH2O` files and `.h2o` projects for :ref:`calibration </h2o_calibration.rst>` 
`.\\configuration` 
    `.json`  files with default :ref:`settings <menus_settings>` for spectral processing
`.\\SilicH2O`
    scripts, dependencies and the executable file.
`.\\temp`
    temporary files used while |silich2o| is running and cleaned upon closing.
`.\\theme`
    app theme (`Breeze <https://github.com/MaxPerl/ttk-Breeze>`_)

The |silich2o| shortcut file can still be moved to any location on your computer. You start |silich2o| by running this shortcut file, or by directly 
running `silicH2O.exe` from the folder `.\\silicH2O`.






Mac
***
TBA


File associations
-----------------
Currently, |silich2o| only supports text files (e.g. txt or csv) for importing raw spectra. Text files should contain no headers and have separate columns for Raman shifts (first) and signal intensity (second).
Characters separating the columns can be whitespaces (any number) or commas.

Once spectra are imported, they can be stored together in :ref:`project files<menus_main>` with `.h2o` extensions (:ref:`File<menus_main>` menu → *save project as*). These files are containers with all spectral data and processing settings 
and can be exchanged and shared between users, encouraging transparent and reproducible data processing.

Calibration data are stored in `.cH2O` files, which can be assigned to any project. By default these files are stored in the `.\\calibration` folder at the top level of the |silich2o| folder.
When saving a new calibration, calibration spectra are also saved as projects in the `.\\calibration\\projects` folder. These projects can later be imported from the :ref:`Calibration menu<menu_main_calibration>`
to make changes or review the data.

|silich2o| stores temporary files in the `.\\temp` folder, do not delete these while the program is running, they are cleaned up automatically upon exiting |silich2o|.


User interface
--------------

.. note:: 
    Keep an eye on the lower left corner of the :ref:`infobar </getting_started.rst#info-bar>`! Informational messages are displayed here frequently.

The user interface has six main components:

.. figure:: /images/gui_0.png
    :alt: main gui
    :width: 800

    Main user interface of |silich2o|

    1 - menus
        Import and export spectra, change settings and set calibrations.
    2 - sample navigation
        Change samples.    
    3 - tool selection
        Select baseline correctin, interpolation or interference correction.
    4  - interactive plot
        Adjust various processing setting by clicking and dragging items in the plot. The plot changes based on the selected tool
    5 - settings and results
        Change processing parameters and get results.
    6 - info bar
        displays information messages and X-Y plot coordinates and has buttons for saving and resetting samples.

    
.. _menus_main:

menus
*****

.. csv-table:: 
    :file: tables/file_menu.csv
    :widths: 30, 70
    :header-rows: 1

.. _menus_settings:

.. csv-table:: 
    :file: tables/settings_menu.csv
    :widths: 10, 20, 70
    :header-rows: 1

Default settings are stored in `.json` files in the `.\\configuration` folder, all settings can also be manually adjusted there.

.. _menu_main_calibration:

.. csv-table:: 
    :file: tables/calibration_menu.csv
    :widths: 30, 70
    :header-rows: 1


sample navigation
*****************
Select a sample:

    * by left-clicking its name
    * with the `next` and `previous` buttons
    * with the up and down arrow keyboard keys

The `delete` button deletes currently selected samples, where multi-selections are possible with `shift + left-click` or `Ctrl + left-click`.

.. figure:: /images/sample_navigation.gif
    :alt: plot navigation
    :width: 800

    Sample navigation (with keystrokes displayed).

tool selection
**************
Choose from one of three processing tools:

    * :ref:`baseline correction<Baseline correction>`
    * :ref:`interpolation<Interpolation>`
    * :ref:`interference subtraction<Interference subtraction>`

Plots and menus for settings and results change based on which tool is selected.

|silich2o| processes spectra in the following order:

 `interference subtraction` → `interpolation` → `baseline correction`

As a consequence, some types of processing are not possible, for example:

    * interference subtraction on interpolated spectra, 
    * interpolation on baseline corrected spectra.

If this is needed, exporting processed spectra and re-importing them is a suitable workaround.

interactive plot
****************
Plot of the current sample. Plot layout varies with the selected tool and each tool has interactive elements to adjust various parameters.
See :ref:`baseline correction<Baseline correction>`, :ref:`interpolation<Interpolation>` and :ref:`interference subtraction<Interference subtraction>`

On the righ-hand side there are several tools for plot navigation:

.. figure:: /images/plot_buttons.png
    :alt: plot navigation buttons
    :width: 400

.. note:: 
    Don't forget to deselect navigation tools when you no longer want to use them. 


.. figure:: /images/plot_navigation.gif
    :alt: plot navigation
    :width: 800

    Plot navigation.


settings and results
********************
Shows settings and results of the current tool.

info bar
********
X-Y plot coordinates of the mouse location are displayed on the right and occasional information messages on the left. The ``reset sample`` button resets the current 
sample to the last saved state and ``save sample`` and ``save all`` save the settings and results of the current sample and all samples respectively .

.. note:: 
    Saving a sample, or all samples, does not yet save the project. This can only be done via *File → save project (as)* or with the *Ctrl+s* keyboard shortcut.
    If you have not yet saved your data to a project file *Ctrl+s* functions the same as `save all`. Keep an eye on the messages in the lower left corner of the :ref:`info bar<info bar>`, they will
    tell you how your data have been saved.

Calibration window
------------------
The calibration window is where you :ref:`create new calibrations <|h2o| calibration>` and link them to projects.

.. figure:: /images/calibration.png
    :alt: calibration window
    :width: 800

    The calibration window

    1 - menus
        Importing and saving calibration data.
    2 - calibration data
        Set reference |h2o| contents and select which samples to use.
    3 - calibration curve
        Plot with calibration data and curve. Hover over symbols to see sample names.
    4 - regression statistics
        Statistics of the linear regression. Select the tickbox *use* to link the current calibration to the active project.

.. _menus_calibration:

menus
*****

.. csv-table:: 
    :file: tables/calibration_import_menu.csv
    :widths: 30, 70
    :header-rows: 1

.. csv-table:: 
    :file: tables/calibration_file_menu.csv
    :widths: 30, 70
    :header-rows: 1



Keyboard shortcuts
------------------
.. csv-table:: 
    :file: tables/keyboard_shortcuts.csv
    :widths: 30, 70
    :header-rows: 1
