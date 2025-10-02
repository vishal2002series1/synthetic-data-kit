import unittest

from lance.generators.java import TYPE_ARRAY_CHAR
from lance.generators.java.typs import *


class TestTypes(unittest.TestCase):

    def test_custom_type(self):
        x, y = process_type(TYPE_CLASS, fqcn="com.susamn.Custom")
        print(x, y)

    def test_void_type(self):
        x, y = process_type(TYPE_VOID)
        print(x, y)

    def test_normal_type(self):
        x, y = process_type(TYPE_STRING)
        print(x, y)

    def test_list_custom(self):
        x, y= process_type(TYPE_LIST_CLASS, fqcn="com.susamn.Foo")
        print(x, y)

    def test_array_int(self):
        x, y = process_type(TYPE_ARRAY_INT)
        print(x, y)

    def test_array_float(self):
        x, y = process_type(TYPE_ARRAY_FLOAT)
        print(x, y)

    def test_array_long(self):
        x, y = process_type(TYPE_ARRAY_LONG)
        print(x, y)

    def test_array_boolean(self):
        x, y = process_type(TYPE_ARRAY_BOOLEAN)
        print(x, y)

    def test_array_char(self):
        x, y = process_type(TYPE_ARRAY_CHAR)
        print(x, y)

    def test_array_custom(self):
        x, y = process_type(TYPE_ARRAY_CLASS, fqcn="com.susamn.Foo")
        print(x, y)



if __name__ == '__main__':
    unittest.main()
