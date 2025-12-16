# Imports
from pathlib import Path
import pycountry

# Internal imports
from . import (
  data,
  shared,
  fetch_functions,
  install_functions,
)
from .base_asset import InvalidAsset
from .assets import Asset
from .extensions import Extension

# Useful vars
InstallMethod = install_functions.InstallMethod
asset_dirs = data.get('asset-dirs')

# Exceptions
class InvalidAssettoDir(Exception):
  pass

# Internal functions
def find_assets_in_dir(self, path: Path) -> list:
  # Vars
  asset_classes = [Extension.CSP] + Asset.get_classes()
  subpaths = [path] + shared.get_paths_recursive(path)
  path_str = str(path)
  found_paths = []
  assets = []
  # Main loop
  for asset_class in asset_classes:
    for subpath in subpaths:
      subpath_relative = str(subpath).removeprefix(path_str)
      is_subpath = False
      for found_path in found_paths:
        if subpath_relative.startswith(found_path):
          is_subpath = True
          break
      if is_subpath:
        continue
      try:
        asset = asset_class(subpath)
      except InvalidAsset:
        continue
      assets.append(asset)
      found_paths.append(subpath_relative)
  # Returning
  return assets

# Manages assets for Assetto Corsa.
class Manager:

  @staticmethod
  def check_assetto_dir(assetto_dir):
    assetto_dir = Path(assetto_dir)
    if not assetto_dir.exists():
      raise FileNotFoundError(
        f"Specified assetto_dir '{assetto_dir}' does not exist"
      )
    if not assetto_dir.is_dir():
      raise NotADirectoryError(
        f"Specified assetto_dir '{assetto_dir}' is not a directory"
      )
    for pathlist in asset_dirs.values():
      path = assetto_dir / Path(*pathlist)
      if not path.is_dir():
        raise InvalidAssettoDir(
          f"Missing required directory '{subpath}' in assetto_dir"
        )
    return assetto_dir

  def __init__(self, assetto_dir):
    self.assetto_dir = self.check_assetto_dir(assetto_dir)

  def fetch_assets(self, asset_class: Asset = None) -> list:
    if asset_class is None:
      assets = []
      for asset_class in Asset.get_classes():
        assets += self.fetch_assets(asset_class)
      return assets
    pair = fetch_functions.get(asset_class)
    if not pair:
      raise TypeError(f"Invalid asset type '{asset_type}'")
    get_function, category = pair
    pathlist = asset_dirs.get(category)
    asset_dir = self.assetto_dir / Path(*pathlist)
    found_paths = get_function(asset_dir)
    assets = []
    for subpath in found_paths:
      try:
        asset = asset_class(subpath)
        assets.append(asset)
      except InvalidAsset:
        continue
    return assets

  def fetch_extension(self, extension_class: Extension):
    valid = extension_class.validate(self.assetto_dir)
    if valid:
      return extension_class(self.assetto_dir)

  def fetch_csp_versions(self) -> dict:
    # importing on-demand for faster overall import times
    import requests
    # links
    base_link =  'https://acstuff.club/patch/'
    info_link = base_link + '?info='
    get_link = base_link + '?get='
    # Version start and end positions
    version = [0, 1, 75]
    cutoff = (0, 3, 0)
    found_lead = False
    # Main loop
    found = {}
    while True:
      version_string = '.'.join([str(n) for n in version])
      link = info_link + version_string
      # print(link)
      request = requests.get(link)
      if request.status_code != 200:
          raise ConnectionError()
      if request.text != 'Unknown version':
        found_lead = True
        found[version_string] = {
          'info': request.content,
          'download-link': get_link + version_string,
        }
        version[2] += 1
      else:
        if (
          version[0] >= cutoff[0] and
          version[1] >= cutoff[1] and
          version[2] >= cutoff[2]
        ):
          break
        if found_lead:
          version[1] += 1
          version[2] = 0
        else:
          version[2] += 1
        found_lead = False
    return found

  def find_assets(self, path) -> list:
    path = Path(path)
    subdirs = [subpath for subpath in path.iterdir() if subpath.is_dir()]
    assets = []
    for subdir in subdirs:
      assets += find_assets_in_dir(self, subdir)
    return assets

  def install(
    self,
    asset: Asset or Extension,
    install_method: InstallMethod,
  ) -> Asset or Extension:
    asset_type = type(asset)
    pair = install_functions.get(asset_type)
    if not pair:
      raise TypeError(f"Invalid asset type '{asset_type}'")
    install_function, category = pair
    if category:
      pathlist = asset_dirs.get(category)
    else:
      pathlist = []
    install_dir = self.assetto_dir / Path(*pathlist)
    return install_function(asset, install_dir, install_method)

  def get_asset_flag(self, asset: Asset) -> str:
    ui_info = asset.get_ui_info()
    if not ui_info:
      return
    country = ui_info.get('country')
    if not country:
      return
    country = country.replace('.', '').strip()
    country = pycountry.countries.get(name=country)
    if country is None:
      return
    iso_3166 = country.alpha_3
    flag_basename = iso_3166 + '.png'
    flags_dir = self.assetto_dir / 'content' / 'gui' / 'NationFlags'
    flag_file = flags_dir / flag_basename
    if not flag_file.is_file():
      return
    return flag_file
