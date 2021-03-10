.. amdapy documentation master file, created by
   sphinx-quickstart on Fri Feb 12 12:11:41 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to amdapy's documentation!
==================================

This package aims to offer streamlined access to heliophysics dataset provided by AMDA (and other 
providers).

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


AMDA
====

This package aims to provide streamlined access to dataset available on :program:`AMDA` (as well as some other
data providers). :program:`AMDA` provides a collection of visualization and analysis tools for heliophical data
and this python package aims to provide an interface for retrieving datasets without accessing the 
online plateform as well as a collection of tools for analysing the data. 

Interacting with AMDA is done through the :class:`amdapy.amda.AMDA` class which implements methods
for navigating and querying the AMDA dataset catalogue. The connector object is initialized simply

.. code-block:: python

   >>> amda = amdapy.amda.AMDA()

Missions and instruments
------------------------

In AMDA datasets are associated with a pair (Mission, Instrument). Retrieving a list of missions is
done like this : 

.. code-block:: python

   >>> [m.name for m in amda.mission()]
   ['ACE', 'AMPTE',..., 'VEX', 'Voyager', 'Wind']

In a similar fashion we can get a list of instruments associated with a mission, here we fetch
names of all instruments aboard the ACE mission.

.. code-block:: python

   >>> [i.name for i in amda.instruments("ACE")]
   ['MFI', 'SWEPAM', 'Ephemeris']

List all datasets associated with mission ACE and instrument MFI

.. code-block:: python

   >>> for dataset in amda.iter_dataset(mission="ACE", instrument="MFI"):
   >>>   print(dataset)
   AMDADataset(id:ace-imf-all, start:1997-09-02 00:00:12, stop:2021-02-27 23:59:48, n_param:3)
   AMDADataset(id:ace-mag-real, start:2020-11-11 00:00:00, stop:2021-03-10 03:59:59, n_param:3)

Iterate over variables belonging to the dataset

.. code-block:: python

   >>> dataset = amda.get_dataset("ace-imf-all")
   >>> for var in dataset.iter_variable():
   >>>   print(var.name, var.units)
   |b| nT
   b_gse nT
   b_gsm nT

Dataset exploration
-------------------

Accessing AMDA datasets is done through methods provided by the :class:`amdapy.amda.AMDA` class. Getting datasets from AMDA : 

.. code-block:: python

   >>> amda = amdapy.amda.AMDA()
   >>> # iterate over datasets
   >>> for dataset in amda.iter_dataset():
   >>>   print("Dataset id : {}".format(dataset.id))
   AMDADataset(id:ace-imf-all)
   AMDADataset(id:ace-mag-real)
   ...
   AMDADataset(id:wnd-swe-kp)

The objects returned by :meth:`amdapy.amda.AMDA.iter_dataset` are of type :class:`amdapy.amda.AMDADataset`. Retrieving the contents of the dataset can be time consumming, thus a call to the 
:meth:`amdapy.amda.AMDADataset.get` method is needed before accessing the contents of the dataset. 
The available information are the start and stop time of the dataset and the shape of it's variables. 
A specific dataset can be retrieved by its :data:`id` with the :meth:`amdapy.amda.AMDA.get_dataset` method.

Once the data has been loaded the user can access the variables of the dataset.

.. code-block:: python

   >>> dataset_id="ace-imf-all"
   >>> dataset = amda.get_dataset(dataset_id)
   >>> print([variable.name for variable in dataset.variables])
   []
   >>> dataset.get()
   >>> print([variable.name for variable in dataset.variables])
   ['imf_mag','imf','imf_gsm']

Variable data is available a :class:`amdapy.core.variable.Variable` objects.

.. code-block:: python

   >>> type(dataset.variables[0])
   <class 'amdapy.core.variable.Variable'>


Variables and Datasets
----------------------

The variables values are stored as :class:`pandas.DataFrame` objects, elements can be accessed using
the bracket operator.

.. code-block:: python

   >>> var = dataset.variables[0]
   >>> type(var[:])
   <class 'pandas.core.frame.DataFrame'>
   >>> var[:]
                      Time  imf_mag
   0   1997-09-02 00:00:28    2.348
   1   1997-09-02 00:00:44    2.384
   2   1997-09-02 00:01:00    2.302
   3   1997-09-02 00:01:16    2.370
   4   1997-09-02 00:01:32    2.455
   ..                  ...      ...
   220 1997-09-02 00:59:08    3.679
   221 1997-09-02 00:59:24    3.755
   222 1997-09-02 00:59:40    3.675
   223 1997-09-02 00:59:56    3.619
   224 1997-09-02 01:00:12    3.631
   
   [225 rows x 2 columns]


Data providers
--------------

Datasets are available on a multitude of platforms, the ones :program:`amdapy` provides access to are
AMDA, PDS, CDAWEB. The last two providers offer a public index listing all available datasets. New 
providers may be defined by sublcassing the :class:`amdapy.provider.DataProvider` class. We can view
the list of providers through the :meth:`amdapy.provider.iter_provider`. Providers are identified 
by their name, which should be unique. The simplest data providers are built around manipulating their
public index. New providers can easly be defined for any website offering a public index of their data
files.

The :meth:`amdapy.ddtime.DDTime.from_datetime` method. 
