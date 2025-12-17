# Imports
from enum import Enum

# Enums
class AssetOrigin(Enum):
  MOD = 0
  KUNOS = 1
  DLC = 2

class AppLang(Enum):
  PYTHON = 0
  LUA = 1

class InstallMethod(Enum):
  UPDATE = 0
  CLEAN = 1

# Exceptions
class InvalidAsset(Exception):
  pass

class InvalidAssettoDir(Exception):
  pass
