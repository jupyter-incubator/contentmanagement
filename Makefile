# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: build clean dev help install sdist test install

PYTHON?=python3

REPO:=jupyter/pyspark-notebook:a388c4a66fd4
CMS_REPO:=jupyter/pyspark-notebook-cms:a388c4a66fd4
PYTHON2_SETUP:=source activate python2;

help:
	@echo 'Host commands:'
	@echo '     build - build dev image'
	@echo '     clean - clean built files'
	@echo '       dev - start notebook server in a container with source mounted'
	@echo '   install - install latest sdist into a container'
	@echo '     sdist - build a source distribution into dist/'
	@echo '      test - run unit tests within a container'

build:
	@-docker rm -f cms-build
	@docker run -it --name cms-build \
		$(REPO) bash -c 'pip install whoosh scandir; \
			$(PYTHON2_SETUP); \
			pip install whoosh scandir'
	@docker commit cms-build $(CMS_REPO)
	@-docker rm -f cms-build

clean:
	@-rm -rf dist
	@-rm -rf *.egg-info
	@-rm -rf __pycache__ */__pycache__ */*/__pycache__
	@-find . -name '*.pyc' -exec rm -fv {} \;

dev: dev-$(PYTHON)

dev-python2: SETUP_CMD?=$(PYTHON2_SETUP)
dev-python2: EXTENSION_DIR=/opt/conda/envs/python2/lib/python2.7/site-packages/urth
dev-python2: _dev

dev-python3: EXTENSION_DIR=/opt/conda/lib/python3.4/site-packages/urth
dev-python3: _dev

_dev: NB_HOME?=/root
_dev: CMD?=sh -c "python --version; jupyter notebook --no-browser --port 8888 --ip='*'"
_dev: AUTORELOAD?=no
_dev:
	@docker run -it --rm \
		-p 9500:8888 \
		-e AUTORELOAD=$(AUTORELOAD) \
		-v `pwd`/urth_cms_js:$(NB_HOME)/.local/share/jupyter/nbextensions/urth_cms_js \
		-v `pwd`/urth:$(EXTENSION_DIR) \
		-v `pwd`/etc/jupyter_notebook_config.py:$(NB_HOME)/.jupyter/jupyter_notebook_config.py \
		-v `pwd`/etc/notebook.json:$(NB_HOME)/.jupyter/nbconfig/notebook.json \
		-v `pwd`/etc/tree.json:$(NB_HOME)/.jupyter/nbconfig/tree.json \
		-v `pwd`/etc/edit.json:$(NB_HOME)/.jupyter/nbconfig/edit.json \
		-v `pwd`/etc/notebooks:/home/jovyan/work \
		$(CMS_REPO) bash -c '$(SETUP_CMD) $(CMD)'

install: CMD?=exit
install:
	@docker run -it --rm \
		--user jovyan \
		-v `pwd`:/src \
		$(REPO) bash -c 'cd /src/dist && \
			pip install --no-binary :all: $$(ls -1 *.tar.gz | tail -n 1) && \
			$(CMD)'

sdist: REPO?=jupyter/pyspark-notebook:$(TAG)
sdist:
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) bash -c 'cp -r /src /tmp/src && \
			cd /tmp/src && \
			python setup.py sdist $(POST_SDIST) && \
			cp -r dist /src'

test: CMD?=bash -c 'cd /src; python3 -B -m unittest discover -s test'
test:
	@echo No tests yet ...	
# @docker run -it --rm \
# 	-v `pwd`:/src \
# 	$(CMS_REPO) $(CMD)

release: POST_SDIST=register upload
release: sdist
