import unittest
from lance.generators.java.interface import Interface


class TestInterface(unittest.TestCase):
    def test_simple_interface(self):
        doc={
            "fqcn": "com.susamn.MetaInterface",
            "type": "INTERFACE",
            "generic_types": ["java.lang.Integer"],
            "extends": [
                {
                    "fqcn": "java.io.Serializable"
                },
                {
                    "fqcn": "org.springframework.data.jpa.repository.JpaRepository",
                    "generic_types": ["com.susamn.Root","java.lang.String"]
                }

            ]
        }
        m = Interface(doc)
        g = m.generate(4)
        print(g)




if __name__ == '__main__':
    unittest.main()