# Imports
from pathlib import Path

# Internal imports
from . import utils

# Functions
def get_id(self) -> str:
  return self.path.name

def get_size(self) -> int:
  return utils.get_dir_size(self.path)

def delete(self):
  utils.unlink_dir(self.path)
