/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'require',
    'jquery',
    'base/js/events'
], function(require, $, events) {
    // container
    var $container = $('<div class="urth-toc">')
        .on('dblclick', function(e) {
            e.stopPropagation();
            localStorage['toc'] = localStorage['toc'] == 1 ? 0 : 1;
            $toc.toggle(50, render_toc);
        })
        .appendTo('body');

    // toggle link
    var $toggle = $('<a class="toggle" href="javascript:">&#x25B2;</a>')
        .on('click', function(e) {
            e.stopPropagation();
            localStorage['toc'] = localStorage['toc'] == 1 ? 0 : 1;
            $toc.toggle(50, render_toc);
        })
        .appendTo($container);

    // links list
    var $toc = $('<ul>')
        .css('display', localStorage['toc'] == 1 ? '' : 'none')
        .appendTo($container);

    // last headers queried
    var $headers;

    // scroll to header
    $toc.on('click', 'a', function(e) {
        e.stopPropagation();
        var $a = $(e.target);
        var i = $a.data('offset');
        var header = $headers.get(i);
        header.scrollIntoView(true);
    });
    $toc.on('click', 'li', function(e) {
        e.stopPropagation();
        var $a = $(e.target).find('a');
        var i = $a.data('offset');
        var header = $headers.get(i);
        header.scrollIntoView(true);
    });

    // retrieve header text only, ignoring any children
    var get_text = function($element) {
        var str = '';
        $element.contents().each(function() {
            if (this.nodeType == 3) {
                str += this.textContent || this.innerText || '';
            }
        });
        return str;
    };

    // rebuild the toc links
    var update_toc = function() {
        $toc.empty();
        $headers = $('#notebook-container :header');
        $headers.each(function(i, header) {
            var $h = $(header);
            var tag = $h.prop('tagName');
            if(tag === 'H5' || tag === 'H6') return;
            var $li = $('<li>').appendTo($toc);
            var $a = $('<a href="javascript:">').appendTo($li);
            $a.text(get_text($h));
            $a.data('offset', i);
            $li.addClass('urth-'+tag.toLowerCase());
        });
    };

    var render_toc = function() {
        if($toc.is(':visible')) {
            $toc.parent().addClass('urth-toc-visible');
        } else {
            $toc.parent().removeClass('urth-toc-visible');
        }
    };

    // update the toc on the best event we have indicating a cell change
    events.on('selected_cell_type_changed.Notebook', function (event, data) { 
        update_toc();
        render_toc();
    });
    
    // load the associated stylesheet
    var link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = require.toUrl("./toc.css");
    document.getElementsByTagName("head")[0].appendChild(link);

    // draw it immediately
    update_toc();
    render_toc();
});