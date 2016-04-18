# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import errno
import os.path
import sys

from ._version import __version__

from jupyter_core.paths import jupyter_config_dir
from notebook.services.config import ConfigManager
from notebook.nbextensions import (InstallNBExtensionApp, EnableNBExtensionApp, 
    DisableNBExtensionApp, flags, aliases)

try:
    from notebook.nbextensions import BaseNBExtensionApp
    _new_extensions = True
except ImportError:
    BaseNBExtensionApp = object
    _new_extensions = False

from traitlets import Unicode
from traitlets.config.application import catch_config_error
from traitlets.config.application import Application

# Make copies to reuse flags and aliases
INSTALL_FLAGS = {}
INSTALL_FLAGS.update(flags)

INSTALL_ALIASES = {}
INSTALL_ALIASES.update(aliases)
del INSTALL_ALIASES['destination']

def makedirs(path):
    '''
    mkdir -p and ignore existence errors compatible with Py2/3.
    '''
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class ExtensionInstallApp(InstallNBExtensionApp):
    '''Subclass that installs this particular extension.'''
    name = u'jupyter-cms-extension-install'
    description = u'Install the jupyter_cms extension'

    flags = INSTALL_FLAGS
    aliases = INSTALL_ALIASES

    examples = """
        jupyter cms install
        jupyter cms install --user
        jupyter cms install --prefix=/path/to/prefix
        jupyter cms install --nbextensions=/path/to/nbextensions
    """

    destination = Unicode('')

    def _classes_default(self):
        return [ExtensionInstallApp, InstallNBExtensionApp]

    def start(self):
        here = os.path.abspath(os.path.join(os.path.dirname(__file__)))

        self.log.info("Installing jupyter_cms JS notebook extensions")
        self.extra_args = [os.path.join(here, 'nbextension')]
        self.destination = 'jupyter_cms'
        self.install_extensions()


class ExtensionActivateApp(EnableNBExtensionApp):
    '''Subclass that activates this particular extension.'''
    name = u'jupyter-cms-extension-activate'
    description = u'Activate the jupyter_cms extension'

    flags = {}
    aliases = {}

    examples = """
        jupyter cms activate
    """

    def _classes_default(self):
        return [ExtensionActivateApp, EnableNBExtensionApp]

    def enable_server_extension(self, extension):
        '''Enables the server side extension in the user config.'''
        server_cm = ConfigManager(config_dir=jupyter_config_dir())
        
        makedirs(server_cm.config_dir)

        cfg = server_cm.get('jupyter_notebook_config')
        server_extensions = (
            cfg.setdefault('NotebookApp', {})
            .setdefault('server_extensions', [])
        )
        if extension not in server_extensions:
            cfg['NotebookApp']['server_extensions'] += [extension]
        server_cm.update('jupyter_notebook_config', cfg)

    def enable_bundler(self):
        '''Enables the notebook bundler extension.'''
        cm = ConfigManager(parent=self, config=self.config)
        cm.update('notebook', { 
            'jupyter_cms_bundlers': {
                'notebook_associations_download': {
                    'label': 'IPython Notebook bundle (.zip)',
                    'module_name': 'jupyter_cms.nb_bundler',
                    'group': 'download'
                }
            }
        })

    def start(self):
        self.log.info("Activating jupyter_cms notebook server extensions")
        self.enable_server_extension('jupyter_cms')

        self.log.info("Activating jupyter_cms JS notebook extensions")
        self.section = "notebook"
        self.enable_nbextension("jupyter_cms/notebook/main")
        self.section = "tree"
        self.enable_nbextension("jupyter_cms/dashboard/main")
        self.section = "edit"
        self.enable_nbextension("jupyter_cms/editor/main")
        self.enable_bundler()

        self.log.info("Done. You may need to restart the Jupyter notebook server for changes to take effect.")

class ExtensionDeactivateApp(DisableNBExtensionApp):
    '''Subclass that deactivates this particular extension.'''
    name = u'jupyter-cms-extension-deactivate'
    description = u'Deactivate the jupyter_cms extension'

    flags = {}
    aliases = {}

    examples = """
        jupyter cms deactivate
    """

    def _classes_default(self):
        return [ExtensionDeactivateApp, DisableNBExtensionApp]

    def disable_server_extension(self, extension):
        '''Disables the server side extension in the user config.'''
        server_cm = ConfigManager(config_dir=jupyter_config_dir())
        
        makedirs(server_cm.config_dir)

        cfg = server_cm.get('jupyter_notebook_config')
        if ('NotebookApp' in cfg and
            'server_extensions' in cfg['NotebookApp'] and
            extension in cfg['NotebookApp']['server_extensions']):
            cfg['NotebookApp']['server_extensions'].remove(extension)

        server_cm.update('jupyter_notebook_config', cfg)

        server_extensions = (
            cfg.setdefault('NotebookApp', {})
            .setdefault('server_extensions', [])
        )
        if extension in server_extensions:
            cfg['NotebookApp']['server_extensions'].remove(extension)
        server_cm.update('jupyter_notebook_config', cfg)

    def disable_bundler(self):
        '''Disables the notebook bundler extension.'''
        cm = ConfigManager(parent=self, config=self.config)
        cm.update('notebook', { 
            'jupyter_cms_bundlers': {
                'notebook_associations_download': None
            }
        })

    def start(self):
        self.log.info("Deactivating jupyter_cms notebook server extensions")
        self.disable_server_extension('jupyter_cms')

        self.log.info("Deactivating jupyter_cms JS notebook extensions")
        self.section = "notebook"
        self.disable_nbextension("jupyter_cms/notebook/main")
        self.section = "tree"
        self.disable_nbextension("jupyter_cms/dashboard/main")
        self.section = "edit"
        self.disable_nbextension("jupyter_cms/editor/main")
        self.disable_bundler()

        self.log.info("Done. You may need to restart the Jupyter notebook server for changes to take effect.")

class ExtensionQuickSetupApp(BaseNBExtensionApp):
    """Installs and enables all parts of this extension"""
    name = "jupyter cms quick-setup"
    version = __version__
    description = "Installs and enables all features of the jupyter_cms extension"

    def start(self):
        self.argv.extend(['--py', 'jupyter_cms'])
        
        from notebook import serverextensions
        install = serverextensions.EnableServerExtensionApp()
        install.initialize(self.argv)
        install.start()
        from notebook import nbextensions
        install = nbextensions.InstallNBExtensionApp()
        install.initialize(self.argv)
        install.start()
        enable = nbextensions.EnableNBExtensionApp()
        enable.initialize(self.argv)
        enable.start()
        from jupyter_cms import bundlerapp
        enable = bundlerapp.EnableNBBundlerApp()
        enable.initialize(self.argv)
        enable.start()

class ExtensionQuickRemovalApp(BaseNBExtensionApp):
    """Disables and uninstalls all parts of this extension"""
    name = "jupyter cms quick-remove"
    version = __version__
    description = "Disables and removes all features of the jupyter_cms extension"

    def start(self):
        self.argv.extend(['--py', 'jupyter_cms'])
        
        from jupyter_cms import bundlerapp
        enable = bundlerapp.DisableNBBundlerApp()
        enable.initialize(self.argv)
        enable.start()
        from notebook import nbextensions
        enable = nbextensions.DisableNBExtensionApp()
        enable.initialize(self.argv)
        enable.start()
        install = nbextensions.UninstallNBExtensionApp()
        install.initialize(self.argv)
        install.start()
        from notebook import serverextensions
        install = serverextensions.DisableServerExtensionApp()
        install.initialize(self.argv)
        install.start()

class ExtensionApp(Application):
    '''CLI for extension management.'''
    name = u'jupyter_cms extension'
    description = u'Utilities for managing the jupyter_cms extension'
    examples = ""
    
    subcommands = dict()

    if _new_extensions:
        subcommands.update({
            "quick-setup": (
                ExtensionQuickSetupApp,
                "Install and enable everything in the package"
            ),
            "quick-remove": (
                ExtensionQuickRemovalApp,
                "Disable and uninstall everything in the package"
            )
        })
    else:
        subcommands.update(dict(
            install=(
                ExtensionInstallApp,
                "Install the extension"
            ),
            activate=(
                ExtensionActivateApp,
                "Activate the extension"
            ),
            deactivate=(
                ExtensionDeactivateApp,
                "Deactivate the extension"
            ),
        ))
        
    def _classes_default(self):
        classes = super(ExtensionApp, self)._classes_default()

        # include all the apps that have configurable options
        for appname, (app, help) in self.subcommands.items():
            if len(app.class_traits(config=True)) > 0:
                classes.append(app)

    @catch_config_error
    def initialize(self, argv=None):
        super(ExtensionApp, self).initialize(argv)

    def start(self):
        # check: is there a subapp given?
        if self.subapp is None:
            self.print_help()
            sys.exit(1)

        # This starts subapps
        super(ExtensionApp, self).start()

def main():
    ExtensionApp.launch_instance()
