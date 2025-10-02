import unittest

from lance.generators.java import TYPE_INTEGER, TYPE_ANNOTATION_STRING, TYPE_STRING
from lance.generators.java.attribute import Attribute


class TestAttrributes(unittest.TestCase):

    def test_simple_attribute(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "type": {
                "of": TYPE_STRING
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_simple_attribute_with_accessors(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "accessors": True,
            "type": {
                "of": TYPE_STRING
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)
        print(m.get_methods())

    def test_annotated_attribute(self):
        doc = {
            "name": "foo",
            "mode": "private",
            "type": {
                "of": TYPE_STRING
            },
            "annotations": [
                {
                    "fqcn": "com.susamn.Annotation1",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_STRING,
                            "value": 23
                        }
                    }
                }
            ]
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_static_attribute(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "is_static": True,
            "type": {
                "of": TYPE_STRING
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_final_attribute(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "is_final": True,
            "type": {
                "of": TYPE_STRING
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_static_final_attribute(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "is_static": True,
            "is_final": True,
            "type": {
                "of": TYPE_STRING
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_static_final_initialized_attribute(self):
        doc = {
            "name": "logger",
            "mode": "public",
            "type": {
                "of": "CLASS",
                "fqcn": "org.slf4j.api.Logger"
            },
            "initialized_form": {
                "form": "LoggerFactory.getLogger(RiskAssessmentController.class)",
                "imports": ["org.apache.logger.api.LoggerFactory","com.susamn.RiskAssessmentController"]
            }
        }
        m = Attribute(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

if __name__ == '__main__':
    unittest.main()
