import vim
import shlex

from omnipytent import INPUT_BUFFER


def _findstart_with_shlex(prefix):
    parts = shlex.split(prefix)
    if parts:
        last_part = parts[-1]
        if prefix.endswith(last_part):
            return len(prefix) - len(last_part)
    return len(prefix) + 1


class ShellCmd:
    def __init__(self, filetype='sh'):
        self.filetype = filetype
        self.completions = {}

    def run(self, text):
        return INPUT_BUFFER(
            text,
            filetype=self.filetype,
            complete=self.complete,
            complete_findstart=_findstart_with_shlex,
        )

    def add_flag(self, *flags):
        for flag in flags:
            self.completions[flag] = None

        def register_function(function):
            for flag in flags:
                self.completions[flag] = function

        return register_function

    def _completions_for(self, flag, base):
        function = self.completions.get(flag)
        if not function:
            return
        if callable(function):
            result = function(base)
            if result:
                for item in result:
                    if item.startswith(base):
                        yield item
        elif hasattr(function, '__iter__'):
            for item in function:
                if item.startswith(base):
                    yield item

    def complete(self, base):
        parts = base.split('=', 1)
        if len(parts) == 2:
            flag, argbase = parts
            for item in self._completions_for(flag, argbase):
                yield '%s=%s' % (flag, item)

        row, col = vim.current.window.cursor
        prefix = vim.current.buffer[:row]
        prefix[-1] = prefix[-1][:col] + base
        prefix = '\n'.join(prefix)
        parts = shlex.split(prefix)
        if prefix.endswith(' '):
            parts.append('')
        if 2 <= len(parts):
            for item in self._completions_for(*parts[-2:]):
                yield item

        for flag, function in self.completions.items():
            if flag.startswith(base):
                yield flag
