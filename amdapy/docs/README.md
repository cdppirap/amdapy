Generating the documentation
============================

Install :program:`sphinx`, move to the :data:`amdapy/amdapy/docs` folder and execute :
```
make html
firefox _build/html/index.html
```

The :program:`nbsphinx` is required for building the documentation from :data:`.ipynb` files. Install
with ::
```
python3 -m pip install nbsphinx
```

