import yaml

from conf import fixture_path

def load_yaml(name):
    with open("{}/{}.yml".format(fixture_path, name), 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)