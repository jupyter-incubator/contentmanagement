/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
define([
    'base/js/namespace',
    'base/js/utils',
    '../common/dnd_upload',
    './search'
], function(IPython, utils, upload) {
    return {
        load_ipython_extension: function() {
            // Use the current file directory as the upload path
            var segs = utils.url_path_split(IPython.editor.file_path);
            upload.set_upload_path(segs[0]);
        }
    };
});
