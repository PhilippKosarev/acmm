# Imports
from libjam import drawer, notebook
import pycountry
# Internal imports
from data import data

# Shorthand vars
kunos_assets = data.get('kunos-assets')

# Helper functions
# If path exists, returns path, otherwise returns None.
def get_existing(path: str):
  if drawer.exists(path):
    return path
  else:
    return None

# Given a country name, returns the country flag file.
def get_flag(AC_DIR: str, country: str) -> str:
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

# Gets the origin of a mod.
def get_origin(
  mod_id: str, mod_path: str, kunos_assets: list, json_filename: str
) -> str:
  if mod_id in kunos_assets:
    mod_files = drawer.get_basenames(drawer.get_files(mod_path))
    if f'dlc_{json_filename}' in mod_files:
      origin = 'dlc'
    else:
      origin = 'kunos'
  else:
    origin = 'mod'
  return origin

# Gets the UI info of cars and tracks.
def get_ui_info(mod_path: str, origin: str, json_filename: str) -> dict:
  if origin == 'dlc':
    json_filename = f'dlc_{json_filename}'
  json_file = f"{mod_path}/ui/{json_filename}"
  if drawer.is_file(json_file):
    return notebook.read_json(json_file)
  else:
    return {}

# Gets the UI info of apps.
def get_app_ui_info(mod_path: str, lang: str) -> dict:
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

# Gets the UI info of PP filters.
def get_ppfilter_ui_info(mod_path: str) -> dict:
  ui_info = notebook.read_ini(mod_path)
  if 'ABOUT' in ui_info:
    return ui_info.get('ABOUT')
  else:
    return {}

# Gets the UI info of weather.
def get_weather_ui_info(mod_path: str) -> dict:
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

# Gets skins of cars and tracks.
def get_skins(mod_path: str, include: list) -> dict:
  folder = f"{mod_path}/skins"
  if not drawer.is_folder(folder):
    return None
  skin_dirs = drawer.get_folders(folder)
  skin_dirs.sort()
  skins = {}
  for skin_path in skin_dirs:
    # Adding basic skin information
    skin_id = drawer.get_basename(skin_path)
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

# Gathers info about the mods.
class InfoGatherer:

  # Available include options:
  # ['size', 'ui', 'flag', 'preview', 'skins', 'badge', 'logo']
  # Note: option 'flag' depends on, and is stored in 'ui'
  def get_car_info(self, mod_path: str, include: list = []) -> dict:
    # Establishing basic mod properties
    mod_id = drawer.get_basename(mod_path)
    mod_info = {'mod_id': mod_id, 'path': mod_path}
    # Getting car origin
    origin = get_origin(mod_id, mod_path, kunos_assets.get('cars'), 'ui_car.json')
    # Getting optional information
    ## Getting filesize info
    if 'size' in include:
      mod_info['size'] = drawer.get_filesize(mod_path)
    ## Getting UI info
    if 'ui' in include:
      ui_info = get_ui_info(mod_path, origin, 'ui_car.json')
      mod_info['ui'] = ui_info
      # Getting country flag
      if 'flag' in include:
        if 'country' in ui_info:
          mod_info['flag'] = get_flag(AC_DIR, ui_info.get('country'))
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
    # Returning
    return mod_info, origin

  # Available include options:
  # ['size', 'ui', 'flag', 'preview', 'skins', 'outline']
  # Note: option 'flag' depends on, and is stored in 'ui'
  def get_track_info(self, mod_path: str, include: list = []) -> dict:
    #TODO: add layouts info
    # Establishing basic mod properties
    mod_id = drawer.get_basename(mod_path)
    mod_info = {'mod_id': mod_id, 'path': mod_path}
    # Getting track origin
    origin = get_origin(mod_id, mod_path, kunos_assets.get('tracks'), 'ui_track.json')
    # Getting optional information
    ## Getting filesize info
    if 'size' in include:
      mod_info['size'] = drawer.get_filesize(mod_path)
    ## Getting UI info
    if 'ui' in include:
      ui_info = get_ui_info(mod_path, origin, 'ui_track.json')
      mod_info['ui'] = ui_info
      # Getting country flag
      if 'flag' in include:
        if 'country' in ui_info:
          mod_info['flag'] = get_flag(AC_DIR, ui_info.get('country'))
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
    # Returning
    return mod_info, origin

  # Available include options:
  # ['size', 'ui', 'icon']
  def get_app_info(self, mod_path: str, include: list = []) -> dict:
    # Establishing basic mod properties
    mod_id = drawer.get_basename(mod_path)
    lang = drawer.get_basename(drawer.get_parent(mod_path))
    mod_info = {'mod_id': mod_id, 'path': mod_path, 'lang': lang}
    # Getting app origin
    if (lang == 'python') and (mod_id in kunos_assets.get('apps')):
      origin = 'kunos'
    else:
      origin = 'mod'
    # Getting optional information
    ## Getting filesize info
    if 'size' in include:
      mod_info['size'] = drawer.get_filesize(mod_path)
    ## Getting UI info
    if 'ui' in include: mod_info['ui'] = get_app_ui_info(mod_path, lang)
    ## Getting icon
    if 'icon' in include:
      image_file = f"{mod_path}/icon.png"
      mod_info['icon'] = get_existing(image_file)
    # Returning
    return mod_info, origin

  # Available include options:
  # ['size', 'ui']
  def get_ppfilter_info(self, mod_path: str, include: list = []) -> dict:
    # Establishing basic mod properties
    mod_id = drawer.get_basename(mod_path).removesuffix('.ini')
    mod_info = {'mod_id': mod_id, 'path': mod_path}
    # Getting ppfilter origin
    if mod_id in kunos_assets.get('ppfilters'):
      origin = 'kunos'
    else:
      origin = 'mod'
    # Getting optional information
    ## Getting filesize info
    if 'size' in include: mod_info['size'] = drawer.get_filesize(mod_path)
    ## Getting UI info
    if 'ui' in include: mod_info['ui'] = get_ppfilter_ui_info(mod_path)
    # Returning
    return mod_info, origin

  # Available include options:
  # ['size', 'ui', 'preview']
  def get_weather_info(self, mod_path: str, include: list = []) -> dict:
    # Establishing basic mod properties
    mod_id = drawer.get_basename(mod_path)
    mod_info = {'mod_id': mod_id, 'path': mod_path}
    # Getting weather origin
    if mod_id in kunos_assets.get('weather'):
      origin = 'kunos'
    else:
      origin = 'mod'
    # Getting optional information
    ## Getting filesize info
    if 'size' in include:
      mod_info['size'] = drawer.get_filesize(mod_path)
    ## Getting UI info
    if 'ui' in include:
      mod_info['ui'] = get_weather_ui_info(mod_path)
    ## Getting preview
    if 'preview' in include:
      image_file = f"{mod_path}/preview.png"
      mod_info['preview'] = get_existing(image_file)
    # Returning
    return mod_info, origin
