# Imports
from libjam import drawer, clipboard

# Internal imports
from .assets import Asset
from .data import data
from .shared import *

# Shorthand vars
asset_paths = data.get('asset-paths')

# Exceptions
class Found(Exception):
  pass

# Helper functions
def search_for_files(path: str, filename: str) -> list:
  matching_files = []
  files = drawer.get_files_recursive(path)
  for file in files:
    basename = drawer.get_basename(file)
    if filename.lower() in basename.lower():
      matching_files.append(file)
  return matching_files


# Find functions
def find_csp(path: str) -> list:
  folders = drawer.get_folders_recursive(path)
  extension_folder = None
  for folder in folders:
    if drawer.get_basename(folder) == 'extension':
      extension_folder = folder
  if extension_folder is None:
    return []
  parent_folder = drawer.get_parent(extension_folder)
  parent_folder_files = drawer.get_files(parent_folder)
  for file in parent_folder_files:
    basename = drawer.get_basename(file)
    if basename == 'dwrite.dll':
      return [parent_folder]
  return []

def find_cars(path: str) -> list:
  mod_paths = search_for_files(path, 'collider.kn5')
  mod_paths = drawer.get_parents(mod_paths)
  return mod_paths

def find_tracks(path: str) -> list:
  files = drawer.get_files_recursive(path)
  kn5_folders = []
  kn5_files = clipboard.match_suffix(files, ".kn5")
  for file in kn5_files:
    basename = drawer.get_basename(file).removesuffix('.kn5')
    parent = drawer.get_parent(file)
    parent_basename = drawer.get_basename(parent)
    if basename == parent_basename:
      kn5_folders.append(parent)
    else:
      kn5_folders.append(parent)
  kn5_folders = clipboard.deduplicate(kn5_folders)
  map_files = clipboard.match_suffix(files, "map.png")
  map_parents = clipboard.deduplicate(drawer.get_parents(map_files))
  mod_paths = clipboard.get_duplicates(kn5_folders, map_parents)
  if mod_paths == []:
    map_parents = clipboard.deduplicate(drawer.get_parents(map_parents))
    mod_paths = clipboard.get_duplicates(kn5_folders, map_parents)
  return mod_paths

def find_ppfilters(path: str) -> list:
  markers = ['[DOF]', '[COLOR]']
  files = drawer.get_files_recursive(path)
  ini_files = clipboard.match_suffix(files, ".ini")
  mod_paths = []
  for file in ini_files:
    try:
      data = open(file, 'r').read()
    except:
      continue
    for marker in markers:
      if marker in data:
        mod_paths.append(file)
        continue
  parents = clipboard.deduplicate(drawer.get_parents(mod_paths))
  if len(parents) == 1:
    mod_paths = drawer.get_all(parents[0])
  mod_paths = clipboard.deduplicate(mod_paths)
  return mod_paths

def find_python_apps(path: str) -> list:
  mod_paths = []
  files = drawer.get_files_recursive(path)
  python_files = clipboard.match_suffix(files, ".py")
  for file in python_files:
    basename = drawer.get_basename(file).removesuffix('.py')
    parent = drawer.get_parent(file)
    parent_basename = drawer.get_basename(parent)
    if basename == parent_basename:
      mod_paths.append(parent)
  return mod_paths

def find_lua_apps(path: str) -> list:
  mod_paths = []
  files = drawer.get_files_recursive(path)
  lua_files = clipboard.match_suffix(files, ".lua")
  for file in lua_files:
    basename = drawer.get_basename(file).removesuffix('.lua')
    parent = drawer.get_parent(file)
    parent_basename = drawer.get_basename(parent)
    if basename == parent_basename:
      mod_paths.append(parent)
  return mod_paths

def find_apps(path: str) -> list:
  return find_python_apps(path) + find_lua_apps(path)

def find_weather(path: str) -> list:
  files = drawer.get_files_recursive(path)
  weather_files = clipboard.match_suffix(files, "/weather.ini")
  weather_folders = clipboard.deduplicate(drawer.get_parents(weather_files))
  weather_parents = clipboard.deduplicate(drawer.get_parents(weather_folders))
  if len(weather_parents) != 1:
    return []
  return weather_folders


# def find_csp_addons(path: str) -> list:
#   folders = drawer.get_folders_recursive(path)
#   extension_folder = None
#   for folder in folders:
#     basename = drawer.get_basename(folder)
#     if basename == 'extension':
#       extension_folder = folder
#   if extension_folder is None:
#     return []
#   extension_addons = []
#   extension_folders = drawer.get_folders(extension_folder)
#   for folder in extension_folders:
#     files = drawer.get_files_recursive(folder)
#     try:
#       for file in files:
#         file_extension = drawer.get_filetype(file)
#         if file_extension == 'lua':
#           raise Found
#     except Found:
#       extension_addons.append(folder)
#       continue
#   return extension_addons

# def find_gui(path: str) -> list:
#   files = drawer.get_files_recursive(path)
#   png_files = clipboard.match_suffix(files, ".png")
#   png_folders = clipboard.deduplicate(drawer.get_parents(png_files))
#   guis = clipboard.deduplicate(drawer.get_parents(png_folders))
#   gui_folders = clipboard.match_suffix(guis, '/gui')
#   if len(gui_folders) == 1:
#     if gui_folders[0] != '':
#       return drawer.get_all(gui_folders[0])
#   return []

# def find_car_skins(folder: str):
  # Getting mod paths
#   cars = self.find_cars(folder)
#   folders = drawer.get_folders_recursive(folder)
#   skin_folders = clipboard.match_suffix(folders, '/skins')
#   parents = drawer.get_parents(skin_folders)
#   skins = clipboard.remove_duplicates(parents, cars)
#   return skins

# def find_track_addons(folder: str):
  # Getting mod paths
#   tracks = self.find_tracks(folder)
#   files = drawer.get_files_recursive(folder)
#   folders = drawer.get_folders_recursive(folder)
#   map_files = clipboard.match_suffix(files, "/map.png")
#   data_folders = clipboard.match_suffix(folders, "/data")
#   ai_folders = clipboard.match_suffix(folders, "/ai")
#   parents = []
#   for item in [map_files, data_folders, ai_folders]:
#     item_parents = drawer.get_parents(drawer.get_parents(item))
#     parents = parents + item_parents
#   parents = clipboard.deduplicate(parents)
#   return parents

# Order is important here
findables = [
  (find_csp, Asset.CSP),
  (find_cars, Asset.Car),
  (find_tracks, Asset.Track),
  (find_ppfilters, Asset.PPFilter),
  (find_weather, Asset.Weather),
  (find_apps, Asset.App),
]

# Finds mods.
class Finder:

  def find(self, directory: str) -> list:
    assets_categories = []
    for item in findables:
      find_function, asset_class = item
      paths = find_function(directory)
      if len(paths) == 0:
        continue
      assets = []
      for path in paths:
        try:
          previously_found_paths = [asset.get_path() for asset in assets]
          for previously_found_path in previously_found_paths:
            if path.startswith(previously_found_path):
              raise Found()
          assets.append(asset_class(path))
        except Found:
          continue
      if len(assets) > 0:
        assets_categories.append(assets)
    return assets_categories
