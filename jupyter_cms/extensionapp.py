# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import errno
import os.path
import sys

from jupyter_core.paths import jupyter_config_dir
from notebook.services.config import ConfigManager
from notebook.nbextensions import (InstallNBExtensionApp, EnableNBExtensionApp, 
    DisableNBExtensionApp, flags, aliases)
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

        self.log.info("Done. You may need to restart the Jupyter notebook server for changes to take effect.")

class ExtensionDeactivateApp(DisableNBExtensionApp):
    '''Subclass that deactivates this particular extension.'''
    name = u'nbgrader-extension-deactivate'
    description = u'Deactivate the nbgrader extension'

    flags = {}
    aliases = {}

    examples = """
        nbgrader extension deactivate
    """

    def _classes_default(self):
        return [ExtensionDeactivateApp, DisableNBExtensionApp]

    # def _recursive_get(self, obj, key_list):
    #     if obj is None or len(key_list) == 0:
    #         return obj
    #     return self._recursive_get(obj.get(key_list[0], None), key_list[1:])

    def disable_server_extension(self, extension):
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

        self.log.info("Done. You may need to restart the Jupyter notebook server for changes to take effect.")

class ExtensionApp(Application):

    name = u'jupyter_cms extension'
    description = u'Utilities for managing the jupyter_cms extension'
    examples = ""

    subcommands = dict(
        install=(
            ExtensionInstallApp,
            "Install the extension."
        ),
        activate=(
            ExtensionActivateApp,
            "Activate the extension."
        ),
        deactivate=(
            ExtensionDeactivateApp,
            "Deactivate the extension."
        )
    )

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
