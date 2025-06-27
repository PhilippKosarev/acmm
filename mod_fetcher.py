# Imports
import pycountry

# Jamming
from libjam import Drawer, Notebook
drawer = Drawer()
notebook = Notebook()

# Internal imports
from data import Data
data = Data()

# Helper functions
def get_existing(path: str):
  if drawer.exists(path):
    return path
  else:
    return None

def get_flag(AC_DIR, country: str):
  if country is None:
    return None
  country = country.replace('.', '').strip()
  country = pycountry.countries.get(name=country)
  if country is None:
    return None
  iso_3166 = country.alpha_3
  flag = f"{AC_DIR}/content/gui/NationFlags/{iso_3166}.png"
  if drawer.is_file(flag):
     return flag
  else:
    return None

def get_origin(mod_id, mod_path, kunos_assets, json_filename: str):
  if mod_id in kunos_assets:
    mod_files = drawer.basename(drawer.get_files(mod_path))
    if f'dlc_{json_filename}' in mod_files:
      origin = 'dlc'
    else:
      origin = 'kunos'
  else:
    origin = 'mod'
  return origin

def get_ui_info(mod_path, origin, json_filename):
  if origin == 'dlc':
    json_filename = f'dlc_{json_filename}'
  json_file = f"{mod_path}/ui/{json_filename}"
  if drawer.is_file(json_file):
    return notebook.read_json(json_file)
  else:
    return {}

def get_app_info(mod_path: str, lang: str):
  try:
    if lang == 'python':
      json_file = f"{mod_path}/ui/ui_app.json"
      ui_info = notebook.read_json(json_file)
    elif lang == 'lua':
      manifest = f"{mod_path}/manifest.ini"
      try:
        ui_info = notebook.read_ini(manifest).get('ABOUT')
      except AttributeError:
        return {}
    return ui_info
  except FileNotFoundError:
    return {}

def get_ppfilter_info(mod_path: str):
  ui_info = notebook.read_ini(mod_path)
  if 'ABOUT' in ui_info:
    return ui_info.get('ABOUT')
  else:
    return {}

def get_weather_info(mod_path: str):
  ini_file = f"{mod_path}/weather.ini"
  ui_info = notebook.read_ini(ini_file)
  if 'LAUNCHER' in ui_info:
    launcher_info = ui_info.get('LAUNCHER')
  else:
    launcher_info = {}
  if '__LAUNCHER_CM' in ui_info:
    cm_info = ui_info.get('__LAUNCHER_CM')
  else:
    cm_info = {}
  ui_info = launcher_info | cm_info
  return ui_info


def get_skins(mod_path, include):
  folder = f"{mod_path}/skins"
  if drawer.is_folder(folder) is False:
    return None
  skin_dirs = drawer.get_folders(folder)
  skins = {}
  for skin_path in skin_dirs:
    # Adding basic skin information
    skin_id = drawer.basename(skin_path)
    skin_info = {'path': skin_path}
    # Getting optional skin info
    ## Adding UI info
    if 'ui' in include:
      json_file = f"{skin_path}/ui_skin.json"
      if drawer.is_file(json_file):
        ui_info = notebook.read_json(json_file)
        skin_info.update(ui_info)
    ## Adding livery
    if 'livery' in include:
      image_file = f"{skin_path}/livery.png"
      if drawer.is_file(image_file):
        skin_info['livery'] = image_file
      else:
        skin_info['livery'] = None
    ## Adding preview
    if 'preview' in include:
      image_file = f"{skin_path}/preview.jpg"
      if drawer.is_file(image_file):
        skin_info['preview'] = image_file
      else:
        skin_info['preview'] = None
    # Adding skin to skins
    skins[skin_id] = skin_info
  # Returning skins
  if skins == {}:
    return None
  else:
    return skins


# Class
class ModFetcher:

  # Returns cars
  # Available 'include' options:
  # ui, flag, badge, preview, logo, skins, size
  def get_cars(self, AC_DIR, include: list = []):
    cars = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = drawer.get_folders(f'{AC_DIR}/content/cars')
    for mod_path in folders:
      # Establishing basic mod properties
      mod_id = drawer.basename(mod_path)
      mod_info = {'path': mod_path}
      # Getting car origin
      origin = get_origin(mod_id, mod_path, data.kunos_cars, 'ui_car.json')
      # Getting optional information
      ## Getting filesize info
      if 'size' in include:
        mod_info['size'] = drawer.get_file_size(mod_path)
      ## Getting UI info
      if 'ui' in include:
        ui_info = get_ui_info(mod_path, origin, 'ui_car.json')
        # Getting country flag
        if 'flag' in include:
          if 'country' in ui_info:
            ui_info['flag'] = get_flag(AC_DIR, ui_info.get('country'))
        mod_info.update(ui_info)
      ## Getting badge
      if 'badge' in include:
        image_file = f"{mod_path}/ui/badge.png"
        mod_info['badge'] = get_existing(image_file)
      ## Getting preview
      if 'preview' in include:
        if origin == 'dlc': image_file = 'dlc_preview.png'
        else: image_file = 'preview.png'
        image_file = f"{mod_path}/ui/{image_file}"
        mod_info['preview'] = get_existing(image_file)
      ## Getting logo
      if 'logo' in include:
        image_file = f"{mod_path}/logo.png"
        mod_info['logo'] = get_existing(image_file)
      ## Getting skins
      if 'skins' in include:
        mod_info['skins'] = get_skins(mod_path, include)
      # Adding car to dict
      cars[origin][mod_id] = mod_info
    return cars


  # Returns tracks
  # Available 'include' options:
  # ui, flag, outline, preview, skins, size
  def get_tracks(self, AC_DIR, include: list = []):
    tracks = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = drawer.get_folders(f'{AC_DIR}/content/tracks')
    for mod_path in folders:
      # Establishing basic mod properties
      mod_id = drawer.basename(mod_path)
      mod_info = {'path': mod_path}
      # Getting track origin
      origin = get_origin(mod_id, mod_path, data.kunos_tracks, 'ui_track.json')
      # Getting optional information
      ## Getting filesize info
      if 'size' in include:
        mod_info['size'] = drawer.get_file_size(mod_path)
      ## Getting UI info
      if 'ui' in include:
        ui_info = get_ui_info(mod_path, origin, 'ui_track.json')
        # Getting country flag
        if 'flag' in include:
          if 'country' in ui_info:
            ui_info['flag'] = get_flag(AC_DIR, ui_info.get('country'))
        mod_info.update(ui_info)
      ## Getting outline
      if 'outline' in include:
        image_file = f"{mod_path}/ui/outline.png"
        mod_info['badge'] = get_existing(image_file)
      ## Getting preview
      if 'preview' in include:
        if origin == 'dlc': image_file = 'dlc_preview.png'
        else: image_file = 'preview.png'
        image_file = f"{mod_path}/ui/{image_file}"
        mod_info['preview'] = get_existing(image_file)
      ## Getting skins
      if 'skins' in include:
        mod_info['skins'] = get_skins(mod_path, include)
      # TODO: add layout info
      # Adding track to dict
      tracks[origin][mod_id] = mod_info
    # Returning fetched tracks
    return tracks


  # Returns apps
  # Available 'include' options:
  # ui, icon, size
  def get_apps(self, AC_DIR, include: list = []):
    apps = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = drawer.get_folders(f'{AC_DIR}/apps/python') + drawer.get_folders(f'{AC_DIR}/apps/lua')
    for mod_path in folders:
      # Establishing basic mod properties
      mod_id = drawer.basename(mod_path)
      lang = drawer.basename(drawer.get_parent(mod_path))
      mod_info = {'path': mod_path, 'lang': lang}
      # Getting app origin
      if (lang == 'python') and (mod_id in data.kunos_apps):
        origin = 'kunos'
      else:
        origin = 'mod'
      # Getting optional information
      ## Getting filesize info
      if 'size' in include:
        mod_info['size'] = drawer.get_file_size(mod_path)
      ## Getting UI info
      if 'ui' in include:
        ui_info = get_app_info(mod_path, lang)
        mod_info.update(ui_info)
      ## Getting icon
      if 'icon' in include:
        image_file = f"{mod_path}/icon.png"
        mod_info['icon'] = get_existing(image_file)
      # Adding track to dict
      apps[origin][mod_id] = mod_info
    # Returning fetched apps
    return apps


  # Returns ppfilters
  # Available 'include' options:
  # ui, size
  def get_ppfilters(self, AC_DIR, include: list = []):
    ppfilters = {'kunos': {}, 'dlc': {}, 'mod': {}}
    files = drawer.get_files(f'{AC_DIR}/system/cfg/ppfilters')
    for mod_path in files:
      # Establishing basic mod properties
      mod_id = drawer.basename(mod_path).removesuffix('.ini')
      mod_info = {'path': mod_path}
      # Getting ppfilter origin
      if mod_id in data.kunos_ppfilters:
        origin = 'kunos'
      else:
        origin = 'mod'
      # Getting optional information
      ## Getting filesize info
      if 'size' in include:
        mod_info['size'] = drawer.get_file_size(mod_path)
      ## Getting UI info
      if 'ui' in include:
        ui_info = get_ppfilter_info(mod_path)
        mod_info.update(ui_info)
      # Adding ppfilter to dict
      ppfilters[origin][mod_id] = mod_info
    # Returning fetched ppfilters
    return ppfilters


  # Returns weather
  # Available 'include' options:
  # ui, preview, size
  def get_weather(self, AC_DIR, include: list = []):
    weather = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = drawer.get_folders(f'{AC_DIR}/content/weather')
    for mod_path in folders:
      # Establishing basic mod properties
      mod_id = drawer.basename(mod_path)
      mod_info = {'path': mod_path}
      # Getting ppfilter origin
      if mod_id in data.kunos_weather:
        origin = 'kunos'
      else:
        origin = 'mod'
      # Getting optional information
      ## Getting filesize info
      if 'size' in include:
        mod_info['size'] = drawer.get_file_size(mod_path)
      ## Getting UI info
      if 'ui' in include:
        ui_info = get_weather_info(mod_path)
        mod_info.update(ui_info)
      ## Getting preview
      if 'preview' in include:
        image_file = f"{mod_path}/preview.png"
        mod_info['preview'] = get_existing(image_file)
      # Adding ppfilter to dict
      weather[origin][mod_id] = mod_info
    # Returning fetched weather
    return weather
