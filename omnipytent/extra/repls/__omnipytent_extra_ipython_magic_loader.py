# print(__import__('.__omnipytent_extra_ipython_magic'))
__import__('importlib.util').util.spec_from_file_location(
    '__omnipytent_extra_ipython_magic',
    str(__import__('pathlib').Path(__file__).parent / '__omnipytent_extra_ipython_magic.py'),
).loader.load_module()

from __omnipytent_extra_ipython_magic import *
