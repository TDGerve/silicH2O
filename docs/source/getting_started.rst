.. include:: ./substitutions.rst


===============
Getting started
===============

Installation
------------




file associations
-----------------
Currently, |silich2o| only supports text files (e.g. txt or csv) for importing raw spectra. Text files should contain no headers and have separate columns for Raman shifts (first) and signal intensity (second).
Characters separating the columns can be whitespaces (any number) or commas.


user interface
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

.. csv-table:: 
    :file: tables/calibration_menu.csv
    :widths: 30, 70
    :header-rows: 1


sample navigation
*****************
Select a sample:

    * by clicking their name
    * with the `next` and `previous` buttons
    * with the up and down arrow keyboard keys

The `delete` button deletes the currently selected samples, where multi-selections are possible.

tool selection
**************
Choose from one of the three processing tools:

    * baseline correction
    * interpolation
    * interference subtraction

Plots and settings and results menus change based on which tool is selected.
