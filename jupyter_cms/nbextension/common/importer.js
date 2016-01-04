/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */
define([
    'underscore',
], function(_) {
    // Regular expressions for valid Python identifiers
    var valid_module_regex = /^[a-zA-Z_][a-zA-Z0-9_]*$/;
    var first_char_regex = /[a-zA-Z_]/;
    var other_char_replace = /[^a-zA-Z0-9_]/g;
    var exports = {};

    exports.for_python = function(args) {
        // Compute resource path segments
        var path_segs = args.relPath.split('/');
        // Chop off the file name extension of file being imported
        var parts = path_segs[path_segs.length-1].split('.');
        var name = parts[0];
        var ext = (parts[parts.length-1] || '').toLowerCase();
        path_segs[path_segs.length-1] = name;

        // Check if all path segments are valid python identifiers
        var valid_module = _.every(path_segs, function(seg) {
            return valid_module_regex.test(seg);
        });

        var code;
        if(ext === 'ipynb' && args.import_ipynb) {
            // Treat as importable notebook
            if(valid_module) {
                // use import syntax
                code = 'import mywb.' + path_segs.join('.') + ' as ' + name.toLowerCase();
            } else {
                // use API syntax
                if(!first_char_regex.test(name[0])) {
                    name[0] = '_';
                }
                name = name.replace(other_char_replace, '_');
                // use the absolute path in this case
                code = name.toLowerCase() +' = load_notebook(\'' + args.path + '\')';
            }
        }
        else if(ext === 'py') {
            // Treat as normal python import statement
            code = 'import ' + path_segs.join('.') + ' as ' + name.toLowerCase();
        }
        else {
            // This seems illogical, so let the user know in a nice way
            code = '# Are you sure you wanted to import the file ' +  parts.join('.') +
                '?\nimport ' + parts.join('.') + ' as ' + name.toLowerCase();
        }

        return code;
    };

    exports.for_r = function(args) {
        // Compute resource path segments
        var path_segs = args.relPath.split('/');
        // Split file name of resource being imported
        var name_parts = path_segs[path_segs.length-1].split('.');
        var ext = name_parts[name_parts.length-1] || '';

        if(ext.toLowerCase() === 'r') {
            // Source .R files
            code = 'source("' + name_parts.join('.') + '")';
        } else {
            // This seems illogical
            code = '# Are you sure you wanted to source the file ' + name_parts.join('.') + 
                '?\nsource("' + name_parts.join('.') + '")';
        }

        return code;
    };

    return exports;
});