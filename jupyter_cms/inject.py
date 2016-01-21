# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.display import display, Javascript
import json

@magics_class
class InjectMagic(Magics):
    def _build_injection_js(self, notebook):
        '''
        Creates a series of JS commands to inject code and markdown cells from
        the passed notebook structure into the existing notebook sans output.
        '''
        js = ['var i = IPython.notebook.get_selected_index();']
        i = 0
        for cell in notebook['cells']:
            if cell['cell_type'] == 'markdown':
                js.append("var cell = IPython.notebook.insert_cell_below('markdown', i+{});".format(i))
                escaped_source = json.dumps(cell['source'].strip()).strip('"')
                js.append('cell.set_text("{}");'.format(escaped_source))
                js.append('cell.rendered = false; cell.render();')
                i += 1
            elif cell['cell_type'] == 'code':
                js.append("var cell = IPython.notebook.insert_cell_below('code', i+{});".format(i))
                escaped_input = json.dumps(cell['source'].strip()).strip('"')
                js.append('cell.set_text("{}");'.format(escaped_input))
                i += 1
        js.append('var self = this; setTimeout(function() { self.clear_output(); }, 0);')
        return '\n'.join(js)

    @line_magic
    def inject(self, line):
        '''
        Injects the rich help notebook associated with the named object as
        cells in this notebook.

            import urth.cms
            import mywb.some_notebook as sn
            %inject sn.some_recipe
        '''
        line = line.strip(' ()')
        segs = line.split('.')
        obj = self.shell.user_module
        for seg in segs:
            try:
                obj = getattr(obj, seg)
            except AttributeError:
                return 'Could not locate ' + line
        if hasattr(obj, '__richdoc__'):
            js = self._build_injection_js(obj.__richdoc__)
        elif hasattr(obj, 'help') and hasattr(obj.help, '__richdoc__'):
            js = self._build_injection_js(obj.help.__richdoc__)
        else:
            return 'Injection of the requested object is not yet supported'
        
        display(Javascript(js))
