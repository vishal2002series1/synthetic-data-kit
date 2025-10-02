import os


class Generator:
    def generate(self, indentation=0):
        pass


class Writer:
    def __init__(self, folder):
        self.folder = folder
        self.classes = {}
        self.package = None

    def add_item(self, fqcn, claz):
        self.classes[fqcn] = claz

    def write_all(self):
        if len(self.classes) == 0:
            print("No classes to write to disk")

        if self.folder:
            for fqcn, generated_data in self.classes.items():
                class_name = class_name_from_package(fqcn)
                package_name = package_name_from_package(fqcn)
                final_path = create_folders(self.folder, package_name)
                with open(os.path.join(final_path, f'{class_name}.java'), "w") as fh:
                    fh.write(generated_data)
                    fh.flush()
                print(f'Written file {final_path}/{class_name}.java')
        else:
            for _, generated_data in self.classes.items():
                print(generated_data)


def create_folders(root_folder, package):
    if not os.path.isdir(root_folder):
        raise ValueError(f'The root directory {root_folder} does not exist')
    parts = package.split(".")
    if parts and len(parts) > 0:
        temp_dir = root_folder
        for part in parts:
            temp_dir = os.path.join(temp_dir, part)
            if not os.path.isdir(temp_dir):
                os.mkdir(temp_dir)
        return temp_dir


def to_camel_case(s):
    return s[0].upper() + s[1:] if s else s


def padding(indentation):
    return f'{"":>{indentation}}'


def package_name_from_package(clazz):
    splits = clazz.split(".")
    return ".".join(splits[:-1])


def class_name_from_package(clazz):
    splits = clazz.split(".")
    return splits[-1]
