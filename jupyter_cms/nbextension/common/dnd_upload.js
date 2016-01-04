/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'require',
    'jquery',
    'base/js/utils',
    'base/js/events',
    './notify',
    '../nls/messages'
], function(require, $, utils, events, notify, messages) {

    var exports = {},
        upload_path = '';

    // Build the uploads URL once
    var uploads_url = utils.url_join_encode(utils.get_body_data("baseUrl"), 
        'uploads/');
    
    // Check if external file(s) being dragged.
    var is_file_drag = function(event) {
        if(event.dataTransfer &&  event.dataTransfer.types) {
            var ts = event.dataTransfer.types;
            if(ts.indexOf) {
                // webkit
                return ts.indexOf('Files') !== -1;
            } else if(ts.contains) {
                // firefox
                return ts.contains('Files');
            }
        }        
    };

    // Test if a mouse event occurred outside the client area of the browser 
    // window
    var is_leaving_window = function(e) {
        e = e.originalEvent;
        // Important to include 0,0 for Chrome at the moment
        if(e.clientX <= 0 || e.clientY <= 0) {
            return true;
        } else if(e.clientX > window.innerWidth || e.clientY > window.innerHeight) {
            return true;
        }
        return false;
    };

    // Upload dropped files
    var on_drop_file = function(event) {
        var files = event.dataTransfer.files;
        if(files.length) {
            var fd = new FormData();
            $.each(files, function(i, file) {
                fd.append(file.name, file);
            });

            // Upload to the path
            var url = utils.url_join_encode(uploads_url+encodeURI(upload_path));

            $.ajax({
                url: url,
                type: 'POST',
                contentType: false,
                processData: false,
                data: fd
            }).then(function(resp) {
                var count = resp.files.length;
                notify.show({
                    type: 'success', 
                    text: _.template(messages.upload_success_tmpl)({
                        count: count,
                        path: resp.path
                    })
                });
                events.trigger('urth.upload.complete', resp);
            }, function(xhr) {
                console.warn('upload failed', arguments);
                var text;
                if(xhr.status === 400) {
                    text = messages.upload_failed_type; 
                } else {
                    text = messages.upload_failed_unknown;
                }
                notify.show({
                    type: 'warning', 
                    text: text
                });
                events.trigger('urth.upload.fail', xhr);
            });
        }
    };

    // HACK to allow us to publish drag event when file(s) dragged from
    // desktop onto the page.
    var is_dragging = false;
    $(document).on('dragenter', function(e) {
        if(!is_dragging && is_file_drag(e)) {
            is_dragging = true;
            $view.fadeIn({duration: 250});
        }
    }).on('dragleave', function(e) {
        if(is_dragging && is_file_drag(e) && is_leaving_window(e)) {
            is_dragging = false;
            $view.fadeOut({duration: 250});
        }
    }).on('drop', function(e) {
        if(is_dragging && is_file_drag(e)) {
            is_dragging = false;
            $view.fadeOut({duration: 250});
        }
    });

    // Prevent default behavior of browser redirecting to file that may be
    // dropped onto the page.
    $(window).on('dragover drop', function(e) {
        if (is_file_drag(e)) {
            e.preventDefault();
        }
    });

    // Include dataTransfer on the jQuery event
    $.event.props.push('dataTransfer');

    // Create the overlay and keep it hidden
    var $view = $('<div>')
        .addClass('urth-upload-overlay')
        .css('display', 'none')
        .appendTo('body')
        .on('drop', on_drop_file);
    $('<div>')
        .addClass('urth-upload-overlay-message')
        .text(messages.upload_prompt)
        .appendTo($view);

    // Load the associated stylesheet
    var link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = require.toUrl("./dnd_upload.css");
    document.getElementsByTagName("head")[0].appendChild(link);

    // Set the upload path under which dropped files are stored.
    exports.set_upload_path = function(path) {
        upload_path = path;
    };

    return exports;
});