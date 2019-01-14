import os
import re

from . import TargetTest


class JavaJUnitTest(TargetTest):
    TEST_PATTERN = re.compile(r'@Test\n\s*public void (\w+)\(')

    def __init__(self, subproject, classname, test):
        self.subproject = subproject
        self.classname = classname
        self.test = test

    def __str__(self):
        return '%s.%s' % (self.classname, self.test)

    def __repr__(self):
        return '%s(subproject=%r, classname=%r, test=%r)' % (
            type(self).__name__,
            self.subproject,
            self.classname,
            self.test)

    @property
    def shortname(self):
        return str(self)

    @classmethod
    def find_at(cls, path):
        for subproject, filepath in cls._find_test_files(path):
            with open(filepath, 'r') as f:
                filetext = f.read()
            for match in cls.TEST_PATTERN.finditer(filetext):
                yield cls(
                    subproject=subproject,
                    classname=os.path.split(os.path.splitext(filepath)[0])[1],
                    test=match.group(1))

    @classmethod
    def gen_cursor_predicate(cls):
        pass

    @classmethod
    def _find_subproject_dirs(cls, path):
        for dirpath, dirnames, filenames in os.walk(path):
            head, tail = os.path.split(dirpath)
            if tail != 'test':
                continue
            head, tail = os.path.split(head)
            if tail != 'src':
                continue
            yield head


    @classmethod
    def _find_test_files(cls, path):
        for subproject_dir in cls._find_subproject_dirs(path):
            _, subproject = os.path.split(subproject_dir)
            for dirpath, dirnames, filenames in os.walk(os.path.join(subproject_dir, 'src', 'test')):
                for filename in filenames:
                    if filename.endswith('.java'):
                        yield subproject, os.path.join(dirpath, filename)
