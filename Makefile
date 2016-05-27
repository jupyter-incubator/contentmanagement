# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: build clean dev help install sdist test install

PYTHON?=python3

REPO:=jupyter/pyspark-notebook:f3028232e94a
DEV_REPO:=jupyter/pyspark-notebook-cms:f3028232e94a
PYTHON2_SETUP:=source activate python2

define EXT_DEV_SETUP
	pushd /src && \
	pip install --no-deps -e . && \
	jupyter cms install --user && \
	jupyter cms activate && \
	popd
endef

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build the dev Docker image
	@-docker rm -f cms-build
	@docker run -it --name cms-build \
		$(REPO) bash -c 'pip install whoosh scandir; \
			$(PYTHON2_SETUP); \
			pip install whoosh scandir'
	@docker commit cms-build $(DEV_REPO)
	@-docker rm -f cms-build

clean: ## Clean source tree
	@-rm -rf dist
	@-rm -rf *.egg-info
	@-rm -rf __pycache__ */__pycache__ */*/__pycache__
	@-find . -name '*.pyc' -exec rm -fv {} \;

dev: dev-$(PYTHON) ## Start notebook server in a container with source mounted

dev-python2: LANG_SETUP_CMD?=$(PYTHON2_SETUP) && python --version
dev-python2: _dev

dev-python3: LANG_SETUP_CMD?=python --version
dev-python3: _dev

_dev: CMD?=start-notebook.sh
_dev: AUTORELOAD?=no
_dev:
	@docker run -it --rm \
		--user jovyan \
		-p 9500:8888 \
		-e AUTORELOAD=$(AUTORELOAD) \
		-v `pwd`:/src \
		-v `pwd`/etc/notebooks:/home/jovyan/work \
		$(DEV_REPO) bash -c '$(LANG_SETUP_CMD) && $(EXT_DEV_SETUP) && $(CMD)'

install: CMD?=exit ## Install and activate the sdist package in the container
install:
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) bash -c 'cd /src/dist && \
			pip install --no-binary :all: $$(ls -1 *.tar.gz | tail -n 1) && \
			jupyter cms install --user && \
			jupyter cms activate && \
			$(CMD)'

sdist: ## Build a source distribution in dist/
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) bash -c 'cp -r /src /tmp/src && \
			cd /tmp/src && \
			python setup.py sdist $(POST_SDIST) && \
			cp -r dist /src'

test: test-$(PYTHON) ## Run tests

test-python2: SETUP_CMD?=$(PYTHON2_SETUP);
test-python2: _test

test-python3: _test

_test: CMD?=cd /src; python --version; python -B -m unittest discover -s test
_test:
# Need to use two commands here to allow for activation of multiple python versions
	@docker run -it --rm \
		-v `pwd`:/src \
		$(DEV_REPO) bash -c '$(SETUP_CMD) $(CMD)'

release: POST_SDIST=register upload
release: sdist ## Package and release to PyPI
