import vim
import shlex

from omnipytent import INPUT_BUFFER


def _findstart_with_shlex(prefix):
    parts = shlex.split(prefix)
    if parts:
        last_part = parts[-1]
        if prefix.endswith(last_part):
            last_part = last_part.split('=', 1)[-1]
            return len(prefix) - len(last_part)
    return len(prefix) + 1


class ShellCmd:
    def __init__(self, filetype='sh'):
        self.filetype = filetype
        self.completions = {}
        self.positional = []

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

        def register_function(source):
            for flag in flags:
                self.completions[flag] = source

        return register_function

    def add_positional(self, source):
        self.positional.append(source)

    def __completions_from(self, source, base):
        if callable(source):
            result = source(base)
        elif hasattr(source, '__iter__'):
            result = source
        else:
            return
        if result:
            for item in result:
                if isinstance(item, dict):
                    if item['word'].startswith(base):
                        yield item
                else:
                    if item.startswith(base):
                        yield item

    def complete(self, base):
        row, col = vim.current.window.cursor
        prefix = vim.current.buffer[:row]
        prefix[-1] = prefix[-1][:col]
        prefix = '\n'.join(prefix)
        parts = shlex.split(prefix)
        if parts:
            flag = parts[-1]
            if flag.endswith('='):
                flag = flag[:-1]
            source = self.completions.get(flag)
            if source is not None:
                for item in self.__completions_from(source, base):
                    yield item
                return

        for source in self.positional:
            for item in self.__completions_from(source, base):
                yield item

        for flag in self.completions.keys():
            if flag.startswith(base):
                yield flag
