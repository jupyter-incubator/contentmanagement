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

* Jupyter Notebook 4.0.x running on Python 3.x or Python 2.7.x
* Edge, Chrome, Firefox, or Safari

Note: If you're running IPython Notebook 3.2.x, you can install the older 0.1.x version of the extension.

## Try It

If you want to try the extension and demos without installing it yourself, visit the [jupyter-incubator/showcase binder](http://mybinder.org/repo/jupyter-incubator/showcase). If the binder site is full, try the tmpnb instance at [http://jupyter.cloudet.xyz](http://jupyter.cloudet.xyz).

Note that both of these deployments tend to lag the latest stable release.

## Install It

`pip install jupyter_cms` and then restart your Notebook server if it was running during the install.

## Writing Bundlers

This extension supports the writing of *bundlers*, Python modules that may take a notebook, transform it (e.g,. using nbconvert), package the result, and either deploy it or download it. Bundlers should register themselves at install time using code like the following:

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
  handler.finish('Hello world!'')
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

## Develop

This repository is setup for a Dockerized development environment.  These instructions assume the Docker client is running natively on the local host, and that it is configured to point to a Docker daemon running on a Linux virtual machine.

### Mac OS X

Do this one-time setup if you do not have a local Docker environment yet.

Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

Download and install Docker.

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
