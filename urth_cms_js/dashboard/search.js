/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'base/js/events',
    'base/js/keyboard',
    'notebook/js/actions',
    '../common/search'
], function(events, keyboard, actions, search) {
    // Create a shortcut manager
    var acts = new actions.init();
    var shortcut_manager = new keyboard.ShortcutManager(undefined, events, acts, {});

    // Create a search dialog hotkey binding
    shortcut_manager.add_shortcut('ctrl-cmd-s', {
        help: 'Show search dialog',
        handler: function(env) {
            // Show search dialog without insert actions
            search.show_dialog({can_insert: false});
        }
    });

    // Bind keydown to shortcut manager
    $(document).on('keydown', function (event) {
        shortcut_manager.call_handler(event);
    });

    // Add search button
    var $toolbar = $('.tree-buttons').find('.pull-right');
    $('<button>')
        .attr('title', 'Search files')
        .addClass('btn btn-default btn-xs')
        .text('Search')
        .on('click', function() {
            search.show_dialog({can_insert: false});
        })
        .prependTo($toolbar);
});