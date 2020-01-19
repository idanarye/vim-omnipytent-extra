import vim
import re
import os
from subprocess import check_output

from . import TargetTest, find_line_above

class PytestTest(TargetTest):
    BASE_COMMAND = 'py.test'
    COLLECT_ONLY_PATTERN = re.compile(r'''^\s*<(Package|Module|Function) (.*)>$''', re.MULTILINE)
    TEST_LINE_PATTERN = re.compile(r'^(\s*)def (test\w*).*[:,(]\s*$')
    CLASS_LINE_PATTERN = re.compile(r'^class (Test\w*).*:')
    ROOT_DIR_PATTERN = re.compile(r'^rootdir: (.*)(?:, inifile:.*)?$', re.MULTILINE)

    def __init__(self, filename, function):
        self.filename = filename
        self.function = function

    def __str__(self):
        return '%s::%s' % (self.filename, self.function)

    def __repr__(self):
        return '%s(filename=%r, function=%r)' % (type(self).__name__, self.filename, self.function)

    @property
    def shortname(self):
        return '%s::%s' % (os.path.basename(self.filename), self.function)

    @classmethod
    def find_at(cls, path):
        package = None
        filename = None
        command_parts = [cls.BASE_COMMAND, '--collect-only', path]
        pytest_collect_output = check_output(command_parts).decode('utf-8')
        rootdir = cls.ROOT_DIR_PATTERN.search(pytest_collect_output).group(1)
        for m in cls.COLLECT_ONLY_PATTERN.finditer(pytest_collect_output):
            kind, name = m.groups()
            if name and name[0] == name[-1] and name[0] in ('"', "'"):
                name = name[1:-1]
            if kind == 'Package':
                package = name
                filename = None
            elif kind == 'Module':
                if package:
                    filename = os.path.join(package, name)
                else:
                    filename = os.path.join(rootdir, name)
            else:
                assert kind == 'Function'
                yield cls(filename=os.path.abspath(filename), function=name)

    @classmethod
    def gen_cursor_predicate(cls):
        curbuf = vim.current.buffer
        normpath = os.path.normpath(curbuf.name)

        test_method_line, selected_test_indentation, selected_test = find_line_above(
            curbuf, vim.current.window.cursor[0] - 1, cls.TEST_LINE_PATTERN)

        if not selected_test:
            return None

        if 4 == len(selected_test_indentation):
            _, test_class_name = find_line_above(curbuf, test_method_line, cls.CLASS_LINE_PATTERN)
            if not test_class_name:
                return None  # probably a method that looks like a test but isn't actually one...
            else:
                # selected_test = '%s and %s' % (test_class_name, selected_test)
                selected_test = class_and_method_format.format(cls=test_class_name, mtd=selected_test)

        def pred(test):
            if os.path.normpath(test.filename) != normpath:
                return False
            if not test.function.startswith(selected_test):
                return False
            postfix = test.function[len(selected_test):]
            return not postfix or postfix[0] == '['
        return pred
