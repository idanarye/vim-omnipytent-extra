import re

from .java import JavaJUnitTest


class KotlinJUnitTest(JavaJUnitTest):
    TEST_PATTERN = re.compile(r'@Test\n\s*fun (\w+)\(')
    TESTFILE_SUFFIX = '.kt'
