from lance.generators.java import TYPE_ANNOTATION, TYPE_ANNOTATION_PRIMITIVE, TYPE_ANNOTATION_CLASS, \
    TYPE_ANNOTATION_STRING, TYPE_ANNOTATION_EVALUATED, TYPE_ANNOTATION_ANNOTATION, TYPE_ANNOTATION_LIST_PRIMITIVE, \
    TYPE_ANNOTATION_LIST_CLASS, TYPE_ANNOTATION_LIST_STRING, TYPE_ANNOTATION_LIST_EVALUATED, \
    TYPE_ANNOTATION_LIST_ANNOTATION
from lance.generators.java.helper import Generator, padding, class_name_from_package


class Annotation(Generator):
    def __init__(self, document):
        self.fqcn = document.get("fqcn")
        self.data = {}

        data = document.get("data")
        if not self.fqcn:
            raise ValueError("If you are providing annotation, it must have package and data")

        # Add self fqcn to the import list
        self.imports = [self.fqcn]

        if data and type(data) is not dict:
            raise ValueError("The data to an annotation can only be a dict, got : ", type(data))
        if data and len(data) > 0:
            parsed_data = self.__parse_data(data)
            self.data.update(parsed_data)

    def get_imports(self):
        return self.imports

    def generate(self, indentation=0):
        if len(self.data) == 0:
            return f'{padding(indentation)}@{class_name_from_package(self.fqcn)}'
        else:
            parts = []
            for k, v in self.data.items():
                parts.append(f'{k} = {v}')
            return f'{padding(indentation)}@{class_name_from_package(self.fqcn)}(' + ", ".join(parts) + ')'

    def __parse_data(self, data):
        result_data = {}
        for k, v in data.items():
            value_type = v.get("type")
            value_data = v.get("value")
            imports = v.get("imports")
            if value_type:
                if value_type not in JAVA_ANNOTATION_MAPPER:
                    raise ValueError(f"The value type {value_type} is not mapped for annotation")
                parsed_data, nested_imports = JAVA_ANNOTATION_MAPPER[value_type](value_data)
                result_data[k] = parsed_data
                # Handle imports
                if imports and len(imports) > 0:
                    self.imports.extend(imports)
                if nested_imports and len(nested_imports) > 0:
                    self.imports.extend(nested_imports)
            else:
                raise ValueError(f'The annotation {self.fqcn} is provided with wrong type')
        return result_data


JAVA_ANNOTATION_MAPPER = {
    TYPE_ANNOTATION: lambda x: create_annotation_with_imports(x),
    TYPE_ANNOTATION_PRIMITIVE: lambda x: (x, None),
    TYPE_ANNOTATION_CLASS: lambda x: (f'{class_name_from_package(x)}.class', None),
    TYPE_ANNOTATION_STRING: lambda x: (f'"{x}"', None),
    TYPE_ANNOTATION_EVALUATED: lambda x: (x, None),
    TYPE_ANNOTATION_ANNOTATION: lambda x: create_annotation_with_imports(x),
    TYPE_ANNOTATION_LIST_PRIMITIVE: lambda x: (f'{{{", ".join([str(a) for a in x])}}}', None),
    TYPE_ANNOTATION_LIST_CLASS: lambda x: (f'{{{", ".join([f"{class_name_from_package(a)}.class" for a in x])}}}', None),
    TYPE_ANNOTATION_LIST_STRING: lambda x: (f'{{{", ".join([wrap_with_quotes(a) for a in x])}}}', None),
    TYPE_ANNOTATION_LIST_EVALUATED: lambda x: (f'{{{", ".join([a for a in x])}}}', None),
    TYPE_ANNOTATION_LIST_ANNOTATION: lambda x: process_list_annotations(x)
}


def process_list_annotations(annotations):
    imports = []
    parsed_annotations = []
    for annotation in annotations:
        a, i = create_annotation_with_imports(annotation)
        if not a:
            raise ValueError(f'The annotation {annotation} could not be parsed')
        parsed_annotations.append(a)
        if i and len(i) > 0:
            imports.extend(i)
    return f'{{{", ".join([a for a in parsed_annotations])}}}', imports


def wrap_with_quotes(val):
    return f'"{val}"'


def create_annotation_with_imports(doc):
    a = create_annotation_from_document(doc)
    return a.generate(), a.get_imports()


def create_annotation_from_document(doc):
    a = Annotation(doc)
    return a


def parse_annotations(annotations=None):
    result = list()
    if annotations and len(annotations) > 0:
        for annotation_doc in annotations:
            result.append(create_annotation_from_document(annotation_doc))
    return result
