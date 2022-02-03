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


class ShellCmd(INPUT_BUFFER):
    def __init__(
        self,
        text=None,
        filetype='sh',
    ):
        super(ShellCmd, self).__init__(
            text=text,
            filetype=filetype,
            complete=self.complete,
            complete_findstart=_findstart_with_shlex,
        )
        self._completions = {}
        self._positional = []

    def add_flag(self, *flags):
        for flag in flags:
            self._completions[flag] = None

        def register_function(source):
            for flag in flags:
                self._completions[flag] = source

        return register_function

    def add_positional(self, source):
        self._positional.append(source)

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
            source = self._completions.get(flag)
            if source is not None:
                for item in self.__completions_from(source, base):
                    yield item
                return

        for source in self._positional:
            for item in self.__completions_from(source, base):
                yield item

        for flag in self._completions.keys():
            if flag.startswith(base):
                yield flag

    def invoke_registered_command(self, command_name):
        pass
