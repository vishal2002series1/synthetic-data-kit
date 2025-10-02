import unittest

from lance.generators.java import TYPE_CLASS, TYPE_INTEGER, TYPE_STRING, TYPE_LIST_CLASS, CONSTRUCTOR_ALL, MODE_PUBLIC, \
    CONSTRUCTOR_EMPTY, CONSTRUCTOR_SELECTED
from lance.generators.java.klass import Klass


class TestClass(unittest.TestCase):
    def test_simple_class(self):
        doc = {
            "fqcn": "com.susamn.MetaEnum",
            "type": TYPE_CLASS
        }
        m = Klass(doc)
        g = m.generate(4)
        print(g)

    def test_simple_class_with_attributes(self):
        doc = {
            "fqcn": "com.susamn.MetaClass",
            "type": TYPE_CLASS,
            "attributes": [
                {
                    "name": "logger",
                    "mode": "public",
                    "type": {
                        "of": TYPE_CLASS,
                        "fqcn": "org.slf4j.api.Logger"
                    }
                }]
        }
        m = Klass(doc)
        g = m.generate(4)
        print(g)

    def test_simple_class_with_attribute_accessors(self):
        doc = {
            "fqcn": "com.susamn.MetaClass",
            "type": TYPE_CLASS,
            "attributes": [
                {
                    "name": "logger",
                    "mode": "public",
                    "type": {
                        "of": TYPE_CLASS,
                        "fqcn": "org.slf4j.api.Logger"
                    },
                    "accessors": True
                }]
        }
        m = Klass(doc)
        g = m.generate(4)
        print(g)

    def test_simple_class_with_attribute_accessors(self):
        doc = {
            "fqcn": "com.susamn.MetaClass",
            "type": TYPE_CLASS,
            "attributes": [
                {
                    "name": "logger",
                    "mode": "public",
                    "type": {
                        "of": TYPE_CLASS,
                        "fqcn": "org.slf4j.api.Logger"
                    },
                    "initialized_form": {
                        "form": "LoggerFactory.getLogger(RiskAssessmentController.class)",
                        "imports": ["org.apache.logger.api.LoggerFactory", "com.susamn.RiskAssessmentController"]
                    }
                }]
        }
        m = Klass(doc)
        g = m.generate(4)
        print(g)

    def test_simple_class_with_constructors(self):
        doc = {
            "fqcn": "com.susamn.MetaClass",
            "type": TYPE_CLASS,
            "attributes": [
                {
                    "name": "employeeId",
                    "type": {
                        "of": TYPE_INTEGER
                    }
                },
                {
                    "name": "name",
                    "type": {
                        "of": TYPE_STRING
                    }
                },
                {
                    "name": "logger",
                    "mode": "public",
                    "type": {
                        "of": TYPE_CLASS,
                        "fqcn": "org.slf4j.api.Logger"
                    }
                },
                {
                    "name": "classes",
                    "mode": "public",
                    "type": {
                        "of": TYPE_LIST_CLASS,
                        "fqcn": "com.susamn.SomeClass"
                    }
                }],
            "constructors": [
                {
                    "type": CONSTRUCTOR_ALL,
                    "mode": MODE_PUBLIC
                },
                {
                    "type": CONSTRUCTOR_EMPTY,
                    "mode": MODE_PUBLIC
                },
                {
                    "type": CONSTRUCTOR_SELECTED,
                    "args": ["classes", "logger"],
                    "body": {
                        "form": ["super(classes);"]
                    }
                }
            ]
        }
        m = Klass(doc)
        g = m.generate(4)
        print(g)


if __name__ == '__main__':
    unittest.main()
