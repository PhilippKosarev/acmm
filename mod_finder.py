# Jamming imports
from libjam import drawer, clipboard

# Helper functions
def search_for_files(path: str, filename: str) -> list:
  matching_files = []
  files = drawer.get_files_recursive(path)
  for file in files:
    basename = drawer.basename(file)
    if filename.lower() in basename.lower():
      matching_files.append(file)
  return matching_files

# Finds mods in a given directory
class ModFinder:
  def find_cars(self, folder: str):
    mod_list = search_for_files("collider.kn5", folder)
    mod_list = drawer.get_parents(mod_list)
    mod_list = clipboard.deduplicate(mod_list)
    return mod_list

  def find_tracks(self, folder: str):
    files = drawer.get_files_recursive(folder)
    # Finding a kn5 files with the same name as parent dir
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
    # Finding map.png file
    map_files = clipboard.match_suffix(files, "map.png")
    # Creating a mod_list out of dirs that have all required contents
    map_parents = clipboard.deduplicate(drawer.get_parents(map_files))
    mod_list = clipboard.get_duplicates(kn5_folders, map_parents)
    # print(mod_list)
    # In case it has multiple layouts
    if mod_list == []:
      map_parents = clipboard.deduplicate(drawer.get_parents(map_parents))
      mod_list = clipboard.get_duplicates(kn5_folders, map_parents)
    return mod_list

  def find_python_apps(self, folder: str):
    mod_list = []
    files = drawer.get_files_recursive(folder)
    python_files = clipboard.match_suffix(files, ".py")
    for file in python_files:
      basename = drawer.get_basename(file).removesuffix('.py')
      parent = drawer.get_parent(file)
      parent_basename = drawer.get_basename(parent)
      if basename == parent_basename:
        mod_list.append(parent)
    return mod_list

  def find_lua_apps(self, folder: str):
    mod_list = []
    files = drawer.get_files_recursive(folder)
    python_files = clipboard.match_suffix(files, ".lua")
    for file in python_files:
      basename = drawer.get_basename(file).removesuffix('.lua')
      parent = drawer.get_parent(file)
      parent_basename = drawer.get_basename(parent)
      if basename == parent_basename:
        mod_list.append(parent)
    return mod_list

  def find_ppfilters(self, folder: str):
    markers = ['[DOF]', '[COLOR]']
    files = drawer.get_files_recursive(folder)
    ini_files = clipboard.match_suffix(files, ".ini")
    mod_list = []
    for file in ini_files:
      try:
        data = open(file, 'r').read()
      except:
        continue
      for marker in markers:
        if marker in data:
          mod_list.append(file)
          continue
    parents = clipboard.deduplicate(drawer.get_parents(mod_list))
    if len(parents) == 1:
      mod_list = drawer.get_all(parents[0])
    mod_list = clipboard.deduplicate(mod_list)
    return mod_list

  def find_weather(self, folder: str):
    files = drawer.get_files_recursive(folder)
    weather_files = clipboard.match_suffix(files, "/weather.ini")
    weather_folders = clipboard.deduplicate(drawer.get_parents(weather_files))
    weather_parents = clipboard.deduplicate(drawer.get_parents(weather_folders))
    if len(weather_parents) == 1:
      return weather_folders
    return []

  def find_extensions(self, folder: str):
    files = drawer.get_files_recursive(folder)
    lua_files = clipboard.match_suffix(files, ".lua")
    lua_folders = clipboard.deduplicate(drawer.get_parents(lua_files))
    extensions = clipboard.deduplicate(drawer.get_parents(lua_folders))
    extensions_folders = clipboard.deduplicate(drawer.get_parents(extensions))
    extensions_folders = clipboard.match_suffix(extensions_folders, '/extension')
    if len(extensions_folders) == 1:
      if extensions_folders[0] != '':
        return drawer.get_folders(extensions_folders[0])
    return []

  def find_gui(self, folder: str):
    files = drawer.get_files_recursive(folder)
    png_files = clipboard.match_suffix(files, ".png")
    png_folders = clipboard.deduplicate(drawer.get_parents(png_files))
    guis = clipboard.deduplicate(drawer.get_parents(png_folders))
    gui_folders = clipboard.match_suffix(guis, '/gui')
    if len(gui_folders) == 1:
      if gui_folders[0] != '':
        return drawer.get_all(gui_folders[0])
    return []

  def find_car_skins(self, folder: str):
    cars = self.find_cars(folder)
    folders = drawer.get_folders_recursive(folder)
    skin_folders = clipboard.match_suffix(folders, '/skins')
    parents = drawer.get_parents(skin_folders)
    skins = clipboard.remove_duplicates(parents, cars)
    return skins

  def find_track_addons(self, folder: str):
    tracks = self.find_tracks(folder)
    files = drawer.get_files_recursive(folder)
    folders = drawer.get_folders_recursive(folder)
    map_files = clipboard.match_suffix(files, "/map.png")
    data_folders = clipboard.match_suffix(folders, "/data")
    ai_folders = clipboard.match_suffix(folders, "/ai")
    parents = []
    for item in [map_files, data_folders, ai_folders]:
      item_parents = drawer.get_parents(drawer.get_parents(item))
      parents = parents + item_parents
    parents = clipboard.deduplicate(parents)
    return parents
