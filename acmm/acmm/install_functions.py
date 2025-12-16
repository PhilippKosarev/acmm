# Imports
from pathlib import Path
from enum import Enum
import shutil

# Internal imports
from .assets import AppLang, Asset
from .extensions import Extension

# Enums
class InstallMethod(Enum):
  UPDATE = 0
  CLEAN = 1

# Install functions
def base_install(
  source: Path, destination: Path, install_method: InstallMethod,
) -> str:
  if install_method is InstallMethod.CLEAN:
    if destination.exists():
      destination.unlink()
    source.copy_into(destination)
  elif install_method is InstallMethod.UPDATE:
    if source.is_dir():
      destination = destination / source.name
      shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
      source.copy_into(destination)
  else:
    raise ValueError(f"Invalid install_method '{install_method}'")

def install_generic(
  asset: Asset, install_dir: str, install_method: InstallMethod,
) -> Asset:
  # Getting info
  asset_path = asset.get_path()
  base_install(asset_path, install_dir, install_method)
  asset.data['path'] = install_dir / asset_path.name
  return asset

def install_app(
  asset: Asset.App, install_dir: str, install_method: InstallMethod,
) -> Asset.App:
  # Getting info
  lang_to_dir = {
    AppLang.PYTHON: 'python',
    AppLang.LUA: 'lua',
  }
  asset_path = asset.get_path()
  lang_dir = lang_to_dir.get(asset.get_lang())
  install_dir = install_dir / lang_dir
  base_install(asset_path, install_dir, install_method)
  asset.data['path'] = install_dir / asset_path.name
  return asset

def install_csp(
  asset: Asset.CSP, install_dir: Path, install_method: InstallMethod,
) -> Asset.CSP:
  asset_path = asset.get_path()
  dwrite_file = asset_path / 'dwrite.dll'
  extension_dir = asset_path / 'extension'
  for destination in [dwrite_file, extension_dir]:
    base_install(destination, install_dir, install_method)
  asset.data['path'] = install_dir
  return install_dir

# Mapping install functions
functions = {
  Extension.CSP:  (install_csp,     None       ),
  Asset.Car:      (install_generic, 'cars'     ),
  Asset.Track:    (install_generic, 'tracks'   ),
  Asset.PPFilter: (install_generic, 'ppfilters'),
  Asset.Weather:  (install_generic, 'weather'  ),
  Asset.App:      (install_app,     'apps'     ),
}

def get(key, default=None, /):
  return functions.get(key, default)

def items():
  return functions.items()

def keys():
  return functions.keys()

def values():
  return functions.values()
