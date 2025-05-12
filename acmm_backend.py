# Imports
import sys
from libjam import Drawer, Clipboard, Notebook, Flashcard

# Jam classes
drawer = Drawer()
clipboard = Clipboard()
notebook = Notebook()
flashcard = Flashcard()

# Setting relative paths
HOME = drawer.get_home()
TEMP = f"{drawer.get_temp()}/accm"

# Content dirs
assettocorsa = "steamapps/common/assettocorsa"
content_dirs = [f"{HOME}/.local/share/Steam/{assettocorsa}",
f"{HOME}/.var/app/com.valvesoftware.Steam/data/Steam/{assettocorsa}",
f"C:/Program Files (x86)/Steam/{assettocorsa}"]

# Configuration paths
CONFIG_DIR = f"{HOME}/.config/acmm"
CONFIG_FILE = f"{CONFIG_DIR}/config.toml"

# Parsing config
notebook.check_config(CONFIG_FILE)
config = notebook.read_toml(CONFIG_FILE)
# Parsing config filters
def get_filter(i: str): return config.get('filters').get(i)
kunos_cars      = get_filter('kunos_cars')
kunos_tracks    = get_filter('kunos_tracks')
kunos_apps      = get_filter('kunos_apps')
kunos_ppfilters = get_filter('kunos_ppfilters')
# Parsing AC_DIR
AC_DIR = config.get('paths').get("AC_DIR")
# Checking AC_DIR
if AC_DIR == None:
  for directory in content_dirs:
    if drawer.is_folder(directory):
      AC_DIR = directory
if AC_DIR == None:
  print(f"Assetto Corsa not found.\nIf Assetto Corsa is not installed in the default location, \
you might need to specify the path to '/steamapps/common/assettocorsa' \
in '{CONFIG_FILE}'.")
  sys.exit(-1)
if drawer.is_folder(AC_DIR) is False:
  print(f"Path to Assetto Corsa's folder specified in '{CONFIG_FILE}' does not exist.")
  sys.exit(-1)
if AC_DIR.endswith(assettocorsa) is False:
  print(f"Path to Assetto Corsa in '{CONFIG_FILE}' is incorrect. It should end with '/{assettocorsa}'.")
  sys.exit(-1)

# Manages mods
class ModManager:

  def __init__(self, options):
    # Mod categories
    self.options = options
    self.mod_categories = {
    "cars": {'title':         "Cars",         'directory': f'{AC_DIR}/content/cars',
    'filter_list': kunos_cars,      'enabled': options.get('list_cars'),
    'find_function': 'find_cars'},

    "tracks": {'title':       "Tracks",       'directory': f'{AC_DIR}/content/tracks',
    'filter_list': kunos_tracks,    'enabled': options.get('list_tracks'),
    'find_function': 'find_tracks'},

    "python_apps": {'title':   "Python apps", 'directory': f'{AC_DIR}/apps/python',
    'filter_list': kunos_apps,      'enabled': options.get('list_apps'),
    'find_function': 'find_python_apps'},

    "ppfilters": {'title':    "PP Filters",   'directory': f'{AC_DIR}/system/cfg/ppfilters',
    'filter_list': kunos_ppfilters, 'enabled': options.get('list_ppfilters'),
    'find_function': 'find_ppfilters'},
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
      mod_list = eval(f"mod_finder.{find_function}('{folder}')")
      if mod_list == []:
        continue
      if mod_list is not None:
        mods[category] = {'title': title, 'mod_list': mod_list, 'install_location': install_location}
    return mods

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
      path = drawer.extract_archive(path, TEMP)
    else:
      return False
    return path

  # Installs given mods
  def install_mods(self, mods: dict, progress_function=None):
    for category in mods:
      install_location = mods.get(category).get('install_location')
      mod_list = mods.get(category).get('mod_list')
      copied = 0
      to_copy = len(mod_list)
      for mod in mod_list:
        basename = drawer.basename(mod)
        final_location = f"{install_location}/{basename}"
        if drawer.exists(final_location):
          drawer.trash(final_location)
        drawer.copy(mod, final_location)
        copied += 1
        if progress_function is not None:
          exec(f"progress_function({copied}, {to_copy})")
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

# Finds mods in a given dir
class ModFinder():
  def find_cars(self, folder:str):
    mod_list = drawer.search_for_files("collider.kn5", folder)
    mod_list = drawer.get_parent(mod_list)
    mod_list = clipboard.deduplicate(mod_list)
    return mod_list
    
  def find_tracks(self, folder:str):
    files = drawer.get_files_recursive(folder)
    folders = drawer.get_folders_recursive(folder)
    # Finding a kn5 files with the same name as parent dir
    kn5_folders = []
    kn5_files = clipboard.match_suffix(files, ".kn5")
    for file in kn5_files:
      basename = drawer.basename(file).removesuffix('.kn5')
      parent = drawer.get_parent(file)
      parent_basename = drawer.basename(parent)
      if basename == parent_basename:
        kn5_folders.append(parent)
    # Finding map.png file
    map_files = clipboard.match_suffix(files, "map.png")
    # Creating a mod_list out of dirs that have all required contents
    kn5_parents = clipboard.deduplicate(drawer.get_parent(kn5_folders))
    map_parents = clipboard.deduplicate(drawer.get_parent(map_files))
    mod_list = clipboard.get_duplicates(kn5_parents, map_parents)
    # In case it has multiple layouts
    if mod_list == []:
      map_parents = clipboard.deduplicate(drawer.get_parent(map_parents))
      mod_list = clipboard.get_duplicates(kn5_parents, map_parents)
    return mod_list
    
  def find_python_apps(self, folder:str):
    mod_list = []
    files = drawer.get_files_recursive(folder)
    folders = drawer.get_folders_recursive(folder)
    python_files = clipboard.match_suffix(files, ".py")
    for file in python_files:
      basename = drawer.basename(file).removesuffix('.py')
      parent = drawer.get_parent(file)
      parent_basename = drawer.basename(parent)
      if basename == parent_basename:
        mod_list.append(parent)
    return mod_list

  def find_ppfilters(self, folder:str):
    markers = ['[DOF]', '[COLOR]']
    mod_list = []
    files = drawer.get_files_recursive(folder)
    folders = drawer.get_folders_recursive(folder)
    ini_files = clipboard.match_suffix(files, ".ini")
    for file in ini_files:
      try:
        data = open(file, 'r').read()
      except:
        continue
      for marker in markers:
        if marker in data:
          mod_list.append(file)
          continue
    mod_list = clipboard.deduplicate(mod_list)
    return mod_list
