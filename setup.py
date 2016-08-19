# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import sys
from setuptools import setup

# Get location of this file at runtime
HERE = os.path.abspath(os.path.dirname(__file__))

# Eval the version tuple and string from the source
VERSION_NS = {}
with open(os.path.join(HERE, 'jupyter_cms', '_version.py')) as f:
    exec(f.read(), {}, VERSION_NS)

install_requires=[
    'notebook>=4.0.0,<5.0',
    'ipython>=4.1.0',
    'whoosh>=2.7.0,<3.0',
]

# Use the built-in version of scandir if possible,
# otherwise require the scandir module
try:
    from os import scandir
except ImportError:
    install_requires.append('scandir>=1.1,<2.0')

setup_args = dict(
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
* Plugin system for deploying and downloading notebook bundles
* Example *IPython Notebook bundle (.zip)* download bundler

See `the project README <https://github.com/jupyter-incubator/contentmanagement>`_
for more information.
''',
    url='https://github.com/jupyter-incubator/contentmanagement',
    version=VERSION_NS['__version__'],
    license='BSD',
    platforms=['Jupyter Notebook 4.0.x', 'Jupyter Notebook 4.1.x', 'Jupyter Notebook 4.2.x'],
    packages=[
        'jupyter_cms'
    ],
    include_package_data=True,
    scripts=[
        'scripts/jupyter-cms',
        'scripts/jupyter-bundler'
    ],
    install_requires=install_requires,
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

if 'setuptools' in sys.modules:
    # setupstools turns entrypoint scripts into executables on windows
    setup_args['entry_points'] = {
        'console_scripts': [
            'jupyter-cms = jupyter_cms.extensionapp:main',
            'jupyter-bundler = jupyter_cms.bundlerapp:main'
        ]
    }
    # Don't bother installing the .py scripts if if we're using entrypoints
    setup_args.pop('scripts', None)

if __name__ == '__main__':
    setup(**setup_args)
