import unittest

from lance.generators.java.schema_reader import engage


class TestSchemaReader(unittest.TestCase):
    def test_schema_single_class(self):
        engage(file="meta.json")



if __name__ == '__main__':
    unittest.main()