#!/bin/python3

# Imports
from libjam import Typewriter, Drawer, Clipboard, Notebook, Flashcard
import sys, os, glob, shutil, tomllib

# Jam classes
typewriter = Typewriter()
drawer = Drawer()
clipboard = Clipboard()
notebook = Notebook()
flashcard = Flashcard()

# Setting relative paths
TEMP = '/tmp/acmm'
HOME = os.getenv('HOME')
LOCAL = f"{HOME}/.local"
# Content dirs
AC_DIR = f"{LOCAL}/share/Steam/steamapps/common/assettocorsa"
# Config files
CONFIG_DIR = f"{HOME}/.config/acmm"
CONFIG_FILE = f"{CONFIG_DIR}/config.toml"
# Checking if config files exist
drawer = Drawer()
if not drawer.is_folder(CONFIG_DIR):
  drawer.make_folder(CONFIG_DIR)
if not drawer.is_file(CONFIG_FILE):
  drawer.make_file(CONFIG_FILE)
# Parsing config
notebook = Notebook()
config = notebook.read_toml(CONFIG_FILE)
# Assigning vars from config
def get_filter(i: str): return config.get('filters').get(i)
kunos_cars      = get_filter('kunos_cars')
kunos_tracks    = get_filter('kunos_tracks')
kunos_apps      = get_filter('kunos_apps')
kunos_ppfilters = get_filter('kunos_ppfilters')

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
  def get_mods(self, content_dir):
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
      mod_list = drawer.get_folders(directory)
      if self.options.get('list_all') is False:
        mod_list = drawer.filter_by_basename(mod_list, filter_list)
      if self.options.get('only_kunos') is True:
        mod_list = drawer.filter_by_basename(filter_list, mod_list)
      mods[category] = {'title': title, 'mod_list': mod_list}
    if mods == None:
      print("No mods found.")
      exit()
    return mods
  
  # Printing mods
  def list(self):
    mods = self.get_mods(AC_DIR)
    print_mod_categories(mods)
  
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

  def install(self, path: str):
    # Checking if file exists
    if drawer.is_file(path) is False and drawer.is_folder(path) is False:
      print(f"File '{path}' does not exist.")
      exit()
    # Checking temp dir
    clean_temp_dir()
    # Extracting archive if needed
    if drawer.is_archive(path):
      typewriter.print_status("Extracting archive...")
      path = drawer.extract_archive(path, TEMP)
    # Searching for mods
    typewriter.print_status("Searching for mods...")
    mods = self.find_mods(path)
    if mods == {}:
      typewriter.print("No mods found.")
      return
    typewriter.print(typewriter.bolden("Mods found:"))
    print_mod_categories(mods)
    if flashcard.yn_prompt("Install listed mods?") is False:
      print("Installation cancelled.")
      return
    # Installing mods
    typewriter.print_status("Installing...")
    for category in mods:
      install_location = mods.get(category).get('install_location')
      mod_list = mods.get(category).get('mod_list')
      for mod in mod_list:
        basename = drawer.basename(mod)
        final_location = f"{install_location}/{basename}"
        if drawer.is_folder(final_location):
          drawer.trash_folder(final_location)
        drawer.copy_folder(mod, final_location)
    clean_temp_dir()
    typewriter.print("Installation complete.")
  
  def remove_mods(self, search_term: str):
    mods = self.get_mods(AC_DIR)
    marked_mods = []
    for category in mods:
      title = mods.get(category).get('title')
      mod_list = mods.get(category).get('mod_list')
      mod_list = clipboard.match_substring(search_term, mod_list)
      print_mod_category(title, mod_list)
      marked_mods += mod_list
    if marked_mods == []:
      print(f"No mods match '{search_term}'.")
      exit()
    if flashcard.yn_prompt('Remove the listed mods?'):
      drawer.trash_folder(marked_mods)
      print('Deleted.')
    else:
      print('Deletion cancelled.')


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
    kn5_parents = drawer.get_parent(kn5_folders)
    map_parents = drawer.get_parent(map_files)
    mod_list = clipboard.match_list(kn5_parents, map_parents)
    return mod_list
    
  def find_python_apps(self, folder:str):
    mod_list = []
    python_files = drawer.search_for_filetype("py", folder)
    for file in python_files:
      basename = drawer.basename(file).removesuffix('.py')
      parent = drawer.get_parent(file)
      parent_basename = drawer.basename(parent)
      if basename == parent_basename:
        mod_list.append(parent)
    return mod_list
  def find_ppfilters(self, folder:str):
    pass

def print_mod_category(title: str, mod_list: list):
  mod_list = drawer.basename(mod_list)
  entries = len(mod_list)
  # Quitting if there's nothing to print
  if entries == 0:
    return
  # Printing
  print(f"{typewriter.bolden(title)}: ({entries})")
  mods_columns = typewriter.list_to_columns(mod_list, None, 4)
  print(f"{mods_columns}")

def print_mod_categories(mods):
  for category in mods:
    title = mods.get(category).get('title')
    mod_list = mods.get(category).get('mod_list')
    print_mod_category(title, mod_list)

def clean_temp_dir():
    typewriter.print_status("Cleaning temporary directory...")
    if drawer.is_folder(TEMP):
      drawer.delete_folder(TEMP)
    drawer.make_folder(TEMP)
