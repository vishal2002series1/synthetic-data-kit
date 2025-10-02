import unittest

from lance.generators.java import TYPE_STRING, TYPE_CLASS, TYPE_LIST_CLASS, MODE_PUBLIC, TYPE_INTEGER, \
    TYPE_ANNOTATION_PRIMITIVE
from lance.generators.java.method import Method, getter, setter


class TestMethods(unittest.TestCase):

    def test_simple_method(self):
        doc = {
            "name": "syncRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
        }
        m = Method(doc)
        g = m.generate(4)
        print(m.get_imports())
        print(g)

    def test_arg_method(self):
        doc = {
            "name": "syncRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "inputs": [
                {
                    "name": "value",
                    "type": {
                        "of": TYPE_STRING
                    }
                }
            ]
        }
        m = Method(doc)
        g = m.generate(4)
        print(m.get_imports())
        print(g)

    def test_body_method(self):
        doc = {
            "name": "deleteRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_CLASS,
                "fqcn": "org.springframework.web.mvc.HttpEntity"
            },
            "inputs": [
                {
                    "type": {
                        "of": TYPE_STRING
                    }
                }
            ],
            "body": {
                "form": ["Map<Integer,RiskAssessment> map = new HashMap<>();", "map.put(1, new RiskAssessment());"],
                "imports": ["java.util.Map", "java.util.HashMap", "com.susamn.RiskAssessment"]
            }
        }
        m = Method(doc)
        g = m.generate(4)
        print(m.get_imports())
        print(g)

    def test_annotated_method(self):
        doc = {
            "name": "processRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "annotations": [
                {
                    "fqcn": "com.susamn.Annotation11",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_PRIMITIVE,
                            "value": 78.10
                        }
                    }
                }
            ]
        }
        m = Method(doc)
        g = m.generate(4)
        print(m.get_imports())
        print(g)

    def test_multiple_annotated_method(self):
        doc = {
            "name": "processRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "annotations": [
                {
                    "fqcn": "com.susamn.Annotation11",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_PRIMITIVE,
                            "value": 78.10
                        }
                    }
                },
                {
                    "fqcn": "com.susamn.Annotation10",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_PRIMITIVE,
                            "value": 12.19
                        }
                    }
                }
            ]
        }
        m = Method(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_arg_method_with_annotation(self):
        doc = {
            "name": "processRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "inputs": [
                {
                    "name": "body",
                    "type": {
                        "of": TYPE_STRING
                    }
                }
            ],
            "annotations": [
                {
                    "fqcn": "com.susamn.Annotation11",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_PRIMITIVE,
                            "value": 78.10
                        }
                    }
                }
            ]
        }
        m = Method(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_arg_method_with_annotation_and_body(self):
        doc = {
            "name": "processRequest",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "inputs": [
                {
                    "name": "body",
                    "type": {
                        "of": TYPE_STRING
                    }
                }
            ],
            "annotations": [
                {
                    "fqcn": "com.susamn.Annotation11",
                    "data": {
                        "key1": {
                            "type": TYPE_ANNOTATION_PRIMITIVE,
                            "value": 78.10
                        }
                    }
                }
            ],
            "body": {
                "form": ["Map<Integer,RiskAssessment> map = new HashMap<>();", "map.put(1, new RiskAssessment());"],
                "imports": ["java.util.Map", "java.util.HashMap", "com.susamn.RiskAssessment"]
            }
        }
        m = Method(doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_getter_string(self):
        attribute_type_doc = {
            "of": TYPE_STRING
        }
        m = getter("employeeId", attribute_type_doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_getter_class(self):
        attribute_type_doc = {
            "of": TYPE_CLASS,
            "fqcn":"com.susamn.Entity"
        }
        m = getter("name", attribute_type_doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_getter_list_class(self):
        attribute_type_doc = {
            "of": TYPE_LIST_CLASS,
            "fqcn":"com.susamn.Entity"
        }
        m = getter("name", attribute_type_doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)

    def test_setter_string(self):
        attribute_type_doc = {
            "of": TYPE_STRING
        }
        m = setter("employeeId", attribute_type_doc)
        print(m.get_imports())
        g = m.generate(4)
        print(g)


if __name__ == '__main__':
    unittest.main()
