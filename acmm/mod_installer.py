# Imports
from libjam import drawer, clipboard

# Internal imports
from .data import data
from .mod_finder import ModFinder
mod_finder = ModFinder()
from .info_gatherer import InfoGatherer
info_gatherer = InfoGatherer()

# tuple format: (find_function, delete_mod_before_installing?)
installable_mod_categories = [
  {
    'category-id': 'csp',
    'find-function': mod_finder.find_csp,
    'info-function': info_gatherer.get_csp_info,
    'install-dir': '',
    'install-mode': 'csp',
  },
  {
    'category-id': 'cars',
    'find-function': mod_finder.find_cars,
    'info-function': info_gatherer.get_car_info,
    'install-dir': data.get('asset-paths').get('cars'),
    'install-mode': 'clean',
  },
  {
    'category-id': 'tracks',
    'find-function': mod_finder.find_tracks,
    'info-function': info_gatherer.get_track_info,
    'install-dir': data.get('asset-paths').get('tracks'),
    'install-mode': 'clean',
  },
  {
    'category-id': 'ppfilters',
    'find-function': mod_finder.find_ppfilters,
    'info-function': info_gatherer.get_ppfilter_info,
    'install-dir': data.get('asset-paths').get('ppfilters'),
    'install-mode': 'clean',
  },
  {
    'category-id': 'weather',
    'find-function': mod_finder.find_weather,
    'info-function': info_gatherer.get_weather_info,
    'install-dir': data.get('asset-paths').get('weather'),
    'install-mode': 'clean',
  },
  {
    'category-id': 'python-apps',
    'find-function': mod_finder.find_python_apps,
    'info-function': info_gatherer.get_app_info,
    'install-dir': data.get('asset-paths').get('apps') + '/python',
    'install-mode': 'clean',
  },
  {
    'category-id': 'lua-apps',
    'find-function': mod_finder.find_lua_apps,
    'info-function': info_gatherer.get_app_info,
    'install-dir': data.get('asset-paths').get('apps') + '/lua',
    'install-mode': 'clean',
  },
  {
    'category-id': 'gui-addons',
    'find-function': mod_finder.find_gui,
    'info-function': info_gatherer.get_generic_info,
    'install-dir': 'content/gui',
    'install-mode': 'clean',
  },
  {
    'category-id': 'csp-addons',
    'find-function': mod_finder.find_csp_addons,
    'info-function': info_gatherer.get_generic_info,
    'install-dir': 'extension',
    'install-mode': 'overwrite',
  },
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
    all_installable_mods = []
    installable_mods_by_category = {}
    for item in installable_mod_categories:
      # Getting info
      find_function = item.get('find-function')
      info_function = item.get('info-function')
      install_dir = item.get('install-dir')
      install_mode = item.get('install-mode')
      # Finding mod paths
      found_paths = find_function(directory)
      found_paths.sort()
      # Getting mod info
      found_mods = []
      for path in found_paths:
        mod_info, origin = info_function(path, include)
        mod_info['install-dir'] = install_dir
        mod_info['install-mode'] = install_mode
        found_mods.append(mod_info)
      # Filtering out already found mods
      marked_mods = []
      for found_mod in found_mods:
        found_mod_path = found_mod.get('path').removeprefix(directory)
        for installable_mod in all_installable_mods:
          installable_mod_path = installable_mod.get('path').removeprefix(directory)
          if found_mod_path.startswith(installable_mod_path):
            marked_mods.append(found_mod)
      for marked_mod in marked_mods:
        found_mods.remove(marked_mod)
      # Adding filtered found mods
      if len(found_mods) == 0:
        continue
      all_installable_mods += found_mods
      category_id = item.get('category-id')
      installable_mods_by_category[category_id] = found_mods
    return installable_mods_by_category

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
      if install_mode == 'clean':
        if drawer.exists(install_final_path):
          drawer.delete_path(install_final_path)
        drawer.copy(mod_path, install_final_path)
      elif  install_mode == 'overwrite':
        drawer.copy(mod_path, install_final_path, overwrite=True)
      elif  install_mode == 'csp':
        # Copying dwrite
        if drawer.exists(AC_DIR+'/dwrite.dll'):
          drawer.delete_path(AC_DIR+'/dwrite.dll')
        drawer.copy(mod_path+'/dwrite.dll', AC_DIR+'/dwrite.dll')
        # Copying extension
        if drawer.exists(AC_DIR+'/extension'):
          drawer.delete_path(AC_DIR+'/extension')
        drawer.copy(mod_path+'/extension', AC_DIR+'/extension')
      else:
        raise NotImplementedError(f"Install mode '{install_mode}' is not implemented.")
      iteration += 1
      installed_mods.append(mod)
    return installed_mods
