from lance.generators.java import ANNOTATION_LEVEL_ATTRIBUTE, MODE_PUBLIC, MODE_PRIVATE
from lance.generators.java.helper import Generator, padding
from lance.generators.java.annotations import parse_annotations
from lance.generators.java.method import getter, setter
from lance.generators.java.typs import obtain_type


class Attribute(Generator):
    # TODO Need to support initialization
    def __init__(self, document):

        self.annotations = []
        self.imports = []
        self.methods = []
        self.initialized_form = None

        self.name = document.get("name")
        self.mode = document.get("mode") or MODE_PRIVATE
        attrib_type = document.get("type")
        self.attribute_accessors_generate = document.get("accessors")
        self.annotation_level = document.get("annotation_level") or ANNOTATION_LEVEL_ATTRIBUTE
        initialized_form = document.get("initialized_form")
        self.is_final = document.get("is_final") or False
        self.is_static = document.get("is_static") or False

        if not self.name or not attrib_type:
            raise ValueError("The attribute name and type must be provided")

        # Type information fetching
        self.typ, imports = obtain_type(self.name, attrib_type)

        if not self.typ:
            raise ValueError(f"The return type of method {self.name} could not be obtained")

        if imports and len(imports) > 0:
            self.imports.extend(imports)

        method_annotations_info = document.get("annotations")
        self.annotations = parse_annotations(method_annotations_info)

        if self.annotations and len(self.annotations) > 0:
            for a in self.annotations:
                if a and a.get_imports() and len(a.get_imports()) > 0:
                    self.imports.extend(a.get_imports())

        if self.attribute_accessors_generate:
            attribute_getter_method = getter(self.name, attrib_type)
            attribute_setter_method = setter(self.name, attrib_type)
            self.methods.append(attribute_getter_method)
            self.methods.append(attribute_setter_method)
            self.imports.extend(attribute_getter_method.get_imports())
            self.imports.extend(attribute_setter_method.get_imports())

        # Add initialization data
        if initialized_form:
            i_form = initialized_form.get("form")
            i_imports = initialized_form.get("imports")
            if i_form:
                self.initialized_form = i_form
            if i_imports and len(i_imports) > 0:
                self.imports.extend(i_imports)

    def get_imports(self):
        return self.imports

    def get_methods(self):
        return self.methods

    def make_static(self):
        self.is_static = True

    def make_final(self):
        self.is_final = True

    def make_public(self):
        self.mode = MODE_PUBLIC

    def get_type(self):
        return self.typ

    def get_name(self):
        return self.name

    def __gt__(self, other):
        if not type(other) == Attribute:
            raise ValueError(f"{other} is not a type that cam be compared to an Attribute")
        if self.annotations and not other.annotations:
            return True

    def generate(self, indentation=0):
        annotation_string = None

        common_structure = f'{padding(indentation)}{self.mode}'

        if self.is_static:
            common_structure = f'{common_structure} static'

        if self.is_final:
            common_structure = f'{common_structure} final'

        if self.initialized_form:
            common_structure = f'{common_structure} {self.typ} {self.name} = {self.initialized_form};'
        else:
            common_structure = f'{common_structure} {self.typ} {self.name};'

        # Calculate the annotation string
        if len(self.annotations) > 0:
            annotation_string = "\n".join([x.generate(indentation=indentation) for x in self.annotations])

        # Add annotations
        if annotation_string:
            common_structure = f'\n{annotation_string}\n{common_structure}'

        return common_structure
