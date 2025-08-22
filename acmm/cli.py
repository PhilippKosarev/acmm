#! /usr/bin/env python3

# Imports
from libjam import captain, drawer, typewriter, notebook, clipboard, flashcard
from multiprocessing import Process, SimpleQueue
import sys, os, time

# Internal imports
from . import data, ModFetcher, ModInstaller
mod_fetcher = ModFetcher()
mod_installer = ModInstaller()

# Handling config
HOME = drawer.get_home()
TEMP = drawer.get_temp() + '/acmm'
script_folder = os.path.dirname(os.path.realpath(__file__))
CONFIG_TEMPLATE_FILE = f"{script_folder}/config.toml.in"
CONFIG_DIR = f"{HOME}/.config/acmm"
CONFIG_FILE = f"{CONFIG_DIR}/config.toml"
notebook.check_config(CONFIG_TEMPLATE_FILE, CONFIG_FILE)
config = notebook.read_toml(CONFIG_FILE)

def get_ac_dir():
  # Checking AC_DIR
  ## Likely AC_DIR locations
  assettocorsa = data.get('ac_path_suffix')
  likely_ac_dirs = data.get('likely_ac_dirs')
  ## Getting AC_DIR
  AC_DIR = config.get('paths').get("AC_DIR")
  if AC_DIR == None:
    for directory in likely_ac_dirs:
      # print(directory)
      if drawer.is_folder(directory):
        AC_DIR = directory
  # Checking AC_DIR
  if AC_DIR == None:
    print(
      f"""Assetto Corsa folder not found.
If Assetto Corsa is not installed in the default location, you might need to specify the path to '{assettocorsa}' in '{CONFIG_FILE}'."""
    )
    return
  elif not drawer.is_folder(AC_DIR):
    print(
      f"""Path to Assetto Corsa's folder specified in '{CONFIG_FILE}' does not exist."""
    )
    return
  elif not AC_DIR.endswith(assettocorsa):
    print(
      f"""Path to Assetto Corsa in '{CONFIG_FILE}' is incorrect. It should end with '{assettocorsa}'.
Currently specified AC directory:\n{AC_DIR}"""
    )
    return
  return AC_DIR

include_info = ['size']

def get_category_mods(
  AC_DIR: str,
  mod_category: str,
  category_info: dict,
  queue: SimpleQueue,
  options: dict,
) -> tuple:
  get_function = category_info.get('get_function')
  assets = get_function(AC_DIR, include_info)
  opt_kunos = options.get('kunos')
  opt_all = options.get('all')
  if opt_kunos is False and opt_all is False:
    mods = assets.get('mod')
  elif opt_kunos is True and opt_all is False:
    mods = assets.get('kunos') + assets.get('dlc')
  else:
    mods = assets.get('kunos') + assets.get('dlc') + assets.get('mod')
  size = 0
  for mod in mods:
    size += mod.get('size')
  return_tuple = (mod_category, mods, size)
  queue.put(return_tuple)

def get_mods(AC_DIR: str, options: dict) -> dict:
  start_time = time.time()
  typewriter.print_status('Fetching installed mods...')
  result_dict = {}
  processes = []
  queue = SimpleQueue()
  for mod_category in mod_categories:
    key = mod_category.get('key')
    if key in options:
      if not options.get(key):
        continue
    if 'get_function' not in mod_category:
      continue
    result_dict[key] = mod_category
    process = Process(
      target=get_category_mods, args=(
        AC_DIR, key, mod_category, queue, options
      )
    )
    process.start()
    processes.append(process)
  for process in processes:
    key, mods, size = queue.get()
    if len(mods) > 0:
      result_dict[key]['mods'] = mods
      result_dict[key]['size'] = size
    else:
      result_dict.pop(key)
  for process in processes:
    process.join()
  queue.close()
  end_time = time.time()
  elapsed = end_time - start_time
  typewriter.print(f"Fetched installed mods in {round(elapsed, 2)}s.")
  return result_dict

# Helper functions
def print_mod_categories(mod_categories: dict):
  for category in mod_categories:
    category_info = mod_categories.get(category)
    title = category_info.get('title')
    mods = category_info.get('mods')
    print_mod_category(title, mods)

def print_mod_category(title: str, mods: list):
  size = 0
  for mod in mods:
    size += mod.get('size')
  size, size_units, _ = drawer.get_readable_filesize(size)
  size = round(size, 1)
  size_units = size_units.upper()
  typewriter.print(f"{typewriter.bolden(title)}: ( {len(mods)} | {size} {size_units} )")
  mod_ids = []
  for mod in mods:
    mod_ids.append(mod.get('mod_id'))
  mods_columns = typewriter.list_to_columns(mod_ids, None, 2)
  typewriter.print(f"{mods_columns}\n")

def clean_temp_dir():
  if drawer.exists(TEMP):
    typewriter.print_status("Cleaning temp dir...")
    drawer.delete_folder(TEMP)
  drawer.make_folder(TEMP)


mod_categories = [
  {
    'title': 'Cars', 'key': 'cars',
    'get_function': mod_fetcher.fetch_cars,
  },
  {
    'title': 'Tracks', 'key': 'tracks',
    'get_function': mod_fetcher.fetch_tracks,
  },
  {
    'title': 'PP Filters', 'key': 'ppfilters',
    'get_function': mod_fetcher.fetch_ppfilters,
  },
  {
    'title': 'Weather', 'key': 'weather',
    'get_function': mod_fetcher.fetch_weather,
  },
  {
    'title': 'Apps', 'key': 'apps',
    'get_function': mod_fetcher.fetch_apps,
  },
  # Installable-only categories
  { 'title': 'Custom Shaders Patch', 'key': 'csp'         },
  { 'title': 'CSP Addons',           'key': 'csp-addons'  },
  { 'title': 'Python Apps',          'key': 'python-apps' },
  { 'title': 'Lua Apps',             'key': 'lua-apps'    },
  { 'title': 'GUI Addons',           'key': 'gui-addons'  },
]

# The command line interface for acmm.
class CLI:

  def __init__(self, AC_DIR: str):
    self.AC_DIR = AC_DIR

  # List installed mods.
  def list(self, args, options):
    mod_categories = get_mods(self.AC_DIR, options)
    print_mod_categories(mod_categories)
    return 0

  # Interface to install mods.
  def install(self, args, options):
    clean_temp_dir()
    unpacked = []
    # Processing mod paths
    for path in args:
      if not drawer.exists(path):
        typewriter.print(f"File '{path}' not found.")
        return -1
      # Unpacking
      if drawer.get_filetype(path) != 'folder':
        if not drawer.is_archive_supported(path):
          return typewriter.print(f"Unsupported file '{path}'")
        basename = drawer.get_basename(path)
        def print_extract_progress(done: int, todo: int):
          typewriter.print_progress(f"Extracting '{basename}'", done, todo)
        typewriter.print_status(f"Extracting '{basename}'...")
        try:
          unpacked.append(
            drawer.extract_archive(
              path, TEMP, progress_function=print_extract_progress
            )
          )
        except KeyboardInterrupt:
          typewriter.print('Archive extraction aborted.')
          return 130
      else:
        unpacked.append(path)
    unpacked = clipboard.deduplicate(unpacked)
    # Searching for mods
    typewriter.print_status('Searching for mods...')
    installable_mods = {}
    for path in unpacked:
      try:
        found_categories = mod_installer.find_installable_mods(path, include_info)
      except KeyboardInterrupt:
        typewriter.print('Mod search aborted.')
        return 130
      for found_category in found_categories:
        found_mods = found_categories.get(found_category)
        if found_category in installable_mods:
          installable_mods[found_category] += found_mods
        else:
          installable_mods[found_category] = found_mods
    if len(installable_mods) == 0:
      return typewriter.print('No mods found.')
    for category in installable_mods:
      mods = installable_mods.get(category)
      # Getting category title
      title = category
      for item in mod_categories:
        if item.get('key') == category:
          title = item.get('title')
      print_mod_category(title, mods)
    try:
      if not flashcard.yn_prompt("Install listed mods?"):
        return typewriter.print("Installation cancelled.")
    except KeyboardInterrupt:
      typewriter.print("Installation cancelled.")
      return 130
    # Installing mods
    all_installable_mods = []
    for category in installable_mods:
      mods = installable_mods.get(category)
      all_installable_mods += mods
    def print_install_progress(current_mod: dict, done: int, todo: int):
      current_mod = current_mod.get('mod_id')
      typewriter.print_progress(f"Installing '{current_mod}'", done, todo)
    try:
      installed_mods = mod_installer.install_mods(
        all_installable_mods, self.AC_DIR, print_install_progress
      )
    except KeyboardInterrupt:
      typewriter.print(
        'Installation aborted half-way through. Some mods may have been installed already.'
      )
      return 130
    clean_temp_dir()
    typewriter.print(f"Installed {len(installed_mods)} mods.")
    return 0

  # Interface to remove mods.
  def remove(self, args, options):
    # Fetching mods
    mod_categories = get_mods(self.AC_DIR, options)
    # Getting matching mods
    empty_categories = []
    for category in mod_categories:
      mods = mod_categories.get(category).get('mods')
      matching_mods = []
      for mod in mods:
        mod_id = mod.get('mod_id')
        for search_term in args:
          if search_term.lower() in mod_id.lower():
            matching_mods.append(mod)
      if len(matching_mods) > 0:
        mod_categories[category]['mods'] = matching_mods
      else:
        empty_categories.append(category)
    # Removing empty categories
    for category in empty_categories:
      mod_categories.pop(category)
    # Checking if any match
    if len(mod_categories) == 0:
      print(f"No mods found matching '{search_term}'.")
      return 0
    print_mod_categories(mod_categories)
    try:
      if not flashcard.yn_prompt('Remove the listed mods?'):
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Getting all mods into a list
    all_mods = []
    for category in mod_categories:
      mods = mod_categories.get(category).get('mods')
      all_mods += mods
    num_of_mods = len(all_mods)
    # Deleting mods
    if num_of_mods > 1:
      delay = 1 / num_of_mods
    else:
      delay = 0.3
    deleted_mods = []
    for mod in all_mods:
      mod_id = mod.get('mod_id')
      mod_path = mod.get('path')
      try:
        typewriter.print_status(f"Deleting '{mod_id}'...")
        time.sleep(delay)
        drawer.trash_path(mod_path)
        deleted_mods.append(mod)
      except KeyboardInterrupt:
        typewriter.print(f"Deletion aborted.")
        if len(deleted_mods) > 0:
          last_deleted = deleted_mods[-1].get('mod_id')
          typewriter.print(f"Deleted {len(deleted_mods)} mods. Last deleted: '{last_deleted}'.")
        else:
          typewriter.print('No mods were deleted.')
        return 130
    typewriter.print(f"Deleted {num_of_mods} mods.")
    return 0


def main():
  AC_DIR = get_ac_dir()
  if AC_DIR is None:
    return 1
  cli = CLI(AC_DIR)

  # Commands and options
  description = 'A CLI mod manager for Assetto Corsa'
  commands = {
    'list': {
      'function': cli.list,
      'description': 'Lists installed mods',
    },
    'install': {
      'function': cli.install,
      'description': 'Installs the specified mod(s)',
      'arguments': ['*paths'],
    },
    'remove': {
      'function': cli.remove,
      'description': 'Removes specified mod(s)',
      'arguments': ['*mods'],
    },
  }
  options = {
    'cars': {
      'long': ['car', 'cars'], 'short': ['c'],
      'description': 'Only list/remove cars',
    },
    'tracks': {
      'long': ['track', 'tracks'], 'short': ['t'],
      'description': 'Only list/remove tracks',
    },
    'ppfilters': {
      'long': ['ppfilter', 'ppfilters'], 'short': ['f'],
      'description': 'Only list/remove PP filters',
    },
    'weather': {
      'long': ['weather'], 'short': ['w'],
      'description': 'Only list/remove weather',
    },
    'apps': {
      'long': ['app', 'apps'], 'short': ['a'],
      'description': 'Only list/remove apps',
    },
    'all': {
      'long': ['all'], 'short': ['A'],
      'description': 'Do not filter out Kunos assets',
    },
    'kunos': {
      'long': ['kunos'], 'short': ['k'],
      'description': 'Filter out non Kunos assets',
    },
  }

  # Parsing user input
  function, arguments, options = captain.sail(description, commands, options)

  # Enabling all filters if none are active
  filter_options = ['cars', 'tracks', 'ppfilters', 'weather', 'apps']
  disabled_filters = []
  for filter_option in filter_options:
    if not options.get(filter_option):
      disabled_filters.append(filter_option)
  if len(disabled_filters) == len(filter_options):
    for filter_option in filter_options:
      options[filter_option] = True

  # Running
  return function(arguments, options)

def main_cli():
  return main()

if __name__ == '__main__':
  sys.exit(main())
