from lance.generators.java.helper import Generator, package_name_from_package, class_name_from_package
from lance.generators.java.annotations import parse_annotations
from lance.generators.java.attribute import Attribute
from lance.generators.java.method import Method
from lance.generators.java.typs import handle_generic_types


class Interface(Generator):
    '''
    Interface class is responsible
    '''
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

        # Process class level implementations
        extends = document.get("extends")
        self.extends = None
        if extends and not type(extends) == list:
            raise ValueError(f"Please provide implementation data properly for interface {self.fqcn}")
        if extends:
            if len(extends) > 0:
                all_extended_interfaces = []
                for e in extends:
                    extends_fqcn_class_name = e.get("fqcn")
                    extends_generic_types = e.get("generic_types")
                    extends_fqcn, imports = handle_generic_types(extends_fqcn_class_name,
                                                                 extends_generic_types)

                    all_extended_interfaces.append(extends_fqcn)
                    self.imports.update(imports)
                self.extends = ", ".join(all_extended_interfaces)

        # Process class level annotations
        annotations = document.get("annotations")
        self.annotations = parse_annotations(annotations)
        if self.annotations and len(self.annotations) > 0:
            for a in self.annotations:
                if a and a.get_imports() and len(a.get_imports()) > 0:
                    self.imports.update(a.get_imports())

        # Attributes
        attributes = document.get("attributes")
        if attributes:
            for a_doc in attributes:
                attribute = Attribute(a_doc)
                attribute.make_final()
                attribute.make_static()
                attribute.make_public()
                self.add_attribute(attribute)

        # Methods
        methods = document.get("methods")
        if methods:
            for m_doc in methods:
                method = Method(m_doc)
                method.make_abstract()
                self.add_method(method)

    def add_method(self, method):
        self.methods.append(method)
        if len(method.get_imports()) > 0:
            self.imports.update(method.get_imports())

    def add_attribute(self, attribute):
        self.attributes.append(attribute)
        if len(attribute.get_imports()) > 0:
            self.imports.update(attribute.get_imports())
        if len(attribute.get_methods()) > 0:
            self.methods.extend(attribute.get_methods())

    def generate(self, indentation=4):
        template = f"public interface {self.class_name}"
        if self.extends:
            template = f"{template} extends {self.extends}"

        generated = ""
        generated += f'package {self.package};'
        generated += "\n\n"
        self.imports = sorted(self.imports)
        for i in self.imports:
            generated += f'import {i};\n'
        generated += "\n\n"
        if len(self.annotations) > 0:
            generated += "\n".join([x.generate() for x in self.annotations])
        generated += f"\n{template} {{"
        generated += "\n\n"
        self.attributes = sorted(self.attributes)
        for att in self.attributes:
            generated += att.generate(indentation=indentation)
            generated += "\n"
        generated += "\n"
        for meth in self.methods:
            generated += meth.generate(indentation=indentation)
            generated += "\n"
        generated += "\n"
        generated += f"}}"

        return self.fqcn, generated
