/**
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define, JSON */
define([
    'jquery',
    'base/js/namespace',
    'services/config',
], function($, IPython, configmod) {
    'use strict';

    var $deploy_menu,
        $download_menu;

    var do_bundle = function(bundler_id) {
        // Read notebook path and base url here in case they change
        var base_url = IPython.notebook.base_url;
        var path = IPython.notebook.notebook_path;
        var url = (
            location.protocol + '//' +
            location.host +
            base_url +
            'api/bundlers/' + encodeURIComponent(bundler_id) +
            '?notebook=' + encodeURIComponent(path)
        );

        // Have to open new window immediately to avoid popup blockers
        var w = window.open('', IPython._target);
        if (IPython.notebook.dirty) {
            // Delay requesting the bundle until a dirty notebook is saved
            var d = IPython.notebook.save_notebook();
            // https://github.com/jupyter/notebook/issues/618
            if(d) {
                d.then(function() {
                    w.location = url;
                });
            }
        } else {
            w.location = url;
        }
    };

    // Menu groupings we support: Deploy as and Download as
    var groups = { 
        deploy: function() {
            if(!$deploy_menu) {
                var $li = $('<li>')
                    .addClass('dropdown-submenu')
                    .insertAfter('#file_menu .dropdown-submenu:eq(2)');
                $('<a>')
                    .text('Deploy as')
                    .attr('href', '#')
                    .appendTo($li);
                $deploy_menu = $('<ul>')
                    .addClass('dropdown-menu')
                    .appendTo($li);
            }
            return $deploy_menu;
        },
        download: function() {
            if(!$download_menu) {
                $download_menu = $('#download_ipynb').parent();
                $('<li>')
                    .addClass('divider')
                    .appendTo($download_menu);
            }
            return $download_menu;        
        }
    };

    var config = IPython.notebook.config;
    // Get the dictionary of registered bundlers from the notebook config
    config.loaded.then(function() {
        var bundlers = config.data.jupyter_cms_bundlers;
        if(bundlers) {
            for(var bundler_id in bundlers) {
                var bundler = bundlers[bundler_id];
                var group = groups[bundler.group];
                if(!group) {
                    console.warn('unknown group', bundler.group, 'for bundler ID', bundler_id, '; skipping');
                    continue;
                } else if(!bundler.label) {
                    console.warn('no label for bundler ID', bundler_id, '; skipping');
                    continue;
                }
                // New menu item in the right menu that triggers do_bundle
                var $li = $('<li>').appendTo(group());
                $('<a>')
                    .attr('href', '#')
                    .text(bundler.label)
                    .appendTo($li)
                    .on('click', do_bundle.bind(this, bundler_id))
                    .appendTo($li);
            }
        }
    });
});