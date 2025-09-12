# Imports
from libjam import drawer

# Internal imports
from .data import data
from .shared import *

# Shorthand vars
asset_paths = data.get('asset-paths')

# Exceptions
class InvalidACDir(Exception):
  pass

# Functions
def check_ac_dir(ac_dir: str):
  if not drawer.is_folder(ac_dir):
    raise FileNotFoundError(
      f"Specified AC directory at '{ac_dir}' does not exist."
    )
  for path in asset_paths.values():
    if not drawer.is_folder(f'{ac_dir}/{path}'):
      raise InvalidACDir(
        f"Missing required path '{path}' in AC directory '{ac_dir}'."
      )
