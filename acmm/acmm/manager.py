# Imports
from libjam import drawer
import pycountry

# Internal imports
from .data import data
from .base_asset import InvalidAsset
from .assets import Asset
from .extensions import Extension
from .fetch_functions import fetch_functions
from .find_functions import find_functions
from .install_functions import install_functions, InstallMethod

# Useful vars
asset_paths = data.get('asset-paths')

# Exceptions
class InvalidACDir(Exception):
  pass

# Helper functions
def is_subpath_of(item: str, all_paths: list):
  for path in all_paths:
    if item.startswith(path):
      return True
  return False


# Manages assets for Assetto Corsa.
class Manager:

  @staticmethod
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

  def __init__(self, ac_dir: str):
    self.check_ac_dir(ac_dir)
    self.ac_dir = ac_dir

  def fetch_assets(self, asset_class: Asset = None):
    if asset_class is None:
      assets = []
      for asset_class in Asset.get_asset_classes():
        assets += self.fetch_assets(asset_class)
      return assets
    else:
      directory, get_function = fetch_functions.get(asset_class)
      directory = f'{self.ac_dir}/{directory}'
      assets = []
      paths = get_function(directory)
      for path in paths:
        try:
          assets.append(asset_class(path))
        except InvalidAsset:
          continue
      return assets

  def get_asset_flag(asset: Asset) -> str:
    ui_info = asset.get_ui_info()
    country = ui_info.get('country')
    if country is not None:
      country = country.replace('.', '').strip()
      country = pycountry.countries.get(name=country)
      if country is not None:
        iso_3166 = country.alpha_3
        flag = f'{AC_DIR}/content/gui/NationFlags/{iso_3166}.png'
        if drawer.is_file(flag):
          return flag

  def fetch_extension(self, extension: Extension):
    try:
      return extension(self.ac_dir)
    except InvalidAsset:
      return None

  def find(self, directory: str) -> list:
    found_paths = []
    found_assets = []
    for asset_class in find_functions:
      find_function = find_functions.get(asset_class)
      for path in find_function(directory):
        if is_subpath_of(path, found_paths):
          continue
        found_paths.append(path)
        found_assets.append(asset_class(path))
    return found_assets

  def install(
    self,
    asset: Asset or Extension,
    install_method: InstallMethod,
  ) -> Asset or Extension:
    install_function, install_dir = install_functions.get(type(asset))
    if install_function is None:
      raise NotImplementedError()
    return install_function(
      asset, f'{self.ac_dir}/{install_dir}', install_method,
    )
