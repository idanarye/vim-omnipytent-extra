import os.path


def add_ipython_capabilities(terminal):
    """
    Modify the `send_raw` of the terminal to allow sending multiline commands.
    """
    if getattr(terminal, '_has_ipython_capabilities', None) == add_ipython_capabilities:
        return
    def send_raw(text):
        rows = text.splitlines()
        while rows and (not rows[0] or rows[0].isspace()):
            rows.pop(0)
        if not rows:
            return
        last_row = rows.pop()
        for row in rows:
            terminal.write('\x01%s\x0f\x0e' % row)
        terminal.write('\x01%s\x1b\r' % last_row)
        # terminal.write('\x0f%s\x04\x1b\n' % '\n'.join(rows))
    terminal.send_raw = send_raw
    terminal._has_ipython_capabilities = add_ipython_capabilities


def add_ipython_magic(terminal):
    """
    Load the omnipytent.extra IPython enahancement plugin

    This plugins adds the following to IPythong:

    * ``%%execute_with_reloading``: execute the code after reloading everything
      ``import``ted in its main namespace. ``import``s inside functions are not
      reloaded.
    * ``patch_existing_instances`: call with classes to patch existing instances of them.
    """
    if getattr(terminal, '_has_ipython_magic', None) == add_ipython_magic:
        return
    this_dir, _ = os.path.split(__file__)
    magic_file = os.path.join(this_dir, '__omnipytent_extra_ipython_magic_loader.py')
    terminal.write('%run {}\n'.format(magic_file))
    terminal._has_ipython_magic = add_ipython_magic
