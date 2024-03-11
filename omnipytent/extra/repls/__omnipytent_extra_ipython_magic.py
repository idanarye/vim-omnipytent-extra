__all__ = [
    'patch_existing_instances'
]

import ast
import sys
from importlib import reload
from types import ModuleType
import re

from IPython.core.magic import register_cell_magic
from IPython import get_ipython


@register_cell_magic
def execute_with_reloading(pattern, code):
    """
    Execute the code after reloading everything ``import``ted in its main namespace

    ``import``s inside functions are not reloaded.
    """
    pattern = re.compile(pattern)
    for imp in ast.parse(code).body:
        if isinstance(imp, ast.Import):
            for name in imp.names:
                if pattern.match(name.name):
                    module = sys.modules.get(name.name)
                    if module is not None:
                        reload(module)
        elif isinstance(imp, ast.ImportFrom):
            parent_module = sys.modules.get(imp.module)
            for name in imp.names:
                fullname = '.'.join((imp.module, name.name))
                if pattern.match(fullname):
                    submodule = sys.modules.get(fullname)
                    if submodule is not None:
                        reload(submodule)
                    elif parent_module is not None and hasattr(parent_module, name.name):
                        reload(parent_module)
                        parent_module = None  # so we won't reload it again

    ip = get_ipython()
    ip.run_cell(code)


def patch_existing_instances(*classes):
    import gc

    for obj in gc.get_objects():
        if not isinstance(obj, type):
            continue
        for cls in classes:
            if obj.__name__ != cls.__name__:
                continue
            if obj.__module__ != cls.__module__:
                continue
            if obj is cls:
                continue
            for k, v in cls.__dict__.items():
                try:
                    setattr(obj, k, v)
                except AttributeError:
                    pass
