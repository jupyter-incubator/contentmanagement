# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from .index import Index
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from tornado import web
import os

class SearchHandler(IPythonHandler):
    def initialize(self, work_dir):
        self.index = Index(work_dir)
        self.work_dir = work_dir
        self.work_dir_len = len(self.work_dir)+1

    @web.authenticated
    def get(self):
        query_string = self.get_query_argument('qs')
        reindex = bool(self.get_query_argument('reindex', 'true') == 'true')

        if reindex:
            self.index.update_index()

        results, total = self.index.search(query_string)

        for result in results:
            rel_path = result['path'][self.work_dir_len:]
            if rel_path.endswith('.ipynb'):
                # take it at face value that the extension implies notebook
                url = url_path_join(self.base_url, 'notebooks', rel_path)
            else:
                url = url_path_join(self.base_url, 'edit', rel_path)
            # Add URLs
            result['url'] = url
            result['tree_url'] = url_path_join(self.base_url, 'tree', os.path.dirname(rel_path))
            # Add relative paths
            result['rel_dirname'] = os.path.dirname(rel_path)
            result['rel_path'] = rel_path
        
        self.write(dict(results=results, total=total))
        self.finish()

def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/search')
    handler_kwargs = dict(work_dir=nb_app.notebook_dir)
    web_app.add_handlers(host_pattern, [
        (route_pattern, SearchHandler, handler_kwargs)
    ])
