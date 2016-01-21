/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'base/js/events',
    'base/js/keyboard',
    'notebook/js/actions',
    '../common/search',
    '../common/importer',
    '../common/topics'
], function(events, keyboard, actions, search, importer) {
    // Create a shortcut manager
    var acts = new actions.init();
    var shortcut_manager = new keyboard.ShortcutManager(undefined, events, acts, {});

    // Create a search dialog hotkey binding
    shortcut_manager.add_shortcut('ctrl-cmd-s', {
        help: 'Show search dialog',
        handler: function(env) {
            search.show_dialog({});
        }
    });

    // Bind keydown to shortcut manager
    $(document).on('keydown', function (event) {
        shortcut_manager.call_handler(event);
    });

    // Insert text as-is into the editor at the cursor location
    var code_mirror = IPython.editor.codemirror;
    events.on('urth.paste.text', function(event, args) {
        code_mirror.replaceSelection(args.text);
    });

    events.on('urth.paste.import', function(event, args) {
        // Default to pasting the full path if we can't figure out how to
        // build a proper import.
        var content = args.path;
        var mode = code_mirror.getMode().name.toLowerCase();
        if(mode === 'python') {
            content = importer.for_python(args);
        } else if(mode === 'r') {
            content = importer.for_r(args);
        }
        code_mirror.replaceSelection(content);
    });
});