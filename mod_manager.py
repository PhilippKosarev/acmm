# Imports
import sys

# Jamming imports
from libjam import Drawer, Clipboard, Notebook, Flashcard
# Jamming shorthands
drawer = Drawer()
clipboard = Clipboard()
notebook = Notebook()
flashcard = Flashcard()

# Internal imports
from mod_finder import ModFinder
# Internal shorthands
mod_finder = ModFinder()

# Getting important paths
HOME = drawer.get_home()
TEMP = f"{drawer.get_temp()}/accm"

# Setting config paths
CONFIG_DIR = f"{HOME}/.config/acmm"
CONFIG_FILE = f"{CONFIG_DIR}/config.toml"

# Parsing config
notebook.check_config(CONFIG_FILE)
config = notebook.read_toml(CONFIG_FILE)

# Checking AC_DIR
## Likely AC_DIR locations
assettocorsa = "steamapps/common/assettocorsa"
content_dirs = [f"{HOME}/.local/share/Steam/{assettocorsa}",
f"{HOME}/.var/app/com.valvesoftware.Steam/data/Steam/{assettocorsa}",
f"C:/Program Files (x86)/Steam/{assettocorsa}"]
## Getting AC_DIR
AC_DIR = config.get('paths').get("AC_DIR")
if AC_DIR == None:
  for directory in content_dirs:
    if drawer.is_folder(directory):
      AC_DIR = directory
# Checking AC_DIR
if AC_DIR == None:
  print(f"Assetto Corsa not found.\n\
If Assetto Corsa is not installed in the default location, \
you might need to specify the path to '/steamapps/common/assettocorsa' \
in '{CONFIG_FILE}'.")
  sys.exit(-1)
if drawer.is_folder(AC_DIR) is False:
  print(f"Path to Assetto Corsa's folder specified in '{CONFIG_FILE}' does not exist.")
  sys.exit(-1)
if AC_DIR.endswith(assettocorsa) is False:
  print(f'''Path to Assetto Corsa in '{CONFIG_FILE}' is incorrect. It should end with '/{assettocorsa}'.)
Currently specified AC directory:\n{AC_DIR}''')
  sys.exit(-1)


# Manages mods
class ModManager:

  def __init__(self, options):
    # Mod categories
    self.options = options
    def get_filter(i: str):
      return config.get('filters').get(i)
    # Defining mod categories
    self.mod_categories = {
      "cars": {'title':         "Cars",        'directory': f'{AC_DIR}/content/cars',
      'filter_list': get_filter('kunos_cars'), 'enabled': options.get('list_cars'),
      'find_function': mod_finder.find_cars},

      "tracks": {'title':       "Tracks",        'directory': f'{AC_DIR}/content/tracks',
      'filter_list': get_filter('kunos_tracks'), 'enabled': options.get('list_tracks'),
      'find_function': mod_finder.find_tracks},

      "python_apps": {'title':   "Python apps", 'directory': f'{AC_DIR}/apps/python',
      'filter_list': get_filter('kunos_apps'),  'enabled': options.get('list_python'),
      'find_function': mod_finder.find_python_apps},

      "lua_apps": {'title':   "Lua apps", 'directory': f'{AC_DIR}/apps/lua',
      'filter_list': [],            'enabled': options.get('list_lua'),
      'find_function': mod_finder.find_lua_apps},

      "ppfilters": {'title':    "PP Filters",       'directory': f'{AC_DIR}/system/cfg/ppfilters',
      'filter_list': get_filter('kunos_ppfilters'), 'enabled': options.get('list_ppfilters'),
      'find_function': mod_finder.find_ppfilters},

      "weather": {'title':    "Weather",          'directory': f'{AC_DIR}/content/weather',
      'filter_list': get_filter('kunos_weather'), 'enabled': options.get('list_weather'),
      'find_function': mod_finder.find_weather},
    }

    self.meta_categories = {
    'extensions': {'title': "Extensions", 'directory': f"{AC_DIR}/extension",
    'find_function': mod_finder.find_extensions, 'keep_old': True},

    'gui': {'title': "GUI", 'directory': f"{AC_DIR}/content/gui",
    'find_function': mod_finder.find_gui, 'keep_old': True},
    }

  # Creates directory lists for each mod_category
  def get_mods(self):
    # Adding mod categories to dict
    mods = {}
    for category in self.mod_categories:
      enabled = self.mod_categories.get(category).get('enabled')
      if enabled is False:
        continue
      directory = self.mod_categories.get(category).get('directory')
      if drawer.is_folder(directory) is False:
        continue
      title = self.mod_categories.get(category).get('title')
      filter_list = self.mod_categories.get(category).get('filter_list')
      mod_list = drawer.get_all(directory)
      mod_basename = drawer.basename(mod_list)
      filtered_basename = clipboard.filter(mod_basename, filter_list)
      if self.options.get('list_all') is False and self.options.get('only_kunos') is False:
        mod_list = clipboard.match_suffixes(mod_list, filtered_basename)
      if self.options.get('only_kunos') is True:
        non_kunos = clipboard.match_suffixes(mod_list, filtered_basename)
        mod_list = clipboard.filter(mod_list, non_kunos)
      # Removing `readme_weather.txt` from list
      for item in clipboard.match_suffix(mod_list, 'readme_weather.txt'):
        mod_list.remove(item)
      mods[category] = {'title': title, 'mod_list': mod_list}
    return mods

  # Finding mods in given folder
  def find_mods(self, folder: str):
    mods = {}
    for category in self.mod_categories:
      enabled = self.mod_categories.get(category).get('enabled')
      if enabled is False:
        continue
      title = self.mod_categories.get(category).get('title')
      install_location = self.mod_categories.get(category).get('directory')
      find_function = self.mod_categories.get(category).get('find_function')
      mod_finder = ModFinder()
      mod_list = find_function(folder)
      if mod_list == []:
        continue
      if mod_list is not None:
        mods[category] = {'title': title, 'mod_list': mod_list, 'install_location': install_location}
    return mods

  # Finding meta mods
  def find_meta_mods(self, folder: str):
    meta_mods = {}
    for category in self.meta_categories:
      title = self.meta_categories.get(category).get('title')
      install_location = self.meta_categories.get(category).get('directory')
      find_function = self.meta_categories.get(category).get('find_function')
      keep_old = self.meta_categories.get(category).get('keep_old')
      mod_finder = ModFinder()
      mod_list = find_function(folder)
      if mod_list == []:
        continue
      if mod_list is not None:
        meta_mods[category] = {
          'title': title, 'mod_list': mod_list,
          'install_location': install_location, 'keep_old': keep_old
        }
    return meta_mods

  def clean_temp_dir(self):
    if drawer.is_folder(TEMP):
      drawer.delete_folder(TEMP)
    drawer.make_folder(TEMP)

  def extract_mod(self, path: str, progress_function=None):
    if drawer.exists(path) is False:
      return None
    self.clean_temp_dir()
    if drawer.is_folder(path):
      basename = drawer.basename(path)
      path = drawer.copy(path, f"{TEMP}/{basename}")
    elif drawer.is_archive(path):
      path = drawer.extract_archive(path, TEMP, progress_function)
    else:
      return False
    return path

  # Installs given mods
  def install_mods(self, mods: dict, progress_function=None):
    for category in mods:
      install_location = mods.get(category).get('install_location')
      mod_list = mods.get(category).get('mod_list')
      keep_old = mods.get(category).get('keep_old')
      copied = 0
      to_copy = len(mod_list)
      for mod in mod_list:
        basename = drawer.basename(mod)
        final_location = f"{install_location}/{basename}"
        if keep_old is not True and drawer.exists(final_location):
          drawer.trash(final_location)
          drawer.copy(mod, final_location)
        else:
          drawer.copy(mod, final_location, overwrite=True)
        copied += 1
        if progress_function is not None:
          progress_function(copied, to_copy)
    self.clean_temp_dir()

  def search_mods(self, search_term: str):
    # Getting mods dict
    mods = self.get_mods()
    marked_mods = {}
    # Filtering out non matching mods
    for category in mods:
      if mods[category].get('enabled') is False:
        continue
      title = mods.get(category).get('title')
      mod_list = mods.get(category).get('mod_list')
      mod_basename = drawer.basename(mod_list)
      mods_found = clipboard.search(mod_basename, search_term)
      mods_found = clipboard.match_suffixes(mod_list, mods_found)
      if mods_found == []:
        continue
      marked_mods[category] = {
      'title': title,
      'mod_list': mods_found
      }
    # Returning matching mods
    return marked_mods

  def remove_mods(self, mods: dict):
    for category in mods:
      mod_list = mods.get(category).get('mod_list')
      for mod in mod_list:
        drawer.trash(mod)
