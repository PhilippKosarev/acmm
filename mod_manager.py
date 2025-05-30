# Imports
import sys

# Jamming imports
from libjam import Drawer, Clipboard, Notebook, Flashcard
drawer = Drawer()
clipboard = Clipboard()
notebook = Notebook()
flashcard = Flashcard()

# Internal imports
from data import Data
data = Data()
from mod_finder import ModFinder
mod_finder = ModFinder()

# Getting important paths
TEMP = f"{drawer.get_temp()}/accm"

# Manages mods
class ModManager:

  def __init__(self, config: dict, options: dict):
    AC_DIR = config.get('paths').get('AC_DIR')
    self.AC_DIR = AC_DIR
    def get_filter(string: str):
      return data.get(string)
    self.options = options
    def get_option(opt: str):
      return options.get(opt).get('enabled')
    # Defining mod categories
    self.mod_categories = {
      "cars": {'title':         "Cars",        'directory': f'{AC_DIR}/content/cars',
      'filter_list': get_filter('kunos_cars'), 'enabled': get_option('car'),
      'find_function': mod_finder.find_cars},

      "tracks": {'title':       "Tracks",        'directory': f'{AC_DIR}/content/tracks',
      'filter_list': get_filter('kunos_tracks'), 'enabled': get_option('track'),
      'find_function': mod_finder.find_tracks},

      "python_apps": {'title':   "Python apps", 'directory': f'{AC_DIR}/apps/python',
      'filter_list': get_filter('kunos_apps'),  'enabled': get_option('python'),
      'find_function': mod_finder.find_python_apps},

      "lua_apps": {'title':   "Lua apps", 'directory': f'{AC_DIR}/apps/lua',
      'filter_list': [],            'enabled': get_option('lua'),
      'find_function': mod_finder.find_lua_apps},

      "ppfilters": {'title':    "PP Filters",       'directory': f'{AC_DIR}/system/cfg/ppfilters',
      'filter_list': get_filter('kunos_ppfilters'), 'enabled': get_option('ppfilter'),
      'find_function': mod_finder.find_ppfilters},

      "weather": {'title':    "Weather",          'directory': f'{AC_DIR}/content/weather',
      'filter_list': get_filter('kunos_weather'), 'enabled': get_option('weather'),
      'find_function': mod_finder.find_weather},
    }

    self.meta_categories = {
      'car_skins': {'title': "Car skins", 'directory': f"{AC_DIR}/content/cars",
      'find_function': mod_finder.find_car_skins, 'keep_old': True},

      'track_additions': {'title': "Track add-ons", 'directory': f"{AC_DIR}/content/tracks",
      'find_function': mod_finder.find_track_addons, 'keep_old': True},

      'extensions': {'title': "Extensions", 'directory': f"{AC_DIR}/extension",
      'find_function': mod_finder.find_extensions, 'keep_old': True},

      'gui': {'title': "GUI", 'directory': f"{AC_DIR}/content/gui",
      'find_function': mod_finder.find_gui, 'keep_old': True},
    }

  # Creates directory lists for each mod_category
  def get_installed_mods(self):
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
      # Getting and filtering mod files
      mod_dict = {}
      for item in drawer.get_all(directory):
        mod_id = drawer.basename(item).removesuffix('.ini')
        if self.options.get('kunos').get('enabled') and clipboard.is_string_in_list(filter_list, mod_id) is False:
          continue
        if self.options.get('all').get('enabled') is False and clipboard.is_string_in_list(filter_list, mod_id):
          continue
        mod_dict[mod_id] = {'path': item}
      # Removing `readme_weather.txt` from list
      if clipboard.is_string_in_list(mod_dict, 'readme_weather.txt'):
        mod_dict.pop('readme_weather.txt')
      # Adding additional details
      for mod_id in mod_dict:
        mod_path = mod_dict.get(mod_id).get('path')
        # Adding ui info
        ui_car = f"{mod_path}/ui/ui_car.json"
        if drawer.is_file(ui_car): mod_dict[mod_id] = mod_dict.get(mod_id) | self.safe_read(ui_car)
        ui_track = f"{mod_path}/ui/ui_track.json"
        if drawer.is_file(ui_track): mod_dict[mod_id] = mod_dict.get(mod_id) | self.safe_read(ui_track)
        # Adding badge
        badge = f"{mod_path}/ui/badge.png"
        if drawer.is_file(badge): mod_dict[mod_id]['badge'] = badge
        else: mod_dict[mod_id]['badge'] = None
        # Adding outline
        outline = f"{mod_path}/ui/outline.png"
        if drawer.is_file(outline): mod_dict[mod_id]['outline'] = outline
        else: mod_dict[mod_id]['outline'] = None
        # Addings skins
        mod_dict[mod_id]['skins'] = self.get_skins(mod_path)
        # Adding layouts
        layouts_dir = f"{mod_path}/ui"
        mod_dict[mod_id]['layouts'] = self.get_layouts(mod_path)
      mods[category] = {'title': title, 'mod_list': mod_dict}
    return mods

  def safe_read(self, json_file: str):
    try:    data = notebook.read_json(json_file)
    except: data = {}
    return  data

  def get_skins(self, mod_path: str):
    skins_dir = f"{mod_path}/skins"
    if drawer.is_folder(skins_dir) is False: return None
    skins = {}
    for folder in drawer.get_folders(skins_dir):
      skin_id = drawer.basename(folder)
      skins[skin_id] = {'path': folder}
      # Adding ui info
      ui_info = f"{folder}/ui_skin.json"
      if drawer.is_file(ui_info):
        ui_dict = self.safe_read(ui_info)
        for item in ui_dict:
          value = ui_dict.get(item)
          skins[skin_id][item] = value
      # Adding preview image
      preview = f"{folder}/preview.jpg"
      if drawer.is_file(preview):
        skins[skin_id]['preview'] = preview
      # Adding livery image
      livery = f"{folder}/livery.png"
      if drawer.is_file(livery):
        skins[skin_id]['livery'] = livery
    # Sorting skins by priority
    # Sorting skins by priority, if present
    skins = self.sort_by_priority(skins)
    return skins

  def get_layouts(self, mod_path):
    layouts_dir = f"{mod_path}/ui"
    if drawer.is_folder(layouts_dir) is False: return None
    layouts = {}
    for folder in drawer.get_folders(layouts_dir):
      layout_id = drawer.basename(folder)
      layouts[layout_id] = {'path': folder}
      # Adding ui json stuff
      ui_json = f"{folder}/ui_track.json"
      if drawer.is_file(ui_json):
        layouts[layout_id] = self.safe_read(ui_json)
      # Adding a preview
      preview = f"{folder}/preview.png"
      if drawer.is_file(preview):
        layouts[layout_id]['preview'] = preview
    layouts = self.sort_by_priority(layouts)
    return layouts

  def sort_by_priority(self, dictionary):
    # Checking if able to sort by priority
    has_priority = True
    for item in dictionary:
      if dictionary.get(item).get('priority') is None:
        return dictionary
    # Sorting
    dictionary = dict( sorted(dictionary.items(), key=lambda v: v[1]['priority']) )
    return dictionary

  # Finding mods in given folder
  def find_mods(self):
    mods = {}
    for category in self.mod_categories:
      enabled = self.mod_categories.get(category).get('enabled')
      if enabled is False:
        continue
      title = self.mod_categories.get(category).get('title')
      install_location = self.mod_categories.get(category).get('directory')
      find_function = self.mod_categories.get(category).get('find_function')
      mod_finder = ModFinder()
      folders = drawer.get_folders(TEMP)
      mod_list = []
      for folder in folders:
        mod_list = mod_list + find_function(folder)
      if mod_list == [] or mod_list == [TEMP]:
        continue
      mods[category] = {'title': title, 'mod_list': mod_list, 'install_location': install_location}
    return mods

  # Finding meta mods
  def find_meta_mods(self):
    meta_mods = {}
    for category in self.meta_categories:
      title = self.meta_categories.get(category).get('title')
      install_location = self.meta_categories.get(category).get('directory')
      find_function = self.meta_categories.get(category).get('find_function')
      keep_old = self.meta_categories.get(category).get('keep_old')
      mod_finder = ModFinder()
      mod_list = find_function(TEMP)
      if mod_list == [] or mod_list == [TEMP]:
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
    if drawer.is_folder(path):
      basename = drawer.basename(path)
      path = drawer.copy(path, f"{TEMP}/{basename}")
      return path
    elif drawer.is_archive(path):
      path = drawer.extract_archive(path, TEMP, progress_function)
      return path
    else:
      return None

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

  def remove_mods(self, mods: dict):
    for category in mods:
      mod_list = mods.get(category).get('mod_list')
      for mod in mod_list:
        path = mods.get(category).get('mod_list').get(mod).get('path')
        if path.startswith(self.AC_DIR) and (path.endswith(mod) or path.endswith(mod + '.ini')):
          drawer.trash(mod)
        else:
          print(f"Aborting unsafe deletion of mod '{mod}' at '{path}'.")
