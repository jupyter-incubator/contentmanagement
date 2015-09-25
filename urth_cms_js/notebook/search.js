/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'base/js/namespace',
    'base/js/events',
    '../common/search',
    '../common/importer',
    '../common/topics'
], function(IPython, events, search, importer) {
    IPython.keyboard_manager.command_shortcuts.add_shortcut('ctrl-cmd-s', {
        help: 'Show search dialog',
        handler: function(env) {
            search.show_dialog({
                notebook: IPython.notebook,
                keyboard_manager: IPython.notebook.keyboard_manager
            });
        }
    });

    // Add search button (yes, there's a typo in the ID)
    var $toolbar = $('#save-notbook');
    var $search = $('<button>')
        .attr('title', 'Search files')
        .addClass('btn btn-default')
        .on('click', function() {
            search.show_dialog({
                notebook: IPython.notebook,
                keyboard_manager: IPython.notebook.keyboard_manager
            });
        })
        .prependTo($toolbar);
    $('<i>')
        .addClass('fa-search fa')
        .appendTo($search);

    // Insert text at the cursor location within the selected cell
    events.on('urth.paste.text', function(event, args) {
        var cell = IPython.notebook.get_selected_cell();
        if(cell) {
            // CodeMirror's prototype redirects most properties to the editor's
            // document. Make sure there is at least one selection, and replace
            // it/them.
            if (cell.code_mirror && cell.code_mirror.getSelections()) {
                cell.code_mirror.replaceSelection(args.text);
                return;
            } 
            // Fall back on insertion if there's no selection or we can't
            // determine if there's a selection. Line separators may be lost.
            var pre = cell.get_pre_cursor();
            var post = cell.get_post_cursor();
            cell.set_text(pre + args.text + post);
        }
    });

    // Parse file properties and craft an import statement.
    events.on('urth.paste.import', function(event, args) {
        var metadata = IPython.notebook.metadata;
        // Default to pasting the full path if we can't figure out how to
        // build a proper import.
        var content = args.path;
        if(metadata && metadata.kernelspec && metadata.kernelspec.name) {
            var kernel_name = metadata.kernelspec.name.toLowerCase();
            if(kernel_name.startsWith('python')) {
                // Support ipynb imports too for Python
                args.import_ipynb = true;
                content = importer.for_python(args);
            } else if(kernel_name === 'ir') {
                content = importer.for_r(args);
            }
        }
        events.trigger('urth.paste.text', {text: content});
    });
});