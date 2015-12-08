# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.utils import url_path_join, url2path
from notebook.base.handlers import IPythonHandler
from notebook.services.config import ConfigManager
from ipython_genutils.importstring import import_item
from tornado import web
import os

class BundlerHandler(IPythonHandler):
    def initialize(self, notebook_dir):
        '''
        :param notebook_dir: Root Notebook working directory
        '''
        self.notebook_dir = notebook_dir

    def get_bundler(self, bundler_id):
        '''
        :param bundler_id: Unique ID within the notebook/jupyter_cms_bundlers
        config section.
        :returns: Dict of bundler metadata with keys label, group, module_name
        :raises KeyError: If the bundler is not registered
        '''
        cm = ConfigManager()
        return cm.get('notebook').get('jupyter_cms_bundlers', {})[bundler_id]

    @web.authenticated
    def get(self, bundler_id):
        '''
        Executes the requested bundler on the given notebook.

        :param bundler_id: Unique ID of an installed bundler
        :arg notebook: Path to the notebook relative to the notebook directory
            root
        '''
        notebook = self.get_query_argument('notebook')
        abs_nb_path = os.path.join(self.notebook_dir, url2path(notebook))
        try:
            bundler = self.get_bundler(bundler_id)
        except KeyError:
            raise web.HTTPError(404, 'Bundler %s not found' % bundler_id)
        try:
            bundler_mod = import_item(bundler['module_name'])
        except ImportError:
            raise web.HTTPError(500, 'Could not import bundler %s ' % bundler_id)

        # Let the bundler respond in any way it sees fit
        bundler_mod.bundle(self, abs_nb_path)

def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'
    bundler_id_regex = r'(?P<bundler_id>[A-Za-z0-9_]+)'
    route_url = url_path_join(web_app.settings['base_url'], '/api/bundlers/%s' % bundler_id_regex)
    web_app.add_handlers(host_pattern, [
        (route_url, BundlerHandler, {'notebook_dir': nb_app.notebook_dir}),
    ])
