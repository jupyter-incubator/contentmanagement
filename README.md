[![PyPI version](https://badge.fury.io/py/jupyter_cms.svg)](https://badge.fury.io/py/jupyter_cms) [![Build Status](https://travis-ci.org/jupyter-incubator/contentmanagement.svg?branch=master)](https://travis-ci.org/jupyter-incubator/contentmanagement) [![Google Group](https://img.shields.io/badge/-Google%20Group-lightgrey.svg)](https://groups.google.com/forum/#!forum/jupyter)

# Jupyter Content Management Extensions

Content management extensions for Jupyter / IPython Notebook.

## What It Gives You

The content management extensions provide the following:

* Search dialog on dashboard, editor, and notebook screens to search over filenames and `.ipynb` content in the notebook directory
* IPython kernel extension to make Python notebooks reusable as modules and cookbooks (see the [cookbooks tutorial](etc/notebooks/cookbooks_demo/use_cookbooks.ipynb))
* Full-page drag-and-drop upload target
* Pop-over table of contents navigation for notebooks
* Plugin system for deploying and downloading notebook bundles (see *Writing Bundlers* below)
* Example *IPython Notebook bundle (.zip)* download bundler (see the [associations example](etc/notebooks/associations_demo/associations_demo.ipynb))

Watch the first 15-20 minutes of the [September 1st Jupyter meeting video recording](https://www.youtube.com/watch?v=SJiezXPhVv8) for demonstrations of each content management feature.

## Prerequisites

* Jupyter Notebook 4.0.x, 4.1.x, or 4.2.x running on Python 3.x or Python 2.7.x
* Edge, Chrome, Firefox, or Safari

Note: If you're running IPython Notebook 3.2.x, you can install the older 0.1.x version of the extension.

## Try It

If you want to try the extension and demos without installing it yourself, visit the [jupyter-incubator/showcase binder](http://mybinder.org/repo/jupyter-incubator/showcase). If the binder site is full, try the tmpnb instance at [http://jupyter.cloudet.xyz](http://jupyter.cloudet.xyz).

Note that both of these deployments tend to lag the latest stable release.

## Install It

In Jupyter Notebook 4.2, you can install and activate all features of the extension in two commands like so:

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

In Jupyter Notebook 4.2:

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

This extension supports the writing of *bundlers*, Python modules that may take a notebook, transform it (e.g,. using nbconvert), package the result, and either deploy it or download it. 

In Jupyter Notebook 4.2 and higher, a package should declare its metadata by implementing the `_jupyter_bundler_paths` function.

```python
def _jupyter_bundler_paths():
    return [{
            'name': 'notebook_associations_download',
            'label': 'IPython Notebook bundle (.zip)',
            'module_name': 'jupyter_cms.nb_bundler',
            'group': 'download'
    }]
```

The package can then instruct its users to enable and disable its bundlers via `jupyter bundler` command like so:

```bash
jupyter bundler enable --py my_bundlers
jupyter bundler disable --py my_bundlers
```

In earlier versions of Jupyter Notebook, the package must implement its own CLI for enabling and disabling the bundler and update the user-specified config directly like so:

```python
from notebook.services.config import ConfigManager

cm = ConfigManager()

cm.update('notebook', { 
  'jupyter_cms_bundlers': {
    'my_bundle_id': {
      'label': 'My menu item label',
      'module_name': 'some.installed.python.package',
      'group': 'deploy' # or 'download'
    }
  }
})
```

At runtime, a menu item with the given label appears either in the *File &rarr; Deploy as* or *File &rarr; Download as* menu depending on the `group` value. When a user clicks the menu item, a new browser tab opens and contacts the `/api/bundler` handler in this extension. The handler imports `some.installed.python.package` and invokes its `bundle` function. The function must have the following definition:

```python
def bundle(handler, absolute_notebook_path):
  '''
  Transforms, converts, bundles, etc. the notebook. Then issues a Tornado web 
  response using the handler to redirect the browser, download a file, show
  an HTML page, etc. This function must finish the handler response before
  returning either explicitly or by raising an exception.

  :param handler: The tornado.web.RequestHandler that serviced the request
  :param absolute_notebook_path: The path of the notebook on disk
  '''
  handler.finish('Hello world!')
```

The caller of the `bundle` function is a `@tornado.gen.coroutine` decorated function. It wraps its call to `bundle` with `torando.gen.maybe_future`. This behavior means `bundle` may be decorated with `@tornado.gen.coroutine`  and `yield` to avoid blocking the Notebook server main loop during long-running asynchronous operations like so:

```python
from tornado import gen

@gen.coroutine
def bundle(handler, absolute_notebook_path):
  # simulate a long running IO op (e.g., deploying to a remote host)
  yield gen.sleep(10)

  # now respond
  handler.finish('I slept for 10 seconds!')
```

The `handler` passed to bundler is a regular `tornado.web.RequestHandler` instance with two additional properties.

1. `notebook_dir` - The root notebook directory configured for the Jupyter Notebook server
2. `tools` - An instance of [BundlerTools](https://github.com/jupyter-incubator/contentmanagement/blob/master/urth/cms/bundler.py#L15), a set of common convenience functions that may be useful to bundlers

## Develop It

This repository is setup for a Dockerized development environment.  These instructions assume the Docker client is running natively on the local host, and that it is configured to point to a Docker daemon running on a Linux virtual machine.

### Mac OS X

Do this one-time setup if you do not have a local Docker environment yet.

```
brew update

# make sure you're on Docker >= 1.7
brew install docker-machine docker

# create a VirtualBox virtual machine called 'dev' on local host, with Docker daemon installed
docker-machine create -d virtualbox dev

# point Docker client to virtual machine
eval "$(docker-machine env dev)"
```

Clone this repository into a local directory that Docker can volume mount.

```
mkdir -p ~/projects/contentmanagement
cd !$
git clone https://github.com/jupyter-incubator/contentmanagement.git
```

Pull a base Docker image and build a subimage from it that includes [scandir](https://github.com/benhoyt/scandir) and [whoosh](http://whoosh.readthedocs.org/en/latest/) (runtime requirements usually installed by setuptools).

```
make build
```

Run the notebook server in a Docker container.

```
make dev
```

The final `make` command starts a Docker container on your VM with the critical pieces of the source tree mounted where they need to be to get picked up by the notebook server within the container.  Most code changes on your Mac host will have immediate effect within the container.

To see the Jupyter instance with extensions working:

1. Run `docker-machine ip dev` and note the IP of the dev machine.
2. Visit http://THAT_IP:9500 in your browser

See the Makefile for other dev, test, build commands as well as options for each command.

## Other Notes

* Importing notebooks as modules does work with ipyparallel, but not with its `sync_imports` context manager. See the [solution and explanation in issue #32](https://github.com/jupyter-incubator/contentmanagement/issues/32#issuecomment-222053318).