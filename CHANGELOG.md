# Changelog

## 0.6.0 (2016-08-18)

* Add license file to the package
* Extend `load_notebook` to support injecting imported notebook variables into the local namepsace
* Relax ipython requirements (>=4.1)
* Fix bug where notebooks could be imported without the mywb prefix

## 0.5.0 (2016-04-18)

* Make compatible with Jupyter Notebook 4.0.x through 4.2.x
* Improve documentation about bundlers
* Add new `jupyter cms quick-setup` for notebook 4.2
* Fix pip install in some shell configuration (whitespace problem)
* Fix bundler exception on Python 2 (unicode problem)

## 0.4.0 (2016-01-15)

* Separate `pip install` from `jupyter dashboards [install | activate | deactivate]`
* Match the Python package to the distribution name, `jupyter_cms`

## 0.3.0 (2015-12-30)

* Add server side extension for bundling notebooks for download and deployment
* Define simple framework for plugging in new bundlers
* Add a real tutorial about reusing notebooks as modules and cookbooks
* Keep compatible with Jupyter Notebook 4.0.x

## 0.2.1 (2015-11-22)

* Use standard lib scandir if present (Python 3.5)
* Fix regression of search feature on file tree and editor screens
* Make compatible with Python 2.7 as well as 3.3+
* Keep compatible with Jupyter Notebook 4.0.x

## 0.2.0 (2015-11-18)

* Make compatible with Jupyter Notebook 4.0.x

## 0.1.2 (2015-11-22)

* Make compatible with Python 2.7 as well as 3.3+
* Keep compatible with IPython Notebook 3.2.x

## 0.1.1 (2015-11-16)

* Fix missing PyPI 0.1.0 download

## 0.1.0 (2015-11-12)

* First PyPI release
* Compatible with IPython Notebook 3.2.x on Python 3.3+
