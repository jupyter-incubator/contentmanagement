# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
'''
Extended from http://nbviewer.ipython.org/github/ipython/ipython/blob/master/examples/notebooks/Importing%20Notebooks.ipynb.
'''
import io, os, sys, types, re, warnings, hashlib
import nbformat
from nbformat import v4 as nb_v4
from nbformat import reader, converter
from nbconvert.exporters.html import HTMLExporter
from traitlets.config import Config
from IPython.display import display, HTML
from IPython.core.interactiveshell import InteractiveShell

UNBOUND_HELP_DOCSTRING_TMPL = 'Run "{name}()" to see this example. Run "%inject {name}()" to inject the example into your notebook.'
BOUND_HELP_DOCSTRING_TMPL = 'Run this function to see a rich example.'
API_DOCSTRING_TMPL = 'Run {name}.help() for a detailed example.'
MODULE_API_DOCSTRING_TMPL = 'Run help() for a detailed example.'
MODULE_DOCSTRING_TMPL = 'Run this function to see rich help about this importable notebook.'

export_html = HTMLExporter(config=Config({
    'CSSHTMLHeaderPreprocessor': {
        'enabled': False
    },
    'HTMLExporter': {
        'template_file': 'basic'
    }
}))


def rich_help():
    def _rich_help(*args):
        with warnings.catch_warnings():
            # ignore warnings about pandoc, nodejs, etc.
            warnings.filterwarnings('ignore', message='Node.js')
            output, resources = export_html.from_notebook_node(_rich_help.__richdoc__)
        # include style in every output; tried it global on import, but if the import is
        # re-run it's lost because there is no output on a repeat module import
        output = '''<style>
    .output .input_prompt,
    .output .output .output_prompt,
    .output .output .prompt { display: none; }
    .output .input_area pre { padding: 0.4em; }
</style>
''' + output
        display(HTML(output))
    return _rich_help

def convert_notebook(notebook):
    '''Converts IPython notebook to current version.'''
    return converter.convert(notebook, nbformat.current_nbformat)

class NotebookLoader(object):
    '''Module loader for IPython Notebooks with support for rich help.'''
    API_REX = re.compile('#\s*<api>')
    # help annotation acceptable at the start of the cell or on the line
    # immediately below a cell magic
    HELP_REX = re.compile('(%%[^\n]+\n)?(#\s*<help(:([^>]+))?>\s*)')

    def __init__(self, path, nb_path, inject_locals={}):
        self.shell = InteractiveShell.instance()
        self.path = path
        self.nb_path = nb_path
        self.inject_locals = inject_locals

    def create_rich_help_func(self):
        '''
        Build a help renderer with an attached __richdoc__ notebook.
        '''
        nb = nb_v4.new_notebook()
        f = rich_help()
        f.__richdoc__ = nb
        return f

    def attach_richdoc(self, obj, cell, prev, name):
        '''
        Attach a help() function to the object that renders rich help. If obj
        is None, don't attach the help renderer, just return it. In either case,
        append the cell markup and the previous cell (if it's markdown) to the
        help renderer.
        '''
        if obj is None:
            # print 'synthesizing function'
            f = self.create_rich_help_func()
            f.__doc__ = UNBOUND_HELP_DOCSTRING_TMPL.format(name=name)
        elif not hasattr(obj, 'help') and not hasattr(obj, '__richdoc__'):
            # print 'attaching as help'
            f = self.create_rich_help_func()
            if isinstance(obj, type):
                # can't assign __doc__ to methods on class or class itself
                obj.help = classmethod(f)
            else:
                obj.help = f
                tmpl = BOUND_HELP_DOCSTRING_TMPL if name is not None else MODULE_DOCSTRING_TMPL
                obj.help.__doc__ = tmpl.format(name=name)

                tmpl = API_DOCSTRING_TMPL if name is not None else MODULE_API_DOCSTRING_TMPL
                api_doc = tmpl.format(name=name)
                if obj.__doc__ is None:
                    obj.__doc__ = api_doc
                elif not obj.__doc__.endswith(api_doc):
                    obj.__doc__ += '\n' + api_doc
        elif hasattr(obj, '__richdoc__'):
            # print 'appending to synthesized function'
            f = obj
        elif hasattr(obj.help, '__richdoc__'):
            # print 'appending to help'
            f = obj.help
        else:
            raise RuntimeError

        if prev and prev.cell_type == 'markdown':
            f.__richdoc__.cells.append(prev)
        # add this cell to the help notebook if it's non-empty
        if cell.source.strip():
            f.__richdoc__.cells.append(cell)

        return f

    def eval_notebook(self, nb, mod):
        '''
        Evaluate notebook cells.
        '''
        mod.__dict__.update(self.inject_locals)
        prev = None
        if not len(nb.cells):
            # notebook is new and has no cells
            return
        for cell in nb.cells:
            if not mod.__doc__ and cell.cell_type == 'markdown':
                mod.__doc__ = cell.source
            elif cell.cell_type == 'code' and len(cell.source):
                if self.API_REX.match(cell.source):
                    # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(cell.source)
                    # run the code in the module
                    exec(code, mod.__dict__)
                else:
                    match = self.HELP_REX.match(cell.source)
                    if match:
                        # strip the cell input of the help tag marker
                        cell.source = cell.source[:match.start(2)] + cell.source[match.end(2):]
                        name = match.group(4)
                        if name is not None:
                            name = name.strip()
                            try:
                                obj = mod.__dict__[name]
                            except KeyError:
                                # attach to a new named function on the module itself
                                obj = self.attach_richdoc(None, cell, prev, name)
                                mod.__dict__[name] = obj
                            else:
                                # attach to an existing object, assuming that it comes
                                # before the help in the notebook
                                self.attach_richdoc(obj, cell, prev, name)
                        else:
                            # attach to the module itself
                            self.attach_richdoc(mod, cell, prev, name)

            # store previous
            prev = cell

    def load_module(self, fullname):
        '''
        Creates a module containing the exposed API content of a notebook
        by evaluating those notebook cells.
        '''
        # parse the notebook json
        with io.open(self.nb_path, 'r', encoding='utf-8') as f:
            notebook = reader.read(f)
        # convert to current notebook version
        notebook = convert_notebook(notebook)

        # create the module
        mod = types.ModuleType(fullname)
        mod.__file__ = self.nb_path
        mod.__package__ = '.'.join(fullname.split('.')[:-1])
        mod.__loader__ = self
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            self.eval_notebook(notebook, mod)
        finally:
            self.shell.user_ns = save_user_ns
        return mod

    def load_module_by_path(self):
        # parse the notebook json
        with io.open(self.nb_path, 'r', encoding='utf-8') as f:
            notebook = reader.read(f)
        # convert to current notebook version
        notebook = convert_notebook(notebook)

        # create the module and generate a hash from the name
        fullname = hashlib.sha1().hexdigest()
        mod = types.ModuleType(fullname)
        mod.__file__ = self.nb_path
        mod.__package__ = None
        mod.__loader__ = self
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            self.eval_notebook(notebook, mod)
        finally:
            self.shell.user_ns = save_user_ns
        return mod

class BlankPackageLoader(object):
    '''
    Acts like the root of an empty Python package.
    '''
    def __init__(self, path, *args):
        self.path = path

    def load_module(self, fullname):
        mod = types.ModuleType(fullname)
        mod.__path__ = self.path
        mod.__package__ = fullname
        mod.__loader__ = self
        sys.modules[fullname] = mod
        return mod

class NotebookFinder(object):
    '''
    Treats IPython Notebooks as importable modules.
    '''
    def __init__(self, loader_cls):
        self.loader_cls = loader_cls

    def find_module(self, fullname, path=None):
        '''
        Find a notebook, given its fully qualified name and an optional path
        '''
        loader = None
        # print('*** finding fullname:', fullname, 'path:', path)
        if fullname.startswith('mywb.'):
            name = fullname.rsplit('.', 1)[-1]
            path = [''] if path is None or not len(path) else path
            fullpath = os.path.join(*path)

            nb_path = os.path.join(fullpath, name + ".ipynb")
            if os.path.isfile(nb_path):
                loader = self.loader_cls(path, nb_path)
        return loader


class NotebookPathFinder(object):
    '''
    Treats the resources root folder and subdirectories as blank modules.
    '''
    def __init__(self, root, loader_cls):
        self.root = root
        self.loader_cls = loader_cls

    def find_module(self, fullname, ns_path=None):
        if fullname == 'mywb' and ns_path is None:
            # bootstrap the top level fake dir for mywb
            loader = self.loader_cls([self.root])
        elif fullname.startswith('mywb.') and ns_path:
            segs = fullname.split('.')
            path = ns_path._path if hasattr(ns_path, '_path') else ns_path
            fullpath = os.path.join(*(path + segs[-1:]))

            if os.path.isdir(fullpath):
                loader = self.loader_cls([fullpath])
            else:
                loader = None
        else:
            loader = None

        return loader

_enabled = None


def enable(root,
           notebook_path_loader_cls=BlankPackageLoader,
           notebook_loader_cls=NotebookLoader):
    '''
    Adds finders to the sys.meta_path to load Jupyter Notebooks stored
    under the given root path.
    '''
    global _enabled
    if _enabled is None:
        nb_path_finder = NotebookPathFinder(root, notebook_path_loader_cls)
        nb_finder = NotebookFinder(notebook_loader_cls)
        sys.meta_path.append(nb_path_finder)
        sys.meta_path.append(nb_finder)
        _enabled = (nb_path_finder, nb_finder)
    else:
        raise RuntimeError('loader already enabled')


def disable():
    '''
    Removes notebook finders from the sys.meta_path.
    '''
    global _enabled
    if _enabled is not None:
        sys.meta_path.remove(_enabled[0])
        sys.meta_path.remove(_enabled[1])
        _enabled = None
    else:
        raise RuntimeError('loader not enabled')


def load_notebook(path, inject_locals={}):
    '''
    Loads a notebook as a module given its absolute path. Returns a new instance
    of the module every time it is called unlike normal imports which
    sys.modules caches based on name.
    '''
    loader = NotebookLoader([], path, inject_locals=inject_locals)
    return loader.load_module_by_path()
