from abc import ABC, abstractproperty, abstractclassmethod

from omnipytent import task


class TargetTest(ABC):
    @abstractproperty
    def shortname(self):
        pass


    @abstractclassmethod
    def find_at(cls, path):
        pass

    @abstractclassmethod
    def gen_cursor_predicate(cls):
        pass

    @classmethod
    def gen_choose_test_task(cls, paths, multi=False, task_name='choose_test', alias=[], cache_choice_value=False):
        if isinstance(paths, str):
            paths = [paths]

        def choose_test(ctx):
            ctx.key(lambda test: test.shortname)
            cursor_predicate = cls.gen_cursor_predicate()
            tests = []
            first_tests = []
            for path in paths:
                for test in cls.find_at(path):
                    if cursor_predicate(test):
                        first_tests.append(test)
                    else:
                        tests.append(test)

            for test in first_tests:
                yield test
            for test in tests:
                yield test

        choose_test.__name__ = task_name

        dsl = task.options_multi if multi else task.options
        return dsl(alias=alias, cache_choice_value=cache_choice_value)(choose_test)


def find_line_above(vimbuf, line_number, pattern):
    while 0 <= line_number:
        m = pattern.match(vimbuf[line_number])
        if m:
            return (line_number,) + m.groups()
        line_number -= 1
    return tuple([None] * (1 + pattern.groups))
