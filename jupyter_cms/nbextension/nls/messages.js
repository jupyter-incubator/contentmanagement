/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
/* global define */

// TODO: making it a plain module for now which we can convert to requirejs-i18n
// format later
define({
    search_dialog_title: 'Search',
    search_placeholder: 'Enter a search query (e.g., matplo*, plot OR chart)',
    search_query_link: 'Query Help',
    search_hits_tmpl: 'Showing <%= hits %> of <%= total %> matches',
    search_no_hits: 'No matches',
    search_status: 'Indexing and searching ...',

    insert_path: 'Insert Path',
    insert_import: 'Insert Import',

    upload_prompt: 'Drop files to upload',
    upload_failed_type: '<strong>Upload failed:</strong> Content not supported',
    upload_failed_unknown: '<strong>Upload failed:</strong> Unknown error',
    upload_success_tmpl: '<strong>Upload successful:</strong> Saved <%= count %> file(s) in <em><%= path %></em>'
});