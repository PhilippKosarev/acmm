# Imports
from libjam import drawer, clipboard

# Internal imports
from .data import data
from .assets import Asset
from .extensions import Extension

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
  if drawer.is_folder(path):
    folders.insert(0, path)
  for folder in folders:
    files = [drawer.get_basename(file) for file in drawer.get_files(folder)]
    subfolders = [drawer.get_basename(subfolder) for subfolder in drawer.get_folders(folder)]
    if 'dwrite.dll' in files and 'extension' in subfolders:
      return [folder]
  return []

def find_cars(path: str) -> list:
  mod_paths = search_for_files(path, 'collider.kn5')
  mod_paths = drawer.get_parents(mod_paths)
  return mod_paths

def find_tracks(path: str) -> list:
  files = drawer.get_files_recursive(path)
  kn5_folders = []
  kn5_files = [file for file in files if file.endswith('.kn5')]
  for file in kn5_files:
    basename = drawer.get_basename(file).removesuffix('.kn5')
    parent = drawer.get_parent(file)
    parent_basename = drawer.get_basename(parent)
    if basename == parent_basename:
      kn5_folders.append(parent)
    else:
      kn5_folders.append(parent)
  kn5_folders = clipboard.deduplicate(kn5_folders)
  map_files = [file for file in files if file.endswith('map.png')]
  map_parents = clipboard.deduplicate(drawer.get_parents(map_files))
  mod_paths = clipboard.get_duplicates(kn5_folders, map_parents)
  if mod_paths == []:
    map_parents = clipboard.deduplicate(drawer.get_parents(map_parents))
    mod_paths = clipboard.get_duplicates(kn5_folders, map_parents)
  return mod_paths

def find_ppfilters(path: str) -> list:
  markers = ['[DOF]', '[COLOR]']
  files = drawer.get_files_recursive(path)
  ini_files = [file for file in files if file.endswith('.ini')]
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
  python_files = [file for file in files if file.endswith('.py')]
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
  lua_files = [file for file in files if file.endswith('.lua')]
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
  weather_files = [file for file in files if file.endswith('/weather.ini')]
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
find_functions = {
  Asset.Car: find_cars,
  Asset.Track: find_tracks,
  Asset.PPFilter: find_ppfilters,
  Asset.Weather: find_weather,
  Asset.App: find_apps,
}
