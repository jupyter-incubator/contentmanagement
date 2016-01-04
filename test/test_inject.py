# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import unittest
import jupyter_cms.loader as loader
import jupyter_cms.inject as inject
from os.path import join as pjoin
from os.path import abspath, dirname

JS_FOR_HELP = '''var i = IPython.notebook.get_selected_index();
var cell = IPython.notebook.insert_cell_below('markdown', i+0);
cell.set_text("# A Recipe!");
cell.rendered = false; cell.render();
var cell = IPython.notebook.insert_cell_below('code', i+1);
cell.set_text("print x + y");
var self = this; setTimeout(function() { self.clear_output(); }, 0);'''

JS_FOR_API = '''var i = IPython.notebook.get_selected_index();
var cell = IPython.notebook.insert_cell_below('markdown', i+0);
cell.set_text("# A function!");
cell.rendered = false; cell.render();
var cell = IPython.notebook.insert_cell_below('code', i+1);
cell.set_text("print some_func()");
var self = this; setTimeout(function() { self.clear_output(); }, 0);'''

def spy():
    '''Really lightweight spy for tracking a single function call.'''
    def spy(value):
        assert spy.call is None
        spy.call = value
    spy.call = None
    return spy

class TestInjectMagic(unittest.TestCase):
    def setUp(self):
        loader.enable(pjoin(dirname(abspath(__file__)), 'resources'))

        self.magics = inject.InjectMagic()
        self.magics.shell = spy()

        # purpose driven mocking
        inject.display = lambda x: None
        self.render = inject.Javascript = spy()

    def tearDown(self):
        loader.disable()

    def test_inject_help(self):
        import mywb.test_injectable as mod

        self.magics.shell.user_module = mod
        self.magics.inject('some_recipe')

        self.assertEqual(self.render.call.strip(), JS_FOR_HELP)

    def test_inject_api(self):
        import mywb.test_injectable as mod

        self.magics.shell.user_module = mod
        self.magics.inject('some_func')

        self.assertEqual(self.render.call.strip(), JS_FOR_API)

    def test_inject_bad_path(self):
        import mywb.test_injectable as mod

        self.magics.shell.user_module = mod
        rv = self.magics.inject('a.b.some_func')

        assert 'Could not locate a.b.some_func' == rv
        assert self.render.call is None

    def test_inject_not_exposed(self):
        import mywb.test_injectable as mod

        self.magics.shell.user_module = mod
        rv = self.magics.inject('not_exposed')

        assert 'Could not locate not_exposed' == rv
        assert self.render.call is None

    def test_inject_unsupported(self):
        import mywb.test_injectable as mod

        self.magics.shell.user_module = mod
        rv = self.magics.inject('another_func')

        assert 'Injection of the requested object is not yet supported' == rv
        assert self.render.call is None