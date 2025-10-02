import unittest

from lance.generators.java.helper import class_name_from_package
from lance.generators.java.typs import process_type, TYPE_STRING


class MyTestCase(unittest.TestCase):
    def test_fqcn(self):
        v = class_name_from_package("java.lang.Integer")
        self.assertEqual(True,  v == "Integer")

    def test_string(self):
        v = process_type(TYPE_STRING)
        print(v)



if __name__ == '__main__':
    unittest.main()
