# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: build clean dev help install sdist test

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

activate: ## eval $(make activate)
	@echo "source activate cms-py3"

build: ## Build dev environments
	@conda create -y -n cms-py3 python=3 notebook whoosh pandas scikit-learn matplotlib seaborn ipywidgets
	@source activate cms-py3 && pip install -e . && jupyter cms quick-setup --sys-prefix
	@conda create -y -n cms-py2 python=2 notebook whoosh scandir
	@source activate cms-py2 && pip install -e . && jupyter cms quick-setup --sys-prefix

clean: ## Clean source tree
	@-rm -rf dist
	@-rm -rf *.egg-info
	@-rm -rf __pycache__ */__pycache__ */*/__pycache__
	@-find . -name '*.pyc' -exec rm -fv {} \;

nuke: clean ## Clean source tree and dev environments
	-conda env remove -n cms-py3 -y
	-conda env remove -n cms-py2 -y

dev: dev-python3
dev-python2: ENV=cms-py2
dev-python2: _dev
dev-python3: ENV=cms-py3
dev-python3: _dev
_dev:
	source activate $(ENV) && jupyter notebook --notebook-dir=./etc/notebooks

sdist: ## Build a source distribution in dist/
	source activate $(ENV) && python setup.py sdist

test: test-python3 ## Run tests
test-python2: ENV=cms-py2
test-python2: _test
test-python3: ENV=cms-py3
test-python3: _test
_test:
	source activate $(ENV) && python -B -m unittest discover -s test

release: sdist ## Package and release to PyPI
	source activate $(ENV) && python setup.py sdist register upload

