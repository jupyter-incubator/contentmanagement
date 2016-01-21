/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'require',
    'jquery',
    'underscore'
], function(require, $, _) {
    var exports = {};

    var $view = $('<div>').appendTo('body'),
        timer,
        finalized = false,
        CLEAR_NOTICE_TIMEOUT = 2 * 1000,
        time_when_browser_focus_first_got_detected = 0;

    var tmpl = _.template(([
        '<div class="urth-notice alert alert-<%= type %> alert-dismissible fade in" role="alert">',
        '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>',
        '  <%= text %>' +
        '</div>'].join('')));

    // Set a timer to hide the notice once the browser has been in focus for 
    // a period of time.
    var set_timer = function() {
        if(timer) {
            // Reset the timer if a new notice arrives
            clearInterval(timer);
            time_when_browser_focus_first_got_detected = 0;
        }
        timer = setInterval(function() {
            var date = new Date();
            if(!document.hasFocus()) {
                // Reset timer if we've lost focus
                time_when_browser_focus_first_got_detected = 0;
                return;
            } else {
                // First time we've seen the browser get focus, so note it
                if (time_when_browser_focus_first_got_detected === 0) {
                    time_when_browser_focus_first_got_detected = date.getTime();
                }
                if (date.getTime() - time_when_browser_focus_first_got_detected >= CLEAR_NOTICE_TIMEOUT) {
                    // We've seen the browser in focus for greater than the max.
                    clearInterval(timer);
                    timer = null;
                    time_when_browser_focus_first_got_detected = 0;
                    $view.find('.alert').alert('close');
                }
            }
        }, CLEAR_NOTICE_TIMEOUT);
    };

    // Show a notice. Supports these args:
    //   * type - Type of notice, one of the Bootstrap alert types
    //   * text - Text to include in the notice
    //   * permanent - True to make the notice permanent (e.g., a failure)
    exports.show = function(args) {
        if(finalized) return;
        finalized = !!args.permanent;
        $view.html(tmpl(args));
        if(!finalized) {
            set_timer();
        } else {
            clearInterval(timer);
            timer = null;
        }
    };

    // Load the associated stylesheet
    var link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = require.toUrl("./notify.css");
    document.getElementsByTagName("head")[0].appendChild(link);

    return exports;
});