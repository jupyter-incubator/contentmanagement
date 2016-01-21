/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
 /* global define */
define([
    'base/js/events'
], function(events) {
    var trigger = function(event) {
        var $trigger = $(event.currentTarget);
        event.preventDefault();

        var topic = $trigger.data('topic');

        // Gather all data attributes and publish as topic value
        var data = $trigger.data();
        delete data['topic'];
        events.trigger(topic, data);
    };
    
    $(document).on('click', '[data-topic]', trigger);
    $(document).on('keydown', '[data-topic]', function(event) {
        if(event.keyCode == 13) {
            trigger(event);
        }
    });
});