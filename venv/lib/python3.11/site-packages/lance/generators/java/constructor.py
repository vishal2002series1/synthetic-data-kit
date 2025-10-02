from lance.generators.java import CONSTRUCTOR_ALL, CONSTRUCTOR_SELECTED, MODE_PRIVATE
from lance.generators.java.helper import Generator, padding


class Constructor(Generator):
    def __init__(self, class_name, doc, attributes):
        if doc:
            self.class_name = class_name
            self.mode = doc.get("mode") or MODE_PRIVATE
            self.constructor_type = doc.get("type")
            self.constructor_args = doc.get("args")
            self.body = None
            self.attributes = None
            self.imports = []

            body = doc.get("body")
            if body and not type(body) == dict:
                raise ValueError("The body section of the constructor must be a dict")

            if body:
                self.body = body.get("form")
                imports = body.get("imports")
                if self.body and not type(self.body) == list:
                    raise ValueError("The form of the body in constructor must be a list")
                if imports and len(imports) > 0:
                    self.imports.extend(imports)

            if self.constructor_type == CONSTRUCTOR_ALL:
                self.attributes = [(a.get_type(), a.get_name()) for a in attributes]
            elif self.constructor_type == CONSTRUCTOR_SELECTED:
                if not self.constructor_args:
                    raise ValueError("For selected arguments constructor, the selections must be provided")
                self.attributes = [(a.get_type(), a.get_name()) for a in attributes if
                                   a.get_name() in self.constructor_args]

    def get_imports(self):
        return self.imports


    def generate(self, indentation=0):
        common_structure = f'{padding(indentation)}{self.mode} {self.class_name}('

        if self.attributes and len(self.attributes) > 0:
            attribute_string = ", ".join([f'{x[0]} {x[1]}' for x in self.attributes])
            if attribute_string:
                common_structure = f'{common_structure}{attribute_string}'

        common_structure = f'{common_structure}){{\n'

        body = ""
        if self.body and len(self.body) > 0:
            for b in self.body:
                body = f'{body}{padding(indentation + 4)}{b}\n'

        body = f'{body}\n'

        if self.attributes and len(self.attributes) > 0:
            for att in self.attributes:
                body = f'{body}{padding(indentation + 4)}this.{att[1]} = {att[1]};\n'

        common_structure = f'{common_structure}{body}'
        common_structure = f'{common_structure}{padding(indentation)}}}\n'

        return common_structure
