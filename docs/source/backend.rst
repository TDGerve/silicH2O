.. include:: ./substitutions.rst

=======
Backend
=======
SilicH2O uses ramCOH as a backend and a comprehensive desciption of all its code is available at `ramCOH.readthedocs.io <https://ramcoh.readthedocs.io/en/latest>`_.


Spectra imported from the main |silich2o| menu are initialised with instances of its :py:class:`~ramcoh:ramCOH.raman.glass.Glass` class and interference spectra with the general :py:class:`~ramcoh:ramCOH.raman.baseclass.RamanProcessing` class.
The methods implemented in each tool are linked in their respective documentation pages:

    * :ref:`baseline correction<Baseline correction>`
    * :ref:`interpolation<Interpolation>`
    * :ref:`interference subtraction<Interference subtraction>`


ramCOH is a stand-alone Python library and all its code can also be used without the |silich2o| interface, in scripts or from the command line.
This gives the user a bit more flexibility, sinc |silich2o| uses fixed default values for some method parameters.
