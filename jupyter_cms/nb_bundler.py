# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import io
import zipfile

def bundle(handler, abs_nb_path):
    '''
    Creates a zip file containing the original notebook, a Dockerfile, and a 
    README explaining how to build the bundle. Does not automagically determine
    what base image, kernels, or libraries the notebook needs (yet?). Has the 
    handler respond with the zip file.
    '''
    # Notebook basename with and without the extension
    notebook_filename = os.path.basename(abs_nb_path)
    notebook_name = os.path.splitext(notebook_filename)[0] 

    # Headers
    zip_filename = os.path.splitext(notebook_name)[0] + '.zip'
    handler.set_header('Content-Disposition',
                       'attachment; filename="%s"' % zip_filename)
    handler.set_header('Content-Type', 'application/zip')

    # Get associated files
    ref_filenames = handler.tools.get_file_references(abs_nb_path, 4)

    # Prepare the zip file
    zip_buffer = io.BytesIO()
    zipf = zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED)
    zipf.write(abs_nb_path, notebook_filename)

    notebook_dir = os.path.dirname(abs_nb_path)
    for nb_relative_filename in ref_filenames:
        # Build absolute path to file on disk
        abs_fn = os.path.join(notebook_dir, nb_relative_filename)
        # Store file under path relative to notebook 
        zipf.write(abs_fn, nb_relative_filename)

    zipf.close()

    # Return the buffer value as the response
    handler.finish(zip_buffer.getvalue())
