.. include:: ./substitutions.rst


===============
Getting started
===============

Installation
------------
PC
**
|silich2o| is installed by extracting the zipfile downloading the latest from `GitHub <https://github.com/TDGerve/silicH2O>`_ to any location on your computer, but keep in mind that its folder structure should stay intact.
The |silich2o| shortcut file can still be moved to any location on your computer. You start |silich2o| by running this shortcut file, or by directly 
running `silicH2O.exe` from the folder `.\\silicH2O`

Mac
***


File associations
-----------------
Currently, |silich2o| only supports text files (e.g. txt or csv) for importing raw spectra. Text files should contain no headers and have separate columns for Raman shifts (first) and signal intensity (second).
Characters separating the columns can be whitespaces (any number) or commas.

Once spectra are imported, they can be stored together in :ref:`project files<menus>` with `.h2o` extensions. These files are containers with all spectral data and processing settings 
and can be exchanged and shared between users, encouraging transparent and reproducible data processing.

Calibration data are stored in `.cH2O` files, which can be assigned to any project. By default these files are stored in the `.\\calibration` folder at the top level of the |silich2o| folder.
When saving a new calibration, calibration spectra are also saved as projects in the `.\\calibration\\projects` folder. These projects can later be imported from the :ref:`Calibration menu<menus>`
to make changes or review the data.


User interface
--------------

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

    

menus
*****

.. csv-table:: 
    :file: tables/file_menu.csv
    :widths: 30, 70
    :header-rows: 1

.. csv-table:: 
    :file: tables/settings_menu.csv
    :widths: 10, 20, 70
    :header-rows: 1

Default settings are stored in `.json` files in the `.\\configuration` folder, all settings can also be manually adjusted there.

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

The `delete` button deletes the currently selected samples, where multi-selections are possible.

tool selection
**************
Choose from one of three processing tools:

    * :ref:`baseline correction<tutorial 1: baseline correction>`
    * :ref:`interpolation<tutorial 3: interpolation>`
    * :ref:`interference subtraction<tutorial 4: interference subtraction>`

Plots and settings and results menus change based on which tool is selected.

interactive plot
****************
Plot of the current sample. Plot layout varies with the selected tool and each tool has interactive elements to set varies processing parameters.
See :ref:`baseline correction<tutorial 1: baseline correction>`, :ref:`interpolation<tutorial 3: interpolation>` and :ref:`interference subtraction<tutorial 4: interference subtraction>`

On the righ-hand side there are several tools for plot navigation:

.. figure:: /images/plot_buttons.png
    :alt: main gui
    :width: 400


settings and results
********************
Shows settings and results of the current tool.

info bar
********
X-Y plot coordinates of the mouse location are displayed on the right and occasional information messages on the left. The `reset sample` button resets the current 
sample to the last saved state and `save sample` and `save all` respectively save the current sample and all samples.

Keyboard shortcuts
------------------
.. csv-table:: 
    :file: tables/keyboard_shortcuts.csv
    :widths: 30, 70
    :header-rows: 1

