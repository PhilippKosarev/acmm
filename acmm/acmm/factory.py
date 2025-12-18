# Imports
from pathlib import Path

# Relative imports
from .shared import *

# An __init__ function for all assigned assets.
def asset_init(self, path):
  # Checking given path
  path = Path(path)
  if not path.exists():
    raise FileNotFoundError(f"Path '{path}' does not exist")
  if not self.__validate__(path):
    function_source = (
      self.__validate__.__module__ + '.' +
      self.__validate__.__name__
    )
    raise InvalidAsset(
      'Given path appears to lead to an invalid asset. '
      f"Validation was done by '{function_source}'"
    )
  self.path = path

def is_asset_path_valid(self) -> bool:
  if hasattr(self, 'path'):
    if hasattr(self.path, 'name'):
      return True
  return False

def asset_repr(self) -> str:
  name = self.__class__.__name__
  string = f'{name} asset '
  if is_asset_path_valid(self):
    string += f"'{self.get_id()}'"
  else:
    string += 'with broken path'
  return f'<{string} at {hex(id(self))}>'

def container_repr(self):
  name = self.__class__.__name__
  string = f'{name} container'
  return f'<{string}>'

# Returns all subclasses of given class.
def get_classes(cls):
  classes = []
  attributes = cls.__dict__.items()
  for key, value in attributes:
    if type(value) is type:
      classes.append(value)
  return classes

# Creates asset classes and assigns them to a given container.
def create(container_name: str, asset_list: list):
  container = type(container_name, (object,), {
    '__repr__': container_repr,
    'get_classes': classmethod(get_classes),
  })
  for items in asset_list:
    # Validating data
    assert len(items) == 6
    (
      asset_name,
      fetch_function,
      validate_function,
      install_function,
      pathlist,
      asset_functions,
    ) = items
    assert type(asset_name) is str
    assert len(asset_name) > 0
    if fetch_function:
      assert callable(fetch_function)
    assert callable(validate_function)
    if install_function:
      assert callable(install_function)
    assert type(pathlist) is list
    assert type(asset_functions) is dict
    asset_function_names = asset_functions.keys()
    for function_name in ['get_id', 'get_size', 'get_ui_info']:
      assert function_name in asset_function_names
    # Adding to container
    custom_attributes = {
      '__init__':  asset_init,
      '__pathlist__': pathlist,
      '__fetch__':    staticmethod(fetch_function),
      '__validate__': staticmethod(validate_function),
      '__install__':  staticmethod(install_function),
      '__repr__':  asset_repr,
    }
    asset_class = type(asset_name, (object,), {})
    for key, value in custom_attributes.items():
      setattr(asset_class, key, value)
    for function_name, function in asset_functions.items():
      setattr(asset_class, function_name, function)
    setattr(container, asset_name, asset_class)
  return container()
