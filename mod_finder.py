# Jamming imports
from libjam import drawer, clipboard
# Internal imports
from info_gatherer import InfoGatherer
info_gatherer = InfoGatherer()

# Helper functions
def search_for_files(path: str, filename: str) -> list:
  matching_files = []
  files = drawer.get_files_recursive(path)
  for file in files:
    basename = drawer.get_basename(file)
    if filename.lower() in basename.lower():
      matching_files.append(file)
  return matching_files

# Finds mods.
class ModFinder:

  def find_cars(self, path: str, include: list = []) -> list:
    mod_paths = search_for_files(path, 'collider.kn5')
    mod_paths = drawer.get_parents(mod_paths)
    return mod_paths

  def find_tracks(self, folder: str, include: list = []) -> list:
    files = drawer.get_files_recursive(folder)
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

  def find_python_apps(self, folder: str):
    # Getting mod paths
    mod_paths = []
    files = drawer.get_files_recursive(folder)
    python_files = clipboard.match_suffix(files, ".py")
    for file in python_files:
      basename = drawer.get_basename(file).removesuffix('.py')
      parent = drawer.get_parent(file)
      parent_basename = drawer.get_basename(parent)
      if basename == parent_basename:
        mod_paths.append(parent)
    # Getting mod info
    mods = []
    for path in mod_paths:
      mod, origin = info_gatherer.get_track_info(path, include)
      mods.append(mod)
    return mods

  def find_lua_apps(self, folder: str, include: list = []):
    # Getting mod paths
    mod_paths = []
    files = drawer.get_files_recursive(folder)
    python_files = clipboard.match_suffix(files, ".lua")
    for file in python_files:
      basename = drawer.get_basename(file).removesuffix('.lua')
      parent = drawer.get_parent(file)
      parent_basename = drawer.get_basename(parent)
      if basename == parent_basename:
        mod_paths.append(parent)
    # Getting mod info
    mods = []
    for path in mod_paths:
      mod, origin = info_gatherer.get_track_info(path, include)
      mods.append(mod)
    return mods

  def find_ppfilters(self, folder: str, include: list = []) -> list:
    # Getting mod paths
    markers = ['[DOF]', '[COLOR]']
    files = drawer.get_files_recursive(folder)
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
    # Getting mod info
    mods = []
    for path in mod_paths:
      mod, origin = info_gatherer.get_track_info(path, include)
      mod['install-dir'] = data.get('asset-paths').get('ppfilters')
      mod['install-mode'] = 'replace'
      mods.append(mod)
    return mods

  def find_weather(self, folder: str, include: list = []) -> list:
    # Getting mod paths
    files = drawer.get_files_recursive(folder)
    weather_files = clipboard.match_suffix(files, "/weather.ini")
    weather_folders = clipboard.deduplicate(drawer.get_parents(weather_files))
    weather_parents = clipboard.deduplicate(drawer.get_parents(weather_folders))
    mod_paths = weather_parents
    if len(weather_parents) != 1:
      return []
    # Getting mod info
    mods = []
    for path in mod_paths:
      mod, origin = info_gatherer.get_weather_info(path, include)
      mod['install-dir'] = data.get('asset-paths').get('weather')
      mod['install-mode'] = 'replace'
      mods.append(mod)
    return mods

  def find_extensions(self, folder: str, include: list = []) -> list:
    # Getting mod paths
    files = drawer.get_files_recursive(folder)
    lua_files = clipboard.match_suffix(files, ".lua")
    lua_folders = clipboard.deduplicate(drawer.get_parents(lua_files))
    extensions = clipboard.deduplicate(drawer.get_parents(lua_folders))
    mod_paths = clipboard.deduplicate(drawer.get_parents(extensions))
    mod_paths = clipboard.match_suffix(mod_paths, '/extension')
    if len(mod_paths) != 1:
      return []
    if mod_paths[0] != '':
      mod_paths = drawer.get_folders(mod_paths[0])

  def find_gui(self, folder: str):
    # Getting mod paths
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
    # Getting mod paths
    cars = self.find_cars(folder)
    folders = drawer.get_folders_recursive(folder)
    skin_folders = clipboard.match_suffix(folders, '/skins')
    parents = drawer.get_parents(skin_folders)
    skins = clipboard.remove_duplicates(parents, cars)
    return skins

  def find_track_addons(self, folder: str):
    # Getting mod paths
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
