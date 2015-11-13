# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from setuptools import setup
from setuptools.command.install import install

from IPython.html.nbextensions import install_nbextension
from IPython.html.services.config import ConfigManager

# Get location of this file at runtime
HERE = os.path.abspath(os.path.dirname(__file__))

# Eval the version tuple and string from the source
VERSION_NS = {}
with open(os.path.join(HERE, 'urth/cms/_version.py')) as f:
    exec(f.read(), {}, VERSION_NS)

EXT_DIR = os.path.join(os.path.dirname(__file__), 'urth_cms_js')
SERVER_EXT_CONFIG = "c.NotebookApp.server_extensions.append('urth.cms')"

class InstallCommand(install):
    def run(self):
        print('Installing Python module')
        install.run(self)
        
        print('Installing notebook extension')
        install_nbextension(EXT_DIR, overwrite=True, user=True)
        cm = ConfigManager()
        print('Enabling extension for notebook')
        cm.update('notebook', {"load_extensions": {'urth_cms_js/notebook/main': True}})
        print('Enabling extension for dashboard')
        cm.update('tree', {"load_extensions": {'urth_cms_js/dashboard/main': True}})
        print('Enabling extension for text editor')
        cm.update('edit', {"load_extensions": {'urth_cms_js/editor/main': True}})

        print('Installing notebook server extension')
        fn = os.path.join(cm.profile_dir, 'ipython_notebook_config.py')
        with open(fn, 'r+') as fh:
            lines = fh.read()
            if SERVER_EXT_CONFIG not in lines:
                fh.seek(0, 2)
                fh.write('\n')
                fh.write(SERVER_EXT_CONFIG)

setup(
    name='jupyter_cms',
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    description='IPython / Jupyter extensions for advanced content management',
    url='https://github.com/jupyter-incubator/contentmanagement',
    version=VERSION_NS['__version__'],
    license='BSD',
    platforms=['IPython Notebook 3.x'],
    packages=[
        'urth', 
        'urth.cms'
    ],
    install_requires=[
        'whoosh', 
        'scandir'
    ],
    cmdclass={
        'install': InstallCommand
    }
)