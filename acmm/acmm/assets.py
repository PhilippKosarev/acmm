# Imports
from pathlib import Path
from libjam import notebook
from enum import Enum

# Internal imports
from .shared import *
from . import (
  data,
  utils,
  shared,
  fetch_functions,
  validate_functions,
  install_functions,
  generic_functions,
  factory,
)
from .subassets import SubAsset

# Shorthand vars
kunos_assets = data.get('kunos-assets')
ui_file_pathlists = {
  'cars': (
    ['ui', 'ui_car.json'],
    ['ui', 'dlc_ui_car.json'],
  ),
  'tracks': (
    ['ui', 'ui_track.json'],
    ['ui', 'dlc_ui_track.json'],
  ),
}
preview_file_pathlists = {
  'cars': (
    ['ui', 'preview.jpg'],
    ['ui', 'dlc_preview.jpg'],
  ),
  'tracks': (
    ['ui', 'preview.jpg'],
    ['ui', 'dlc_preview.jpg'],
  ),
}

# ID getters
def get_ppfilter_id(self) -> str:
  return self.path.name.removesuffix('.ini')

# Size getters
def get_ppfilter_size(self) -> int:
  return utils.get_file_size(self.path)

# Origin getters
def origin_getter(self, key: str) -> AssetOrigin:
  if self.get_id() in kunos_assets.get(key):
    pair = ui_file_pathlists.get(key)
    if pair:
      ui_file_pathlist, dlc_ui_file_pathlist = pair
      dlc_ui_file = self.path / Path(*dlc_ui_file_pathlist)
      if dlc_ui_file.is_file():
        return AssetOrigin.DLC
    return AssetOrigin.KUNOS
  return AssetOrigin.MOD

def get_car_origin(self) -> AssetOrigin:
  return origin_getter(self, 'cars')

def get_track_origin(self) -> AssetOrigin:
  id_in_kunos_assets = self.get_id() in kunos_assets.get('tracks')
  if id_in_kunos_assets:
    layouts = self.get_layouts()
    if layouts:
      layout = layouts[0]
      ui_dir = layout.get_ui_dir()
      dlc_ui_file_pathlist = ui_file_pathlists.get('tracks')[1]
      dlc_ui_file = ui_dir / Path(*dlc_ui_file_pathlist)
      if dlc_ui_file.is_file():
        return AssetOrigin.DLC
    return AssetOrigin.KUNOS
  return AssetOrigin.MOD

def get_weather_origin(self) -> AssetOrigin:
  return origin_getter(self, 'weather')

def get_app_origin(self) -> AssetOrigin:
    if self.get_lang() is AppLang.PYTHON:
      if self.get_id() in kunos_assets.get('apps'):
        return AssetOrigin.KUNOS
    return AssetOrigin.MOD

def get_ppfilter_origin(self) -> AssetOrigin:
  return origin_getter(self, 'ppfilters')

# UI info getters
def ui_file_getter(self, key: str) -> dict:
  ui_file_pathlist, dlc_ui_file_pathlist = ui_file_pathlists.get(key)
  origin = self.get_origin()
  if origin is AssetOrigin.DLC:
    ui_file = self.path / Path(*dlc_ui_file_pathlist)
    if ui_file.is_file():
      return ui_file
  ui_file = self.path / Path(*ui_file_pathlist)
  return ui_file

def ui_info_getter(self, key: str) -> dict or None:
  ui_file = ui_file_getter(self, key)
  if not ui_file.is_file():
    return
  return utils.read_json(ui_file)

def get_car_ui_info(self) -> dict:
  return ui_info_getter(self, 'cars')

def get_track_ui_info(self) -> dict:
  return ui_info_getter(self, 'tracks')

def get_weather_ui_info(self) -> dict:
  ui_file = self.path / 'weather.ini'
  data = notebook.read_ini(str(ui_file))
  launcher_info = data.get('LAUNCHER')
  cm_info = data.get('__LAUNCHER_CM')
  data = launcher_info
  if cm_info:
    data.update(cm_info)
  return data

def get_app_ui_info(self) -> dict:
  lang = self.get_lang()
  if lang is AppLang.PYTHON:
    ui_file = self.path / 'ui' / 'ui_app.json'
    if not ui_file.is_file():
      return {}
    data = utils.read_json(ui_file)
  elif lang is AppLang.LUA:
    ui_file = self.path / 'manifest.ini'
    if not ui_file.is_file():
      return {}
    data = notebook.read_ini(str(ui_file)).get('ABOUT')
  return data

def get_ppfilter_ui_info(self) -> dict:
  data = notebook.read_ini(str(self.path))
  about = data.get('ABOUT')
  if about:
    return about
  return {}

# Preview file getters
def get_car_preview_file(self) -> Path:
  return utils.return_if_file(self.path / 'ui' / 'preview.jpg')

def get_track_preview_file(self) -> Path:
  return utils.return_if_file(self.path / 'ui' / 'preview.png')

def get_weather_preview_file(self) -> Path:
   return utils.return_if_file(self.path / 'preview.jpg')

# delete functions
def delete_ppfilter(self):
  self.path.unlink()

# Car-specific functions
def get_car_badge_file(self) -> Path:
  return utils.return_if_file(self.path / 'ui' / 'badge.png')

def get_logo_file(self) -> Path:
  return utils.return_if_file(self.path / 'logo.png')

def get_car_skins(self) -> list:
  skins_dir = self.path / 'skins'
  skins = []
  if not skins_dir.is_dir():
    return skins
  for skin_dir in skins_dir.iterdir():
    try:
      skin = SubAsset.CarSkin(skin_dir)
      skins.append(skin)
    except InvalidAsset:
      continue
  return skins

# Track-specific functions
def get_track_outline_file(self) -> Path:
  return utils.return_if_file(self.path / 'ui' / 'outline.png')

def get_track_map_file(self) -> Path:
   return utils.return_if_file(self.path / 'map.png')

def get_track_layouts(self) -> list:
  non_layout_dirs = ['ai', 'data', 'skins', 'ui']
  layouts = []
  for subpath in self.path.iterdir():
    if subpath.name in non_layout_dirs:
      continue
    try:
      layout = SubAsset.TrackLayout(subpath)
      layouts.append(layout)
    except InvalidAsset:
      continue
  return layouts

# App-specific functions
def get_app_lang(self) -> AppLang:
  py_file = self.path / (self.path.name + '.py')
  lua_file = self.path / (self.path.name + '.lua')
  if py_file.is_file():
    return AppLang.PYTHON
  if lua_file.is_file():
    return AppLang.LUA
  raise InvalidAsset('App is missing a script file')

def get_app_icon_file(self) -> Path:
  lang = self.get_lang()
  if lang is not AppLang.LUA:
    return
  return utils.return_if_file(self.path / 'icon.png')

# Mapping functions
car_functions = {
  'get_id': generic_functions.get_id,
  'get_size': generic_functions.get_size,
  'get_origin': get_car_origin,
  'get_ui_info': get_car_ui_info,
  'get_preview_file': get_car_preview_file,
  'delete': generic_functions.delete,
  'get_skins': get_car_skins,
}
track_functions = {
  'get_id': generic_functions.get_id,
  'get_size': generic_functions.get_size,
  'get_origin': get_track_origin,
  'get_ui_info': get_track_ui_info,
  'get_preview_file': get_track_preview_file,
  'delete': generic_functions.delete,
  'get_layouts': get_track_layouts,
}
weather_functions = {
  'get_id': generic_functions.get_id,
  'get_size': generic_functions.get_size,
  'get_origin': get_weather_origin,
  'get_ui_info': get_weather_ui_info,
  'get_preview_file': get_weather_preview_file,
  'delete': generic_functions.delete,
}
app_functions = {
  'get_id': generic_functions.get_id,
  'get_size': generic_functions.get_size,
  'get_origin': get_app_origin,
  'get_ui_info': get_app_ui_info,
  'delete': generic_functions.delete,
  'get_lang': get_app_lang,
  'get_icon_file': get_app_icon_file,
}
ppfilter_functions = {
  'get_id': get_ppfilter_id,
  'get_size': get_ppfilter_size,
  'get_origin': get_ppfilter_origin,
  'get_ui_info': get_ppfilter_ui_info,
  'delete': delete_ppfilter,
}

# Constructing assets
asset_list = [
  (
    'Car',
    fetch_functions.get_dirs,
    validate_functions.is_car,
    install_functions.install_generic,
    ['content', 'cars'],
    car_functions,
  ),
  (
    'Track',
    fetch_functions.get_dirs,
    validate_functions.is_track,
    install_functions.install_generic,
    ['content', 'tracks'],
    track_functions,
  ),
  (
    'Weather',
    fetch_functions.get_dirs,
    validate_functions.is_weather,
    install_functions.install_generic,
    ['content', 'weather'],
    weather_functions,
  ),
  (
    'App',
    fetch_functions.get_app_dirs,
    validate_functions.is_app,
    install_functions.install_app,
    ['apps'],
    app_functions,
  ),
  (
    'PPFilter',
    fetch_functions.get_files,
    validate_functions.is_ppfilter,
    install_functions.install_generic,
    ['system', 'cfg', 'ppfilters'],
    ppfilter_functions,
  ),
]

# Creating assets
class Asset:
  pass
factory.assign_assets(Asset, asset_list)
Asset = Asset()
