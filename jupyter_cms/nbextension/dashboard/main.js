/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
define([
    'base/js/namespace',
    'base/js/events',
    '../common/dnd_upload',
    './search',
], function(IPython, events, upload) {
    return {
        load_ipython_extension: function() {
            // Use the current tree directory as the upload path
            upload.set_upload_path(IPython.notebook_list.notebook_path);

            events.on('urth.upload.complete', function() {
                // Refresh file listing
                IPython.notebook_list.load_list();
            });
        }
    };
});
