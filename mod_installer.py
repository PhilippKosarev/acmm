# Imports
from libjam import drawer, clipboard
# Internal imports
from data import data
from mod_finder import ModFinder
mod_finder = ModFinder()
from info_gatherer import InfoGatherer
info_gatherer = InfoGatherer()

# tuple format: (find_function, delete_mod_before_installing?)
installable_mod_categories = [
  # Cars
  {
    'category-id': 'cars',
    'find-function': mod_finder.find_cars,
    'info-function': info_gatherer.get_car_info,
    'install-dir': data.get('asset-paths').get('cars'),
    'install-mode': 'delete-then-install',
  },
  # Tracks
  {
    'category-id': 'tracks',
    'find-function': mod_finder.find_tracks,
    'info-function': info_gatherer.get_track_info,
    'install-dir': data.get('asset-paths').get('tracks'),
    'install-mode': 'delete-then-install',
  },
  # 'apps': (mod_finder.find_apps, True),
  # 'ppfilters': (mod_finder.find_ppfilters, True),
  # 'weather': (mod_finder.find_weather, True),
  # (mod_finder.find_extensions, False),
  # (mod_finder.find_gui, False),
  # (mod_finder.find_car_skins, False),
  # (mod_finder.find_track_addons, False),
]

# Installs mods.
class ModInstaller:

  def find_installable_mods(self, directory: str, include: list = []) -> list:
    # Checking path
    if not drawer.exists(directory):
      raise FileNotFoundError(f"Directory '{directory}' does not exist.")
    if not drawer.is_folder(directory):
      raise NotADirectoryError(f"Path '{directory}' does not lead to a directory.")
    # Getting installable mods
    installable_mods = []
    for item in installable_mod_categories:
      # Getting info
      find_function = item.get('find-function')
      info_function = item.get('info-function')
      install_dir = item.get('install-dir')
      install_mode = item.get('install-mode')
      # Finding mod paths
      found_paths = find_function(directory, include)
      # Getting mod info
      found_mods = []
      for path in found_paths:
        mod_info, origin = info_function(path, include)
        mod_info['install-dir'] = install_dir
        mod_info['install-mode'] = install_mode
        found_mods.append(mod_info)
      # Filtering out duplicates
      found_mods = clipboard.filter(found_mods, installable_mods)
      installable_mods += found_mods
    return installable_mods

  def install_mods(self, mods: list, AC_DIR: str, progress_function = None):
    n_of_mods = len(mods)
    iteration = 0
    installed_mods = []
    for mod in mods:
      # Getting info
      install_dir = f"{AC_DIR}/{mod.get('install-dir')}"
      install_mode = mod.get('install-mode')
      mod_path = mod.get('path')
      # Progress report
      if progress_function is not None:
        progress_function(mod, iteration + 1, n_of_mods)
      # Installing
      install_final_path = f"{install_dir}/{drawer.get_basename(mod_path)}"
      if install_mode == 'delete-then-install':
        if drawer.exists(install_final_path):
          drawer.delete_path(install_final_path)
      else:
        raise NotImplementedError(f"Install mode '{install_mode}' is not implemented.")
      drawer.copy(mod_path, install_final_path)
      iteration += 1
      installed_mods.append(mod)
    return installed_mods
