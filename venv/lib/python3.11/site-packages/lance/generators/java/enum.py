from lance.generators.java import TYPE_CLASS, TYPE_STRING, MODE_PUBLIC
from lance.generators.java.helper import Generator, padding, package_name_from_package, class_name_from_package
from lance.generators.java.annotations import parse_annotations
from lance.generators.java.method import Method
from lance.generators.java.typs import process_type


class Enum(Generator):
    # TODO Need to support initialization
    def __init__(self, document, folder=None):
        self.fqcn = document.get("fqcn")
        if self.fqcn:
            self.class_name = class_name_from_package(self.fqcn)
            self.package = package_name_from_package(self.fqcn)
        else:
            raise ValueError("A class must have a fqcn")
        self.imports = set()
        self.attributes = []
        self.methods = []
        self.generate_folder = folder
        self.enums = []

        enums = document.get("values")
        if not enums or not type(enums) == list or len(enums) == 0:
            raise ValueError(f"Please provide enum values to the Enum {self.class_name}")
        self.enums.extend(enums)

        # Process class level annotations
        annotations = document.get("annotations")
        self.annotations = parse_annotations(annotations)
        if self.annotations and len(self.annotations) > 0:
            for a in self.annotations:
                if a and a.get_imports() and len(a.get_imports()) > 0:
                    self.imports.update(a.get_imports())

    def generate(self, indentation=4):
        template = f"public enum {self.class_name}"

        typ, ims = process_type(TYPE_STRING)
        self.imports.update(ims)

        method_from_value = {
            "name": "fromValue",
            "mode": MODE_PUBLIC,
            "is_static": True,
            "type": {
                "of": TYPE_CLASS,
                "fqcn": self.class_name
            },
            "inputs": [
                {
                    "name": "value",
                    "type": {
                        "of": TYPE_STRING
                    }
                }
            ],
            "body": {
                "form": ["return valueOf(value);"]
            }
        }

        method_getter = {
            "name": "getValue",
            "mode": MODE_PUBLIC,
            "type": {
                "of": TYPE_STRING
            },
            "body": {
                "form": ["return this.toString();"]
            }
        }

        method_from_value = Method(method_from_value)
        method_getter = Method(method_getter)

        generated = ""
        generated += f'package {self.package};'
        generated += "\n\n"
        self.imports = sorted(self.imports)
        for i in self.imports:
            generated += f'import {i};\n'
        generated += "\n\n"
        generated += f"\n{template} {{"
        generated += "\n"
        self.enums = sorted(self.enums)

        enum_string = f'{padding(indentation)}{",".join(self.enums)};'
        generated += enum_string
        generated += "\n"

        generated += "\n"
        generated += method_from_value.generate(indentation=indentation)
        generated += "\n"
        generated += method_getter.generate(indentation=indentation)
        generated += "\n"
        generated += "\n"
        generated += f"}}"

        return self.fqcn, generated

