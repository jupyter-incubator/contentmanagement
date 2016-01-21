# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.utils import url_path_join, url_unescape
from notebook.base.handlers import IPythonHandler, path_regex
from tornado import web
import os

class UploadsHandler(IPythonHandler):
    def initialize(self, work_dir):
        self.work_dir = work_dir

    @web.authenticated
    def post(self, path):
        '''
        Write uploaded files to disk.

        :param path:
        '''
        files = self.request.files
        if not len(files):
            raise web.HTTPError(400, 'missing files to upload')
        root_path = os.path.join(self.work_dir, path.strip('/'))
        written_paths = []
        for filename, metas in files.items():
            path = url_unescape(os.path.join(root_path, filename))
            with open(path, 'wb') as fh:
                fh.write(metas[0].body)
            written_paths.append(path)
        self.finish({
            'files' : written_paths,
            'path' : url_unescape(root_path)
        })

def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], 
        '/uploads%s' % path_regex)
    handler_kwargs = dict(work_dir=nb_app.notebook_dir)
    web_app.add_handlers(host_pattern, [
        (route_pattern, UploadsHandler, handler_kwargs)
    ])
