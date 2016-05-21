# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import unittest
import jupyter_cms.loader as loader
from os.path import join as pjoin
from os.path import abspath, dirname

def spy():
    '''Really lightweight spy for tracking a single function call.'''
    def spy(value):
        if spy.call is not None:
            raise RuntimeError('spy already called')
        spy.call = value
    spy.call = None
    return spy

class TestNotebookPathFinder(unittest.TestCase):
    '''Tests for traversing paths within the loader root directory.'''
    def setUp(self):
        self.root = pjoin(dirname(abspath(__file__)), 'resources')
        loader.enable(self.root)

    def tearDown(self):
        loader.disable()

    def test_mywb_module(self):
        '''Should import the root as an empty module.'''
        import mywb as mod
        self.assertEqual(mod.__name__, 'mywb')
        self.assertEqual(mod.__package__, mod.__name__)
        self.assertEqual(mod.__path__, [self.root])

    def test_mywb_subdir_submodule(self):
        '''Should import subdirectories as empty packages.'''
        import mywb.subdir as mod
        self.assertEqual(mod.__name__, 'mywb.subdir')
        self.assertEqual(mod.__package__, mod.__name__)
        # print(dir(mod.__path__))
        # self.assertEqual(str(mod.__path__), [os.path.join(self.root, 'subdir')])

        import mywb.subdir.subsubdir as mod
        self.assertEqual(mod.__name__, 'mywb.subdir.subsubdir')
        self.assertEqual(mod.__package__, mod.__name__)
        # assert mod.__path__ == [os.path.join(self.root, 'subdir', 'subdir2')]

    def test_mywb_subdir_not_found(self):
        '''Should fail to import non-existent subdirectories.'''
        try:
            import mywb.subdir2
        except ImportError:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')

        try:
            import mywb.fake
        except ImportError:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')

    def test_normal_packages(self):
        '''Should import normal packages as before.'''
        import xml
        import xml.dom
        import xml.dom.minidom

class TestNotebookFinder(unittest.TestCase):
    '''Tests for traversing notebooks within the loader root directory.'''
    def setUp(self):
        self.root = pjoin(dirname(abspath(__file__)), 'resources')
        loader.enable(self.root)

    def tearDown(self):
        loader.disable()

    def test_mywb_notebook(self):
        '''Should import a notebook as a module.'''
        import mywb.test_injectable as mod
        self.assertEqual(mod.__name__, 'mywb.test_injectable')
        self.assertEqual(mod.__package__, 'mywb')

    def test_mywb_subdir_notebook(self):
        '''Should import a notebook in a subdir as a module.'''
        import mywb.subdir.test_injectable as mod
        self.assertEqual(mod.__name__, 'mywb.subdir.test_injectable')
        self.assertEqual(mod.__package__, 'mywb.subdir')

    def test_notebook_not_found(self):
        '''Should fail to import non-existent notebooks.'''
        try:
            import kawb.not_help
        except ImportError:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')

        try:
            import mywb.not_help
        except ImportError:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')

    def test_general_not_found(self):
        '''Should fail import non-existent modules as before.'''
        try:
            import not_found
        except ImportError:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')
            
    def test_cwd_notebook(self):
        '''Should not import a notebook in the cwd.'''
        # switch to resources so that notebook are in the cwd
        path = os.getcwd()
        os.chdir(self.root)        
        try:
            import test_injectable as mod
        except ImportError as e:
            pass
        else:
            self.assertTrue(False, 'expected ImportError')
        finally:
            os.chdir(path)
            

class TestNotebookLoader(unittest.TestCase):
    '''Tests for loading notebooks within the loader root directory.'''
    def setUp(self):
        self.root = pjoin(dirname(abspath(__file__)), 'resources')
        loader.enable(self.root)

    def tearDown(self):
        loader.disable()

    def test_mywb_notebook(self):
        '''Should import a notebook as a module with a top level help().'''
        import mywb.test_injectable as mod

        self.assertEqual(mod.__name__, 'mywb.test_injectable')
        self.assertEqual(mod.__file__, os.path.join(self.root, 'test_injectable.ipynb'))
        self.assertEqual(mod.__package__, 'mywb')

        self.assertTrue(hasattr(mod, 'help'))
        self.assertTrue(callable(mod.help))

    def test_mywb_empty_notebook(self):
        '''Should import an empty notebook as an empty module.'''
        import mywb.empty as mod

        self.assertEqual(mod.__name__, 'mywb.empty')
        self.assertEqual(mod.__file__, os.path.join(self.root, 'empty.ipynb'))
        self.assertEqual(mod.__package__, 'mywb')

    def test_mywb_subdir_notebook(self):
        '''Should import a notebook in a subdir as a module with a top level help().'''
        import mywb.subdir.test_injectable as mod

        self.assertEqual(mod.__name__, 'mywb.subdir.test_injectable')
        self.assertEqual(mod.__file__, os.path.join(self.root, 'subdir/test_injectable.ipynb'))
        self.assertEqual(mod.__package__, 'mywb.subdir')

        self.assertTrue(hasattr(mod, 'help'))
        self.assertTrue(callable(mod.help))

    def test_load_by_path(self):
        '''Should import a notebook as a module using a function instead of import.'''
        for path in [
            os.path.join(self.root, 'test_injectable.ipynb'),
            os.path.join(self.root, 'subdir', 'test_injectable.ipynb')
        ]:
            mod = loader.load_notebook(path)
            self.assertTrue(mod.__name__)
            self.assertEqual(mod.__file__, path)
            self.assertEqual(mod.__package__, None)

class TestNotebookExposure(unittest.TestCase):
    '''Tests for APIs exposed by loaded notebooks.'''
    def setUp(self):
        self.root = pjoin(dirname(abspath(__file__)), 'resources')
        loader.enable(self.root)

        # purpose driven mocking
        loader.display = lambda x: None
        self.render = loader.HTML = spy()

    def tearDown(self):
        loader.disable()

    def test_module_help(self):
        '''Should return rich help.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.help))
        self.assertEqual(mod.help.__doc__, loader.MODULE_DOCSTRING_TMPL)
        self.assertTrue(mod.__doc__.endswith(loader.MODULE_API_DOCSTRING_TMPL))
        mod.help()
        self.assertIn('Fake Module!', self.render.call)
        self.assertNotIn('help', self.render.call)

    def test_api(self):
        '''Should expose a notebook function as a module function.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.some_func))
        self.assertIn('existing docstring', mod.some_func.__doc__)
        self.assertTrue(mod.some_func.__doc__.endswith(loader.API_DOCSTRING_TMPL.format(name='some_func')))
        self.assertEqual(mod.some_func(), 'fake-return')

    def test_api_help(self):
        '''Should expose a help method on a notebook function.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.some_func.help))
        self.assertEqual(mod.some_func.help.__doc__, loader.BOUND_HELP_DOCSTRING_TMPL)
        mod.some_func.help()
        self.assertIn('A function!', self.render.call)
        self.assertIn('some_func', self.render.call)
        self.assertIn('fake-return', self.render.call)
        self.assertNotIn('help', self.render.call)

    def test_class_api_help(self):
        '''Should expose a help method on a notebook class.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.SomeClass.help))
        mod.SomeClass.help()
        self.assertIn('SomeClass', self.render.call)
        self.assertIn('some_method', self.render.call)
        self.assertIn('True', self.render.call)

    def test_recipe_help(self):
        '''Should expose cell contents as a help recipe.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.some_recipe))
        self.assertFalse(hasattr(mod.some_recipe, 'help'))
        self.assertEqual(mod.some_recipe.__doc__, loader.UNBOUND_HELP_DOCSTRING_TMPL.format(name='some_recipe'))
        mod.some_recipe()
        self.assertIn('A Recipe!', self.render.call)
        self.assertIn('print', self.render.call)
        self.assertIn('fake-output', self.render.call)
        self.assertNotIn('help', self.render.call)

    def test_magic_recipe_help(self):
        '''Should expose cell contents with a cell magic prefix as a help recipe.'''
        import mywb.test_injectable as mod
        self.assertTrue(callable(mod.r_recipe))
        self.assertFalse(hasattr(mod.r_recipe, 'help'))
        self.assertEqual(mod.r_recipe.__doc__, loader.UNBOUND_HELP_DOCSTRING_TMPL.format(name='r_recipe'))
        mod.r_recipe()
        self.assertIn('X', self.render.call)
        self.assertIn('1,2,3', self.render.call)
        self.assertIn(r'%%', self.render.call)
        self.assertNotIn('help', self.render.call)
