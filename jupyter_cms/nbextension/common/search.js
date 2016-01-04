/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'require',
    'jquery',
    'underscore',
    'base/js/dialog',
    'base/js/utils',
    'base/js/keyboard',
    '../nls/messages'
], function(require, $, _, dialog, utils, keyboard, messages) {
    var exports = {};

    // Constants
    var template = _.template([
        '<input type="text" class="form-control urth-search-input" placeholder="<%= messages.search_placeholder %>" />',
        '<div class="urth-search-input-help">',
        '  <a href="http://whoosh.readthedocs.org/en/latest/querylang.html" target="_blank"><%= messages.search_query_link %> ',
        '    <i class="fa fa-external-link"></i>',
        '  </a>',
        '</div>',
        '<div class="urth-search-summary text-muted"></div>',
        '<div class="urth-search-results"></div>'
    ].join(''));
    var search_url = utils.url_join_encode(utils.get_body_data("baseUrl"), 'search');

    // Configuration
    var can_insert;
        
    // Search response handler that populates the dialog
    var on_result = function(resp) {
        var $results = $('.urth-search-results');

        if(resp.total === 0) {
            $('.urth-search-summary').text(messages.search_no_hits);
            return;
        }

        var results = resp.results;
        $('.urth-search-summary')
            .text(_.template(messages.search_hits_tmpl)({
                hits: results.length,
                total: resp.total
            }));

        for(var i=0; i < results.length; i++) {
            var result = results[i];
            var $row = $('<div>')
                .addClass('row urth-search-result-row')
                .appendTo($results);
            $('<div>')
                .addClass('col-xs-1')
                .text((i+1)+'.')
                .appendTo($row);
            var $info = $('<div>')
                .addClass('col-xs-11')
                .appendTo($row);
            var $first = $('<div>').appendTo($info);
            $('<a>')
                .attr('href', result.url)
                .attr('target', '_blank')
                .text(result.basename)
                .appendTo($first);
            var $actions = $('<span>')
                .addClass('urth-search-result-actions urth-search-result-location')
                .text(' in ')
                .appendTo($first);
            $('<a>')
                .attr('href', result.tree_url)
                .attr('target', '_blank')
                .text(result.rel_dirname + '/')
                .appendTo($actions);

            var $second = $('<div>').appendTo($info);
            $actions = $('<span>')
                .addClass('urth-search-result-actions')
                .appendTo($second);
            if(can_insert) {
                $('<a>')
                    .attr('href', 'javascript:void(0);')
                    .attr('data-topic', 'urth.paste.text')
                    .attr('data-text', result.path)
                    .text(messages.insert_path)
                    .appendTo($actions);
                $('<span>').html(' &#8226; ').appendTo($actions);
                $('<a>')
                    .attr('href', 'javascript:void(0);')
                    .attr('data-topic', 'urth.paste.import')
                    .attr('data-path', result.path)
                    .attr('data-rel-path', result.rel_path)
                    .text(messages.insert_import)
                    .appendTo($actions);
            }
        }
    };

    // Search error handler that shows an brief error message in the dialog
    var on_error = function() {
        $('.urth-search-summary').text('Error fetching results');
    };

    // Register a listener once for keypress on the search input
    $(document).on('keyup', '.urth-search-input', function(event) {
        if(event.keyCode === keyboard.keycodes.enter) {
            var text = $.trim($(event.target).val());
            $('.urth-search-summary').text(messages.search_status);
            $('.urth-search-results').empty();
            localStorage['urth.last_query_string'] = text;
            $.ajax({
                url: search_url,
                data: {qs: text},
                dataType: 'json'
            }).then(on_result, on_error);
        }
    });

    // Show the search dialog.
    // Options:
    //      * notebook: Instance of notebook over which to show the dialog
    //      * keyboard_manager: Keyboard manager for the notebook
    //      * can_insert: Show insertion action links for results
    exports.show_dialog = function(args) {
        // Prevent overlapping dialogs
        if($('.urth-search-input').length) return;

        can_insert = args.can_insert === undefined ? true : args.can_insert;
        var dlg = dialog.modal({
            title: messages.search_dialog_title,
            body: template({messages: messages}),
            sanitize: false,
            keyboard_manager: args.keyboard_manager,
            notebook: args.notebook,
            open: function() {
                $('.urth-search-input').focus();
                var qs = localStorage['urth.last_query_string'];
                if(qs) {
                    $('.urth-search-input').val(qs).select();
                }
                delete localStorage['urth.last_query_string'];
            }
        });
        // Let content area take focus so key capture works
        dlg.find('.modal-content').attr('tabindex', '0');
    };

    // Load the associated stylesheet
    var link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = require.toUrl("./search.css");
    document.getElementsByTagName("head")[0].appendChild(link);

    return exports;
});