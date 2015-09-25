# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: clean dev help sdist test install

TAG?=cms-dev

help:
	@echo 'Host commands:'
	@echo '     build - build dev image'
	@echo '     clean - clean built files'
	@echo '       dev - start notebook server in a container with source mounted'
	@echo '   install - install latest sdist into a container'
	@echo '     sdist - build a source distribution into dist/'
	@echo '      test - run unit tests within a container'

build:
	@docker build --rm -t jupyter/pyspark-notebook:$(TAG) .

clean:
	@-rm -rf dist
	@-rm -rf *.egg-info
	@-rm -rf __pycache__ */__pycache__ */*/__pycache__
	@-find . -name '*.pyc' -exec rm -fv {} \;

dev: NB_HOME?=/home/jovyan
dev: REPO?=jupyter/pyspark-notebook:$(TAG)
dev: CMD?=sh -c "ipython notebook --no-browser --port 8888 --ip='*'"
dev: AUTORELOAD?=no
dev:
	@docker run -it --rm \
		-p 9500:8888 \
		-e AUTORELOAD=$(AUTORELOAD) \
		-v `pwd`/urth_cms_js:$(NB_HOME)/.ipython/nbextensions/urth_cms_js \
		-v `pwd`/etc:$(NB_HOME)/.ipython/profile_default/nbconfig \
		-v `pwd`/urth:/opt/conda/lib/python3.4/site-packages/urth \
		-v `pwd`/etc/ipython_notebook_config.py:$(NB_HOME)/.ipython/profile_default/ipython_notebook_config.py \
		-v `pwd`/etc/notebooks:$(NB_HOME)/work \
		$(REPO) $(CMD)

install: REPO?=jupyter/pyspark-notebook:$(TAG)
install: CMD?=exit
install:
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) bash -c 'cd /src/dist && \
			pip install $$(ls -1 *.tar.gz | tail -n 1) && \
			$(CMD)'

sdist: REPO?=jupyter/pyspark-notebook:$(TAG)
sdist: RELEASE?=
sdist: BUILD_NUMBER?=0
sdist: GIT_COMMIT?=HEAD
sdist:
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) bash -c 'cp -r /src /tmp/src && \
			cd /tmp/src && \
			echo "$(BUILD_NUMBER)-$(GIT_COMMIT)" > VERSION && \
			python setup.py sdist && \
			cp -r dist /src'

test: REPO?=jupyter/pyspark-notebook:$(TAG)
test: CMD?=bash -c 'cd /src; python3 -B -m unittest discover -s test'
test:
	@docker run -it --rm \
		-v `pwd`:/src \
		$(REPO) $(CMD)
