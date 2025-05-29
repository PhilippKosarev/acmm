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
      if self.options.get('kunos').get('enabled'):
        non_kunos = clipboard.match_suffixes(mod_list, filtered_basename)
        mod_list = clipboard.filter(mod_list, non_kunos)
      elif self.options.get('all').get('enabled'):
        mod_list = mod_list
      else:
        mod_list = clipboard.match_suffixes(mod_list, filtered_basename)
      # Removing `readme_weather.txt` from list
      for item in clipboard.match_suffix(mod_list, 'readme_weather.txt'):
        mod_list.remove(item)
      # Adding additional details
      mod_dict = {}
      for mod in mod_list:
        mod_dict[mod] = {}
        # Adding ui info
        ui_car = f"{mod}/ui/ui_car.json"
        if drawer.is_file(ui_car): mod_dict[mod] = self.safe_read(ui_car)
        ui_track = f"{mod}/ui/ui_track.json"
        if drawer.is_file(ui_track): mod_dict[mod] = self.safe_read(ui_track)
        # Adding badge
        badge = f"{mod}/ui/badge.png"
        if drawer.is_file(badge): mod_dict[mod]['badge'] = badge
        else: mod_dict[mod]['badge'] = None
        # Adding outline
        outline = f"{mod}/ui/outline.png"
        if drawer.is_file(outline): mod_dict[mod]['outline'] = outline
        else: mod_dict[mod]['outline'] = None
        # Addings skins
        skins_dir = f"{mod}/skins"
        if drawer.is_folder(skins_dir): skins = self.get_skins(skins_dir)
        else: skins = None
        mod_dict[mod]['skins'] = skins
        # Adding layouts
        layouts_dir = f"{mod}/skins"
        if drawer.is_folder(layouts_dir): layouts = self.get_layouts(layouts_dir)
        else: layouts = None
        mod_dict[mod]['layouts'] = layouts
      mods[category] = {'title': title, 'mod_list': mod_dict}
    return mods

  def safe_read(self, json_file: str):
    try:
      data = notebook.read_json(json_file)
    except:
      data = {}
    return data

  def get_skins(self, skins_dir):
    if drawer.is_folder(skins_dir) is False:
      return None
    skins = {}
    skin_list = drawer.get_folders(skins_dir)
    for skin in skin_list:
      skins[skin] = {}
      # Adding ui info
      ui_info = f"{skin}/ui_skin.json"
      if drawer.is_file(ui_info):
        ui_dict = self.safe_read(ui_info)
        for item in ui_dict:
          value = ui_dict.get(item)
          skins[skin][item] = value
      # Adding preview image
      preview = f"{skin}/preview.jpg"
      if drawer.is_file(preview):
        skins[skin]['preview'] = preview
      # Adding livery image
      livery = f"{skin}/livery.png"
      if drawer.is_file(livery):
        skins[skin]['livery'] = livery
    return skins

  def get_layouts(self, layouts_dir):
    layouts = {}
    layout_list = drawer.get_folders(layouts_dir)
    for layout in layout_list:
      layouts[layout] = {}
      # Adding ui json stuff
      ui_json = f"{layout}/ui_track.json"
      if drawer.is_file(ui_json):
        layouts[layout] = self.safe_read(ui_json)
      # Adding a preview
      preview = f"{layout}/preview.png"
      if drawer.is_file(preview):
        layouts[layout]['preview'] = preview
    return layouts

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
