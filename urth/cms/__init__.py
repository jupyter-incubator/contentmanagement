# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from .inject import InjectMagic
from . import search
from . import uploads
from . import loader
from jupyter_core.paths import jupyter_runtime_dir
import os
import json

# Use the built-in version of scandir if possible, otherwise
# use the scandir module version
try:
    from os import scandir
except ImportError:
    from scandir import scandir

def load_ipython_extension(ipython):
    # use the configured working directory if we can find it
    work_dir = None
    for filename in scandir(jupyter_runtime_dir()):
        if filename.name.startswith('nbserver-') and filename.name.endswith('.json'):
            with open(filename.path, 'r') as fh:
                nbserver = json.load(fh)
                work_dir = nbserver['notebook_dir']
                break
    if work_dir is None:
        # fall back on an environment variable or ultimately the pwd
        work_dir = os.getenv('WORK', '.')
    
    loader.enable(work_dir)
    ipython.push({'load_notebook': loader.load_notebook})
    ipython.register_magics(InjectMagic(ipython))
    
def unload_ipython_extension(ipython):
    ipython.drop_by_id({'load_notebook': loader.load_notebook})
    loader.disable()
    del ipython.magics_manager.magics['line']['inject']
    del ipython.magics_manager.registry['InjectMagic']

def load_jupyter_server_extension(nb_app):
    '''
    Loads all extensions within this package.
    '''
    nb_app.log.info('Loaded urth.cms')
    search.load_jupyter_server_extension(nb_app)
    uploads.load_jupyter_server_extension(nb_app)
