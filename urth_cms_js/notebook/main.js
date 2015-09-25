/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
define([
    'base/js/namespace',
    'base/js/utils',
    '../common/dnd_upload',
    './toc',
    './search'
], function(IPython, utils, upload) {
    // Use the current notebook directory as the upload path
    var segs = utils.url_path_split(IPython.notebook.notebook_path);
    upload.set_upload_path(segs[0]);
});
