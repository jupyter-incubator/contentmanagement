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

* Jupyter Notebook >=4.0 running on Python 3.x or Python 2.7.x
* Edge, Chrome, Firefox, or Safari

## Install It

In Jupyter Notebook >=4.2, you can install and activate all features of the extension in two commands like so:

```bash
# Install the python package
pip install jupyter_cms

# Install all parts of the extension to the active conda / venv / python env
# and enable all parts of it in the jupyter profile in that environment
# See jupyter cms quick-setup --help for other options (e.g., --user)
jupyter cms quick-setup --sys-prefix
# The above command is equivalent to this sequence of commands:
# jupyter serverextension enable --py jupyter_cms --sys-prefix
# jupyter nbextension install --py jupyter_cms --sys-prefix
# jupyter nbextension enable --py jupyter_cms --sys-prefix
# jupyter bundler enable --py jupyter_cms --sys-prefix
```

In Jupyter Notebook 4.1 and 4.0, you install and activate the extension like so:

```bash
# Install the python package
pip install jupyter_cms
# Register the notebook frontend extensions into ~/.local/jupyter
# See jupyter cms install --help for other options (e.g., --sys-prefix)
jupyter cms install --user --symlink --overwrite
# Enable the JS and server extensions in your ~/.jupyter
jupyter cms activate
```

In either case, you will need to restart your notebook server if it was running during the enable/activate step. Also, note that you can run `jupyter --paths` to get a sense of where the extension files will be installed.

## Uninstall It

In Jupyter Notebook >=4.2:

```bash
# Remove all parts of the extension from the active conda / venv / python env
# See jupyter cms quick-remove --help for other options (e.g., --user)
jupyter cms quick-remove --sys-prefix
# The above command is equivalent to this sequence of commands:
# jupyter bundler disable --py jupyter_cms --sys-prefix
# jupyter nbextension disable --py jupyter_cms --sys-prefix
# jupyter nbextension uninstall --py jupyter_cms --sys-prefix
# jupyter serverextension disable --py jupyter_cms --sys-prefix

# Remove the python package
pip uninstall jupyter_cms
```

In Jupyter Notebook 4.0 and 4.1:

```bash
# Disable extensions, but no way to remove frontend assets in this version
jupyter cms deactivate

# Remove the python package
pip uninstall jupyter_cms
```

## Write Bundlers

This extension used to support *bundlers*. That functionality has graduated and is available in Jupyter Notebook >=5.0. See [Custom bundler extensions](http://jupyter-notebook.readthedocs.io/en/latest/extending/bundler_extensions.html) in the documentation for more information.

## Develop It

This repository is setup for a conda-based development environment.  These instructions assume that have you installed miniconda.

```
# clone this repo if you don't have it
git clone https://github.com/jupyter-incubator/contentmanagement.git
cd contentmanagement

# create `cms-py2` and `cms-py3` conda environments
make build

# run unit tests
make test         # py3
make test-python2 # py2

# run a notebook server with the extension installed as editable
make dev          # py3
make dev-python2  # py2

# build a source package
make sdist

# release the source package on pypi
make release

# remove built artifacts
make clean

# remove build artifacts and cms-py2, cms-py3 environments
make nuke
```

## Other Notes

* Importing notebooks as modules does work with ipyparallel, but not with its `sync_imports` context manager. See the [solution and explanation in issue #32](https://github.com/jupyter-incubator/contentmanagement/issues/32#issuecomment-222053318).
