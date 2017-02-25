[![PyPI version](https://badge.fury.io/py/jupyter_cms.svg)](https://badge.fury.io/py/jupyter_cms) [![Build Status](https://travis-ci.org/jupyter-incubator/contentmanagement.svg?branch=master)](https://travis-ci.org/jupyter-incubator/contentmanagement) [![Google Group](https://img.shields.io/badge/-Google%20Group-lightgrey.svg)](https://groups.google.com/forum/#!forum/jupyter)

# Jupyter Content Management Extensions

Content management extensions for Jupyter / IPython Notebook.

## What It Gives You

The content management extensions provide the following:

* Search dialog on dashboard, editor, and notebook screens to search over filenames and `.ipynb` content in the notebook directory
* IPython kernel extension to make Python notebooks reusable as modules and cookbooks (see the [cookbooks tutorial](etc/notebooks/cookbooks_demo/use_cookbooks.ipynb))
* Full-page drag-and-drop upload target
* Pop-over table of contents navigation for notebooks

## Prerequisites

* Jupyter Notebook >=4.2 running on Python 3.x or Python 2.7.x
* Edge, Chrome, Firefox, or Safari

## Install and Enabling

The following steps install the extension package using `pip` and enable the
extension in the active Python environment.

```bash
pip install jupyter_cms
jupyter cms quick-setup --sys-prefix
```

Run `jupyter cms quick-setup --help` for other options. Note that the
second command is a shortcut for the following:

```bash
jupyter serverextension enable --py jupyter_cms --sys-prefix
jupyter nbextension install --py jupyter_cms --sys-prefix
jupyter nbextension enable --py jupyter_cms --sys-prefix
```

Altenratively, the followign command both installs and enables the package
using `conda`.

```bash
conda install jupyter_cms -c conda-forge
```

In either case, you will need to restart your notebook server if it was running
during the enable/activate step.

## Disabling and Uninstalling

The following steps deactivate the extension in the active Python environment
and uninstall the package using `pip`.

```bash
jupyter cms quick-remove --sys-prefix
pip uninstall jupyter_cms
```

Note that the first command is a shortcut for the following:

```bash
jupyter nbextension disable --py jupyter_cms --sys-prefix
jupyter nbextension uninstall --py jupyter_cms --sys-prefix
jupyter serverextension disable --py jupyter_cms --sys-prefix
```

The following command deactivates and uninstalls the package if it was
installed using `conda`.

```bash
conda remove jupyter_cms
```

## Write Bundlers

This extension used to support *bundlers*. That functionality has graduated and
is available in Jupyter Notebook >=5.0. See [Custom bundler
extensions](http://jupyter-notebook.readthedocs.io/en/latest/extending/bundler_extensions.html)
in the documentation for more information.

If you cannot upgrade to notebook>=5.0 and need bundler support, install a version of
this extension prior to 0.7.0.

## Develop It

This repository is setup for a conda-based development environment.  These
instructions assume that have you installed `conda`.

```
# clone this repo if you don't have it
git clone https://github.com/jupyter-incubator/contentmanagement.git
cd contentmanagement

# create a `cms` conda environment
make env

# run unit tests
make test

# run a notebook server with the extension installed
make notebook

# build a source package
make sdist

# release the source package on pypi
make release

# remove built artifacts
make clean

# remove build artifacts and cms environment
make nuke
```

## Other Notes

* Importing notebooks as modules does work with ipyparallel, but not with its `sync_imports` context manager. See the [solution and explanation in issue #32](https://github.com/jupyter-incubator/contentmanagement/issues/32#issuecomment-222053318).
