# Imports
from libjam import drawer
from enum import Enum

# Internal imports
from .assets import AppLang, Asset
from .extensions import Extension
from .data import data

# Shorthand vars
asset_paths = data.get('asset-paths')

# Enums
class InstallMethod(Enum):
  UPDATE = 0
  CLEAN = 1

# Install functions
def base_install(
  from_path: str, to_path: str, install_method: InstallMethod,
) -> str:
  if install_method is InstallMethod.CLEAN:
    if drawer.exists(to_path):
      drawer.trash_path(to_path)
    final_location = drawer.copy(from_path, to_path)
  elif install_method is InstallMethod.UPDATE:
    final_location = drawer.copy(from_path, to_path, overwrite=True)
  else:
    raise ValueError(f"Invalid install_method '{install_method}'")
  return final_location

def install_generic(
  asset: Asset, install_dir: str, install_method: InstallMethod,
) -> Asset:
  # Getting info
  asset_path = asset.get_path()
  basename = drawer.get_basename(asset_path)
  final_location = f'{install_dir}/{basename}'
  # Installing
  final_location = base_install(asset_path, final_location, install_method)
  # Returning
  asset.data['path'] = final_location
  return asset

def install_app(
  asset: Asset.App, install_dir: str, install_method: InstallMethod,
) -> Asset.App:
  # Getting info
  lang_to_folder = {
    AppLang.PYTHON: 'python',
    AppLang.LUA: 'lua',
  }
  asset_path = asset.get_path()
  app_lang = lang_to_folder.get(asset.get_lang())
  basename = drawer.get_basename(asset_path)
  final_location = f'{install_dir}/{app_lang}/{basename}'
  # Installing
  final_location = base_install(asset_path, final_location, install_method)
  # Returning
  asset.data['path'] = final_location
  return asset

def install_csp(
  asset: Asset.CSP, install_dir: str, install_method: InstallMethod,
) -> Asset.CSP:
  asset_path = asset.get_path()
  for path in [asset_path + '/dwrite.dll', asset_path + '/extension']:
    basename = drawer.get_basename(path)
    local_install_dir = f'{install_dir}/{basename}'
    base_install(path, local_install_dir, install_method)
  asset.data['path'] = install_dir
  return asset

# Mapping install functions
install_functions = {
  Asset.Car:      ( install_generic, asset_paths.get('cars')      ),
  Asset.Track:    ( install_generic, asset_paths.get('tracks')    ),
  Asset.PPFilter: ( install_generic, asset_paths.get('ppfilters') ),
  Asset.Weather:  ( install_generic, asset_paths.get('weather')   ),
  Asset.App:      ( install_app,     asset_paths.get('apps')      ),
  Extension.CSP:  ( install_csp,     ''                           ),
}
