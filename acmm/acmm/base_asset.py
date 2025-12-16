# Imports
from pathlib import Path

# Exceptions
class InvalidAsset(Exception):
  pass

# The base for all assets and extensions.
class BaseAsset:
  def __init__(self, path):
    # Checking methods
    required_methods = [
      self.validate,
      self.get_id,
      self.get_size,
      self.get_ui_info,
      self.delete,
    ]
    for method in required_methods:
      assert callable(method)
    # Checking given path
    path = Path(path)
    if not path.exists():
      raise FileNotFoundError(f"Path '{path}' does not exist")
    if not self.validate(path):
      raise InvalidAsset()
    # Initialising data
    self.data = {
      'path': path,
    }

  # Returns path to asset.
  def get_path(self) -> Path:
    return self.data.get('path')
