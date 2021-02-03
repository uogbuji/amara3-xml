import pytest
import os, inspect

def module_path(local_function):
    '''
    returns the module path without the use of __file__.  Requires a function defined locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    '''
    return os.path.abspath(inspect.getsourcefile(local_function))


# Locate test resource (data) files regardless of from where pytest was run
# Warning: requires all tests to be grandchildren of the test dir
@pytest.fixture
def testresourcepath():
    return os.path.normpath(os.path.join(
        module_path(lambda _: None), '../resource/'))

