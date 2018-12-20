import vim
import re
from subprocess import check_output, SubprocessError
import tempfile
import os

from omnipytent.dsl import task
from omnipytent.execution import ShellCommandExecuter


class Screen(ShellCommandExecuter):
    LINE_RESET = vim.eval(r'nr2char(char2nr("\<C-u>"))')
    CLEAR_TERMINAL = vim.eval(r'nr2char(char2nr("\<C-l>"))')
    LIST_PATTERN = re.compile(r'^\t(.*)?\t\((.*)\)$', re.MULTILINE)

    @classmethod
    def iter(cls):
        try:
            screen_list_output = check_output(['screen', '-list']).decode('utf-8')
        except SubprocessError:
            pass
        else:
            for match in cls.LIST_PATTERN.finditer(screen_list_output):
                yield Screen(match.group(1))

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s(%r)' % (type(self).__name__, self.name)

    def _screen_command(self, command, *args):
        return check_output(['screen', '-S', self.name, '-X', command] + list(args))

    def send_raw(self, text):
        self._screen_command('stuff', '%s%s\r' % (self.LINE_RESET, text))

    def clear_terminal(self):
        self._screen_command('stuff', self.CLEAR_TERMINAL)

    def hardcopy(self, with_scrollback=False):
        f, path = tempfile.mkstemp()
        f = os.fdopen(f)
        try:
            args = ['hardcopy']
            if with_scrollback:
                args.append('-h')
            args.append(path)
            self._screen_command(*args)
            return f.read()
        finally:
            f.close()
            try:
                os.remove(path)
            except OSError:
                pass


@task.options
def choose_screen(ctx):
    ctx.key(lambda s: s.name)
    ctx.preview(lambda s: s.hardcopy())
    for screen in Screen.iter():
        yield screen
