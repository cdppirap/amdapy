.. code-block:: python

   for dataset in amdapy.Provider(name="PDS").iter_dataset():
       for variable in dataset.iter_variable(units=amdapy.units.NANOTESLA):
           print(dataset)
           continue
