# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

from notebook.nbextensions import install_nbextension
from notebook.services.config import ConfigManager
from jupyter_core.paths import jupyter_config_dir

# Get location of this file at runtime
HERE = os.path.abspath(os.path.dirname(__file__))

# Eval the version tuple and string from the source
VERSION_NS = {}
with open(os.path.join(HERE, 'urth/cms/_version.py')) as f:
    exec(f.read(), {}, VERSION_NS)

EXT_DIR = os.path.join(os.path.dirname(__file__), 'urth_cms_js')
SERVER_EXT_CONFIG = "c.NotebookApp.server_extensions.append('urth.cms')"

def _install_notebook_extension():
    print('Installing notebook extension')
    install_nbextension(EXT_DIR, overwrite=True, user=True)
    cm = ConfigManager()
    print('Enabling extension for notebook')
    cm.update('notebook', {"load_extensions": {'urth_cms_js/notebook/main': True}})
    print('Enabling extension for dashboard')
    cm.update('tree', {"load_extensions": {'urth_cms_js/dashboard/main': True}})
    print('Enabling extension for text editor')
    cm.update('edit', {"load_extensions": {'urth_cms_js/editor/main': True}})
    print('Enabling notebook and associated files bundler')
    cm.update('notebook', { 
      'jupyter_cms_bundlers': {
        'notebook_associations_download': {
          'label': 'IPython Notebook bundle (.zip)',
          'module_name': 'urth.cms.nb_bundler',
          'group': 'download'
        }
      }
    })

    print('Installing notebook server extension')
    fn = os.path.join(jupyter_config_dir(), 'jupyter_notebook_config.py')
    with open(fn, 'r+') as fh:
        lines = fh.read()
        if SERVER_EXT_CONFIG not in lines:
            fh.seek(0, 2)
            fh.write('\n')
            fh.write(SERVER_EXT_CONFIG)

class InstallCommand(install):
    def run(self):
        install.run(self)
        _install_notebook_extension()

class DevelopCommand(develop):
    def run(self):
        develop.run(self)
        _install_notebook_extension()

install_requires=[
    'whoosh>=2.7.0, <3.0',
]

# Use the built-in version of scandir if possible, 
# otherwise require the scandir module
try:
    from os import scandir
except ImportError:
    install_requires.append('scandir>=1.1, <2.0')

setup(
    name='jupyter_cms',
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    description='Extension for Jupyter Notebook 4.0.x with experimental content management features',
    long_description = '''
    This package adds the following features to Jupyter Notebook:

* Search dialog on file tree, editor, and notebook screens to search over filenames and .ipynb content in the notebook directory
* IPython kernel extension to make notebooks importable, and notebook cells injectable via # <api> and # <help> annotations
* Full-page drag-and-drop upload target
* Pop-over table of contents navigation for notebooks

See `the project README <https://github.com/jupyter-incubator/contentmanagement>`_
for more information. 
''',   
    url='https://github.com/jupyter-incubator/contentmanagement',
    version=VERSION_NS['__version__'],
    license='BSD',
    platforms=['Jupyter Notebook 4.0.x'],
    packages=[
        'urth', 
        'urth.cms'
    ],
    install_requires=install_requires,
    cmdclass={
        'install': InstallCommand,
        'develop': DevelopCommand,
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)