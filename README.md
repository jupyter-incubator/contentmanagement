# Jupyter Content Management Extensions

Content management extensions for Jupyter / IPython Notebook.

## What It Gives You

The content management extensions provide the following:

* Search dialog on dashboard, editor, and notebook screens to search over filenames and `.ipynb` content in the notebook directory
* IPython extension to make notebooks importable, and notebook cells injectable via `# <api>` and `# <help>` annotations (see included example notebooks)
* Full-page drag-and-drop upload target (notebooks only at the moment)
* Pop-over table of contents navigation for notebooks

Watch the first 15-20 minutes of the [September 1st Jupyter meeting video recording](https://www.youtube.com/watch?v=SJiezXPhVv8) for demonstrations of each content management feature.

## What it Lacks

* Tests (they exist, just not ported to the open source yet)
* User docs
* Snippets in search hits (requires Whoosh unicode fixes for Python3)

## Runtime Requirements

* Jupyter Notebook 4.x running on Python 2.7 or Python 3.x
* [scandir](https://github.com/benhoyt/scandir) and [whoosh](http://whoosh.readthedocs.org/en/latest/)
* Notebook instance running out of `profile_default`

These requirements are satisfied automatically when you follow the setup instructions below.

# Try It

We're running a tmpnb instance at http://jupyter.cloudet.xyz with a snapshot of this project (and other related incubator projects) pre-installed.

# Install It

`pip install jupyter_cms` and then restart your notebook server

# Develop

This repository is setup for a Dockerized development environment.  These instructions assume the Docker client is running natively on the local host, and that it is configured to point to a Docker daemon running on a Linux virtual machine.

## Mac OS X

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

Build a Docker image to add the prereqs listed in the Requirements section above.

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

## Intended But Not Here Yet

* Search becomes omnibox for importing notebooks
* Generate secret urls for omnibox to pull directly from other jupyters
* Download files / folders from dashboard screen

