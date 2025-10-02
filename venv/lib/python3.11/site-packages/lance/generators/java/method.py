from lance.generators.java import MODE_PRIVATE, MODE_PUBLIC, TYPE_VOID
from lance.generators.java.helper import Generator, to_camel_case, padding
from lance.generators.java.annotations import parse_annotations
from lance.generators.java.typs import obtain_type


class Method(Generator):
    def __init__(self, document):
        self.inputs = []
        self.named_inputs = {}
        self.body = None
        self.isAbstract = False
        self.isStatic = document.get("is_static") or False
        self.imports = []

        self.name = document.get("name")
        self.mode = document.get("mode") or MODE_PRIVATE
        return_type = document.get("type")
        method_body = document.get("body")

        if not self.name or not return_type:
            raise ValueError(f'The method argument must have method name and type')

        # Type check of the method
        self.return_type, method_imports = obtain_type(self.name, return_type)

        if not self.return_type:
            raise ValueError(f"The return type of method {self.name} could not be obtained")

        if method_imports and len(method_imports) > 0:
            self.imports.extend(method_imports)

        inputs = document.get("inputs")
        if inputs and len(inputs) > 0:
            for i in inputs:
                input_type_information = i.get("type")
                input_type_name = i.get("name")
                if not input_type_information:
                    raise ValueError(f"The input type of method {self.name} could not be found")
                method_input_type, method_input_imports = obtain_type(self.name, input_type_information)
                if not method_input_type:
                    raise ValueError(f"The input type of method {self.name} could not be parsed")
                # Add method input type
                if input_type_name:
                    self.named_inputs[input_type_name] = method_input_type
                else:
                    self.inputs.append(method_input_type)
                if len(method_input_imports) > 0:
                    self.imports.extend(method_input_imports)

        method_annotations_info = document.get("annotations")
        self.annotations = parse_annotations(method_annotations_info)

        if self.annotations and len(self.annotations) > 0:
            for a in self.annotations:
                if a and a.get_imports() and len(a.get_imports()) > 0:
                    self.imports.extend(a.get_imports())


        if method_body:
            m_body_form = method_body.get("form")
            m_body_imports = method_body.get("imports")
            if m_body_form:
                self.body = m_body_form

                if m_body_imports and len(m_body_imports) > 0:
                    self.imports.extend(m_body_imports)

    def get_imports(self):
        return self.imports

    def make_abstract(self):
        self.isAbstract = True



    def generate(self, indentation=0):
        input_string = None
        named_input_string = None
        annotation_string = None

        # Calculate the annotation string
        if len(self.annotations) > 0:
            annotation_string = "\n".join([x.generate(indentation=indentation) for x in self.annotations])

        # Calculate the input string, this is for the inputs, where only the type of the args are known
        if len(self.inputs) > 0:
            input_string = ", ".join([f'{x} val{i}' for i, x in enumerate(self.inputs)])

        # Calculate the input string, this is for the inputs, where the name and type is known
        if len(self.named_inputs) > 0:
            named_input_string = ", ".join([f'{y} {x}' for x, y in self.named_inputs.items()])

        # Create the common method structure
        if self.isStatic:
            common_structure = f'{padding(indentation)}{self.mode} static {self.return_type} {self.name}'
        else:
            common_structure = f'{padding(indentation)}{self.mode} {self.return_type} {self.name}'

        # Add input arguments
        total_input_string = None
        if input_string and named_input_string:
            total_input_string = f'{named_input_string}, {input_string}'
        elif input_string and not named_input_string:
            total_input_string = input_string
        elif named_input_string and not input_string:
            total_input_string = named_input_string

        if total_input_string:
            common_structure = f'{common_structure}({total_input_string})'
        else:
            common_structure = f'{common_structure}()'

        # Add body
        if self.isAbstract:
            common_structure = f'{common_structure};'
        else:
            if self.body:
                bps=[]
                for bp in self.body:
                    if bp:
                        bps.append(f'{padding(indentation+4)}{bp}')
                formatted_body = '\n'.join(bps)
                common_structure = f'{common_structure}{{\n{formatted_body}\n{padding(indentation)}}}'
            else:
                common_structure = f'{common_structure}{{\n{padding(indentation)}}}'

        # Add annotations
        if annotation_string:
            common_structure = f'{annotation_string}\n{common_structure}'

        return common_structure


def getter(attribute_name, typ):
    getter = {
        "name": f'get{to_camel_case(attribute_name)}',
        "mode": MODE_PUBLIC,
        "type": typ,
        "body": {
            "form": [f'return this.{attribute_name};']
        }
    }
    method = Method(getter)
    return method


def setter(attribute_name, typ):
    setter = {
        "name": f'set{to_camel_case(attribute_name)}',
        "mode": MODE_PUBLIC,
        "type": {
            "of": TYPE_VOID
        },
        "inputs": [
            {
                "name": f'{attribute_name}',
                "type": typ
            }
        ],
        "body": {
            "form": [f'this.{attribute_name} = {attribute_name};']
        }
    }
    method = Method(setter)
    return method

