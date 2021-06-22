Generating the documentation
============================

Install `sphinx`, move to the `amdapy/amdapy/docs` folder and execute :
```
make html
firefox _build/html/index.html
```

The `nbsphinx` is required for building the documentation from `.ipynb` files. Install
with :
```
python3 -m pip install nbsphinx
```

