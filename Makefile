# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: activate build clean dev help install nuke sdist test

ENV:=cms

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

activate: ## eval $(make activate)
	@echo "source activate $(ENV)"

build: ## Build dev environments
	@conda create -y -n $(ENV) -c conda-forge python=3 \
		notebook pandas scikit-learn matplotlib seaborn ipywidgets widgetsnbextension
	@source activate $(ENV) && \
		pip install -e . && \
		jupyter cms quick-setup --sys-prefix

clean: ## Clean source tree
	@-rm -rf dist
	@-rm -rf *.egg-info
	@-rm -rf __pycache__ */__pycache__ */*/__pycache__
	@-find . -name '*.pyc' -exec rm -fv {} \;

nuke: clean ## Clean source tree and dev environments
	-conda env remove -n $(ENV) -y

dev:
	source activate $(ENV) && jupyter notebook --notebook-dir=./etc/notebooks

sdist: ## Build a source distribution in dist/
	source activate $(ENV) && python setup.py sdist

test: ## Run tests
	source activate $(ENV) && python -B -m unittest discover -s test

release: sdist ## Package and release to PyPI
	source activate $(ENV) && python setup.py sdist register upload

