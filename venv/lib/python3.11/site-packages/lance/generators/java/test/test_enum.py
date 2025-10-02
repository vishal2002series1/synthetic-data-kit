import unittest

from lance.generators.java.enum import Enum


class TestEnum(unittest.TestCase):
    def test_enum(self):
        doc = {
            "fqcn": "com.susamn.MetaEnum",
            "type": "ENUM",
            "values": [
                "SUCCESS",
                "FAILURE"
            ]
        }

        m = Enum(doc)
        g = m.generate(4)
        print(g)


if __name__ == '__main__':
    unittest.main()
