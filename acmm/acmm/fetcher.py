# Imports
from libjam import drawer
from enum import Enum

# Internal imports
from .assets import Asset
from .data import data
from .shared import *

# Shorthand vars
asset_paths = data.get('asset-paths')

def get_app_paths(directory: str):
  paths = []
  for folder in drawer.get_folders(directory):
    paths += drawer.get_folders(folder)
  return paths

# Asset categories
class FetchableAssetCategory(Enum):
  CARS      = Asset.Car,      asset_paths.get('cars'),      drawer.get_folders
  TRACKS    = Asset.Track,    asset_paths.get('tracks'),    drawer.get_folders
  PPFILTERS = Asset.PPFilter, asset_paths.get('ppfilters'), drawer.get_files
  WEATHER   = Asset.Weather,  asset_paths.get('weather'),   drawer.get_folders
  APPS      = Asset.App,      asset_paths.get('apps'),      get_app_paths

# Fetches installed assets.
class Fetcher:

  def __init__(self, ac_dir: str):
    check_ac_dir(ac_dir)
    self.ac_dir = ac_dir

  def fetch(self, category: FetchableAssetCategory):
    asset_class, directory, get_function = category.value
    directory = f'{self.ac_dir}/{directory}'
    assets = []
    paths = get_function(directory)
    assets = [asset_class(path) for path in paths]
    return assets

  def fetch_csp(self):
    return Asset.CSP(self.ac_dir)

  def search_by_id(self, category: FetchableAssetCategory, asset_id: str):
    asset_id = asset_id.lower()
    asset_class, directory, get_function = category.value
    directory = f'{self.ac_dir}/{directory}'
    paths = get_function(directory)
    matching = []
    for path in paths:
      if asset_id in drawer.get_basename(path).lower():
        matching.append(asset_class(path))
    return matching
