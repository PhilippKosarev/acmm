# Imports
from libjam import drawer

# Exceptions
class InvalidAsset(Exception):
  pass

# The base for all assets and extensions.
class BaseAsset:
  def __init__(self, path: str):
    # Checking methods
    required_methods = [
      self.get_id,
      self.get_size,
      self.get_ui_info,
    ]
    for method in required_methods:
      assert callable(method)
    # Checking files
    if not drawer.exists(path):
      raise FileNotFoundError(f"File '{path}' not found.")
    if hasattr(self, 'checks'):
      for function, value in self.checks:
        if not function(path, value):
          raise InvalidAsset(
            f"Failed check '{function.__name__}'."
          )
    # Initialising data
    self.data = {
      'path': path,
    }

  # Returns path to asset.
  def get_path(self) -> str:
    return self.data.get('path')
