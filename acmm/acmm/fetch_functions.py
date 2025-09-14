# Imports
from libjam import drawer

# Internal imports
from .assets import Asset
from .data import data

# Shorthand vars
asset_paths = data.get('asset-paths')

# Fetch functions
def get_app_paths(directory: str):
  paths = []
  for folder in drawer.get_folders(directory):
    paths += drawer.get_folders(folder)
  return paths

# Fetch info
fetch_functions = {
  Asset.Car:      (asset_paths.get('cars'),      drawer.get_folders),
  Asset.Track:    (asset_paths.get('tracks'),    drawer.get_folders),
  Asset.PPFilter: (asset_paths.get('ppfilters'), drawer.get_files),
  Asset.Weather:  (asset_paths.get('weather'),   drawer.get_folders),
  Asset.App:      (asset_paths.get('apps'),      get_app_paths),
}
