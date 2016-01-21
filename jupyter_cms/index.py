# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from jupyter_core.paths import jupyter_data_dir
from whoosh.index import create_in, open_dir, exists_in, LockError
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.query import AndMaybe, Term
from whoosh.qparser import MultifieldParser
import nbformat
import io
import os
import json
import shutil

# Use the built-in version of scandir if possible, otherwise
# use the scandir module version
try:
    from os import scandir
except ImportError:
    from scandir import scandir

class Index(object):
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self._init_index()
        
    def _init_index(self, reset=False):
        index_path = os.path.join(jupyter_data_dir(), 'index')
        
        # clear out old index if requested
        if reset:
            shutil.rmtree(index_path, True)
        
        # make sure there's a path to store the index data
        if not os.path.exists(index_path):
            os.makedirs(index_path)
            
        if not exists_in(index_path):
            # create an index with the current schema
            schema = Schema(basename=TEXT(stored=True, field_boost=5.0), 
                            dirname=ID(stored=True),
                            path=ID(stored=True, unique=True), 
                            content=TEXT(stored=False), 
                            time=STORED)
            self.ix = create_in(index_path, schema)
        else:
            # open the existing index
            self.ix = open_dir(index_path)
            
        # build a query parser based on the current schema
        self.query_parser = MultifieldParser(["content", "basename", "dirname"], self.ix.schema)
    
    def _file_to_document(self, filename, m_time):
        content = u''
        
        # get content for notebooks only
        if filename.endswith('.ipynb'):
            with io.open(filename, 'r', encoding='utf-8') as f:
                try:
                    notebook = nbformat.read(f, 4)
                    content = u'\n'.join(cell.get('source', u'') for cell in notebook['cells'])
                except (Exception):
                    pass
        return dict(
            basename=os.path.basename(filename),
            dirname=os.path.dirname(filename),
            path=filename,
            content=content,
            time=m_time
        )
    
    def _scan_disk(self, on_disk, path):
        for entry in scandir(path):
            if not entry.name.startswith('.') and entry.is_dir():
                self._scan_disk(on_disk, entry.path)
            elif entry.is_file():
                on_disk[entry.path] = entry.stat().st_mtime
        return on_disk
                
    def _scan_index(self):
        in_index = {}
        with self.ix.searcher() as searcher:
            for fields in searcher.all_stored_fields():
                in_index[fields['path']] = fields['time']
        return in_index
                
    def _compute_ops(self, on_disk, in_index):
        in_index_set = set(in_index.keys())
        on_disk_set = set(on_disk.keys())

        to_remove = in_index_set - on_disk_set
        to_add = on_disk_set - in_index_set
        to_update = on_disk_set.intersection(in_index_set)
        
        return to_add, to_remove, to_update
        
    def _add_to_index(self, writer, to_add, on_disk):
        for filename in to_add:
            meta = self._file_to_document(filename, on_disk[filename])
            writer.add_document(**meta)
        
    def _remove_from_index(self, writer, to_remove):
        for filename in to_remove:
            writer.delete_by_term('path', filename)
            
    def _update_in_index(self, writer, to_update, on_disk, in_index):
        for filename in to_update:
            # only update if modification time differs
            if on_disk[filename] == in_index[filename]:
                continue
            meta = self._file_to_document(filename, on_disk[filename])
            writer.update_document(**meta)
    
    def update_index(self):
        '''
        Updates the index based on the disk/index delta.
        '''
        on_disk = {}
        on_disk = self._scan_disk(on_disk, self.work_dir)
        in_index = self._scan_index()
        to_add, to_remove, to_update = self._compute_ops(on_disk, in_index)
        
        #print(len(to_add), len(to_remove), len(to_update)) 
        
        try:
            writer = self.ix.writer()
        except LockError:
            # skip index updates: locked by another process
            pass
        else:
            self._add_to_index(writer, to_add, on_disk)
            self._remove_from_index(writer, to_remove)
            self._update_in_index(writer, to_update, on_disk, in_index)
            writer.commit()

    def search(self, query_string, limit=25, cwd=os.getcwd()):
        '''
        Searches the index given a query string.
        '''
        with self.ix.searcher() as searcher:
            # parse user query
            query = self.query_parser.parse(query_string)
            # improve the score of files in the same directory
            query = AndMaybe(query, Term('dirname', cwd))
            results = searcher.search(query, limit=limit)
            # return dict copies: results not valid outside of context
            return ([dict(
                basename=result['basename'],
                dirname=result['dirname'],
                path=result['path']
            ) for result in results], len(results))

    def reset_index(self):
        '''
        Clears the search index.
        '''
        self._init_index(True)
