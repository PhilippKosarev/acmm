# Imports
from libjam import notebook
from pathlib import Path
from enum import Enum
import html
import re

# Internal imports
from . import data, validate_functions, shared
from .base_asset import BaseAsset, InvalidAsset

# Shorthand vars
kunos_assets = data.get('kunos-assets')
re_html_br_tag = re.compile('<.*?br.*?>')

# Helper functions
def get_existing(prefix: Path, basename: str):
  if not prefix or not basename:
    return None
  path = prefix / basename
  if path.exists():
    return path

def get_existing_iter(prefix: Path, pathlist: iter) -> Path or None:
  if not prefix or not pathlist:
    return
  path = prefix / Path(*pathlist)
  if path.exists():
    return path

def unescape_json_dict(data: dict) -> dict:
  for key, value in data.items():
    value_type = type(value)
    if value_type is dict:
      value = unescape_json_dict(value)
    elif value_type is str:
      value = html.unescape(value)
      value = re.sub(re_html_br_tag, '\n', value)
    else:
      continue
    data[key] = value
  return data

# Enums
class AssetOrigin(Enum):
  MOD = 0
  KUNOS = 1
  DLC = 2

class AppLang(Enum):
  PYTHON = 0
  LUA = 1


# Base for all assets in the Asset and SubAsset container.
class GenericAsset(BaseAsset):
  def __init__(self, path):
    super().__init__(path)

  def get_id(self) -> str:
    path = self.get_path()
    return path.name

  def get_size(self) -> int:
    path = self.get_path()
    return shared.get_size(path)

  def get_origin(self) -> AssetOrigin:
    category = self.data.get('category')
    if self.get_id() in kunos_assets.get(category):
      ui_file = self.data.get('dlc-ui-file')
      if ui_file:
        ui_file = self.get_path() / Path(*ui_file)
        if ui_file.is_file():
          return AssetOrigin.DLC
      return AssetOrigin.KUNOS
    return AssetOrigin.MOD

  def get_preview_file(self) -> Path:
    preview_file = None
    origin = self.get_origin()
    if origin is AssetOrigin.DLC:
      preview_file = self.data.get('dlc-preview-file')
    if preview_file is None:
      preview_file = self.data.get('preview-file')
    return get_existing_iter(self.get_path(), preview_file)

  def get_ui_file(self) -> Path:
    ui_file = None
    if self.get_origin() == AssetOrigin.DLC:
      ui_file = self.data.get('dlc-ui-file')
    if not ui_file:
      ui_file = self.data.get('ui-file')
    return get_existing_iter(self.get_path(), ui_file)

  def get_ui_info(self) -> dict:
    ui_file = self.get_ui_file()
    if not ui_file:
      return
    data = notebook.read_json(str(ui_file))
    data = unescape_json_dict(data)
    return data

  def delete(self):
    path = self.get_path()
    shared.unlink_tree(path)


class SubAsset:
  class CarSkin(GenericAsset):
    validate = staticmethod(validate_functions.is_car_skin)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'ui-file':      ['ui_skin.json'],
        'preview-file': ['preview.jpg'],
        'livery-file':  ['livery.png'],
      })

    def get_livery_file(self) -> Path:
      livery_file = self.data.get('livery-file')
      return get_existing_iter(self.get_path(), livery_file)

  class TrackLayout(GenericAsset):
    validate = staticmethod(validate_functions.is_track_layout)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'map-file':         ['map.png'],
        'dlc-ui-file':      ['dlc_ui_track.json'],
        'ui-file':          ['ui_track.json'],
        'dlc-preview-file': ['dlc_preview.png'],
        'preview-file':     ['preview.png'],
        'outline-file':     ['outline.png'],
      })

    def get_map_file(self) -> Path:
      map_file = self.data.get('map-file')
      return get_existing_iter(self.get_path(), map_file)

    def get_ui_dir(self) -> Path:
      path = self.get_path()
      ui_dir = path.parent / 'ui' / path.name
      if ui_dir.is_dir():
        return ui_dir

    def get_ui_file(self) -> Path:
      ui_file = None
      origin = self.get_origin()
      if origin is AssetOrigin.DLC:
        ui_file = self.data.get('dlc-ui-file')
      if not ui_file:
        ui_file = self.data.get('ui-file')
      ui_dir = self.get_ui_dir()
      return get_existing(ui_dir, ui_file)

    def get_preview_file(self) -> Path:
      preview_file = None
      origin = self.get_origin()
      if origin is AssetOrigin.DLC:
        preview_file = self.data.get('dlc-preview-file')
      if not preview_file:
        preview_file = self.data.get('preview-file')
      ui_dir = self.get_ui_dir()
      return get_existing_iter(ui_dir, preview_file)

    def get_outline_file(self) -> Path:
      ui_dir = self.get_ui_dir()
      outline_file = self.data.get('outline-file')
      return get_existing_iter(ui_dir, outline_file)


# A container for asset classes.
class Asset:
  @classmethod
  def get_classes(cls):
    classes = []
    attributes = cls.__dict__.items()
    for key, value in attributes:
      if type(value) is type:
        classes.append(value)
    return classes


  class Car(GenericAsset):
    validate = staticmethod(validate_functions.is_car)
    def __init__(self, path):
      super().__init__(path)
      path = self.get_path()
      self.data.update({
        'category':         'cars',
        'dlc-ui-file':      ['ui', 'dlc_ui_car.json'],
        'ui-file':          ['ui', 'ui_car.json'],
        'dlc-preview-file': ['ui', 'dlc_ui_car.json'],
        'preview-file':     ['ui', 'preview.jpg'],
        'badge-file':       ['ui', 'badge.png'],
        'logo-file':        ['logo.png'],
        'skins-dir':        'skins',
      })

    def get_badge_file(self) -> Path:
      badge_file = self.data.get('badge-file')
      return get_existing_iter(self.get_path(), badge_file)

    def get_logo_file(self) -> Path:
      logo_file = self.data.get('logo-file')
      return get_existing_iter(self.get_path(), logo_file)

    def get_skins(self) -> list[SubAsset.CarSkin]:
      skins_dir = self.get_path() / self.data.get('skins-dir')
      if not skins_dir.is_dir():
        return
      skins = []
      for skin_dir in skins_dir.iterdir():
        try:
          skin = SubAsset.CarSkin(skin_dir)
          skins.append(skin)
        except InvalidAsset:
          continue
      return skins


  class Track(GenericAsset):
    validate = staticmethod(validate_functions.is_track)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'category':         'tracks',
        'dlc-ui-file':      ['ui', 'dlc_ui_car.json'],
        'ui-file':          ['ui', 'ui_track.json'],
        'dlc-preview-file': ['ui', 'preview.png'],
        'preview-file':     ['ui', 'preview.png'],
        'outline-file':     ['ui', 'outline.png'],
        'map-file':         ['map.png'],
      })

    def get_outline_file(self) -> Path:
      outline_file = self.data.get('outline-file')
      return get_existing_iter(self.get_path(), outline_file)

    def get_map_file(self) -> Path:
      map_file = self.data.get('map-file')
      return get_existing_iter(self.get_path(), map_file)

    def get_layouts(self) -> list[SubAsset.TrackLayout]:
      path = self.get_path()
      non_layout_dirs = ['ai', 'data', 'skins', 'ui']
      layouts = []
      for subpath in path.iterdir():
        if not subpath.is_dir():
          continue
        if subpath.name in non_layout_dirs:
          continue
        try:
          layout = SubAsset.TrackLayout(subpath)
          layouts.append(layout)
        except InvalidAsset:
          continue
      return layouts


  class PPFilter(GenericAsset):
    validate = staticmethod(validate_functions.is_ppfilter)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'category': 'ppfilters',
        'ui-file': [],
      })

    def get_ui_info(self) -> dict:
      ui_file = self.get_ui_file()
      data = notebook.read_ini(str(ui_file))
      about = data.get('ABOUT')
      if about:
        return dict(about)

    def get_id(self) -> str:
      path = self.get_path()
      return path.name.removesuffix('.ini')

    def delete(self):
      path = self.get_path()
      path.unlink()


  class Weather(GenericAsset):
    validate = staticmethod(validate_functions.is_weather)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'category':     'weather',
        'ui-file':      ['weather.ini'],
        'preview-file': ['preview.jpg'],
      })

    def get_ui_info(self) -> dict:
      ui_file = self.get_ui_file()
      if not ui_file:
        return
      data = notebook.read_ini(str(ui_file))
      launcher_info = data.get('LAUNCHER')
      cm_info = data.get('__LAUNCHER_CM')
      data = launcher_info
      if cm_info:
        data.update(cm_info)
      return data


  class App(GenericAsset):
    validate = staticmethod(validate_functions.is_app)
    def __init__(self, path):
      super().__init__(path)
      self.data.update({
        'category': 'apps',
        AppLang.PYTHON: {
          'ui-file': ['ui', 'ui_app.json'],
        },
        AppLang.LUA: {
          'ui-file':   ['manifest.ini'],
          'icon-file': ['icon.png'],
        },
      })

    def get_lang(self) -> AppLang:
      path = self.get_path()
      py_file = path / (path.name + '.py')
      lua_file = path / (path.name + '.lua')
      if py_file.is_file():
        return AppLang.PYTHON
      if lua_file.is_file():
        return AppLang.LUA
      raise InvalidAsset('Missing script file')

    def get_origin(self) -> AssetOrigin:
      if self.get_lang() is AppLang.PYTHON:
        kunos_apps = kunos_assets.get(self.data.get('category'))
        if self.get_id() in kunos_apps:
          return AssetOrigin.KUNOS
      return AssetOrigin.MOD

    def get_icon(self) -> Path:
      lang = self.get_lang()
      icon_file = self.data.get(lang).get('icon-file')
      return get_existing_iter(self.get_path(), icon_file)

    def get_ui_file(self) -> Path:
      lang = self.get_lang()
      ui_file = self.data.get(lang).get('ui-file')
      return get_existing_iter(self.get_path(), ui_file)

    def get_ui_info(self) -> dict:
      ui_file = self.get_ui_file()
      lang = self.get_lang()
      if lang is AppLang.PYTHON:
        data = notebook.read_json(str(ui_file))
        data = unescape_json_dict(data)
      elif lang is AppLang.LUA:
        data = notebook.read_ini(ui_file).get('ABOUT')
      return data
