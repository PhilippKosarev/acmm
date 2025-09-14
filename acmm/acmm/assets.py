# Imports
from libjam import drawer, notebook
from enum import Enum
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Internal imports
from .data import data
from .base_asset import BaseAsset
from . import checker

# Shorthand vars
kunos_assets = data.get('kunos-assets')
asset_paths = data.get('asset-paths')

# Helper functions
def clean_ui_dict(data: dict) -> dict:
  for key in data:
    value = data.get(key)
    value_type = type(value)
    if value_type is dict:
      value = clean_ui_dict(value)
    elif value_type is str:
      value = value.replace('<br>', '\n')
      value = BeautifulSoup(value, 'html.parser').get_text()
    data[key] = value
  return data

# Enums
class AssetOrigin(Enum):
  MOD = 0
  KUNOS = 2
  DLC = 1

class AppLang(Enum):
  PYTHON = 0
  LUA = 1

# Base for all assets in the Asset and SubAsset container.
class GenericAsset(BaseAsset):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.data.update({
      'category': None,
    })

  def get_id(self) -> str:
    return drawer.get_basename(self.get_path())

  def get_size(self, human_readable: bool = False) -> int or tuple:
    size = drawer.get_filesize(self.get_path())
    if human_readable:
      return drawer.get_readable_filesize(size)
    return size

  def get_origin(self) -> AssetOrigin:
    category = self.data.get('category')
    if category is None:
      return
    if category not in kunos_assets:
      return
    if self.get_id() in kunos_assets.get(category):
      ui_file = self.data.get('dlc-ui-file')
      if ui_file is not None:
        if drawer.is_file(ui_file):
          return AssetOrigin.DLC
      return AssetOrigin.KUNOS
    return AssetOrigin.MOD

  def get_preview(self):
    if self.get_origin() is AssetOrigin.DLC:
      preview = self.data.get('dlc-preview-file')
      if not drawer.is_file(preview):
        preview = self.data.get('preview-file')
    else:
      preview = self.data.get('preview-file')
    if drawer.is_file(preview):
      return preview

  def get_ui_file(self) -> str:
    if self.get_origin() == AssetOrigin.DLC:
      ui_file = self.data.get('dlc-ui-file')
    else:
      ui_file = self.data.get('ui-file')
    if drawer.is_file(ui_file):
      return ui_file

  def get_ui_info(self) -> dict:
    ui_file = self.get_ui_file()
    if ui_file is None:
      return None
    data = notebook.read_json(ui_file)
    return clean_ui_dict(data)

  def trash(self):
    path = self.get_path()
    drawer.trash_path(path)
    self.data['path'] = None

  def delete(self):
    path = self.get_path()
    drawer.delete_path(path)
    self.data['path'] = None

class SubAsset:
  class CarSkin(GenericAsset):
    checks = [
      (checker.file_exists, 'preview.jpg'),
      (checker.file_exists, 'livery.png'),
      (checker.file_exists, 'ui_skin.json'),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      path = self.get_path()
      self.data.update({
        'ui-file': 'ui_skin.json',
        'preview-file': 'preview.jpg',
        'livery-file': 'livery.png',
      })

    def get_livery(self):
      file = self.get_path() + '/' + self.data.get('livery-file')
      if drawer.is_file(file):
        return file

  class TrackLayout(GenericAsset):
    checks = [
      (checker.file_exists, 'map.png'),
      (checker.dir_exists,  'data'),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.data.update({
        'map-file': 'map.png',
        'ui-file': 'ui_track.json',
        'preview-file': 'preview.png',
        'outline-file': 'outline.png',
      })

    def get_map(self):
      file = self.data.get('map-file')
      if drawer.is_file(file):
        return file

    def get_ui_dir(self):
      track_folder = drawer.get_parent(self.get_path())
      track_ui_folder = track_folder + '/' + 'ui'
      layout_ui_folder = track_ui_folder + '/' + self.get_id()
      if drawer.is_folder(layout_ui_folder):
        return layout_ui_folder

    def get_ui_file(self):
      ui_dir = self.get_ui_dir()
      if ui_dir is not None:
        file = ui_dir + '/' + self.data.get('ui-file')
        if drawer.is_file(file):
          file

    def get_outline(self):
      ui_dir = self.get_ui_dir()
      if ui_dir is not None:
        file = self.get_ui_dir() + '/' + self.data.get('outline-file')
        if drawer.is_file(file):
          return file


# A container for asset classes.
class Asset:

  @classmethod
  def get_asset_classes(cls):
    classes = []
    attributes = cls.__dict__.items()
    for key, value in attributes:
      if type(value) is type:
        classes.append(value)
    return classes

  class Car(GenericAsset):
    checks = [
      # Files
      (checker.file_exists, 'collider.kn5'),
      (checker.file_exists, 'driver_base_pos.knh'),
      (checker.dir_exists, 'sfx'),
      (checker.dir_exists, 'skins'),
      (checker.dir_exists, 'ui',),
      (checker.either_file_or_dir_exists, ('data.acd', 'data')),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      path = self.get_path()
      self.data.update({
        'category': 'cars',
        'ui-file': 'ui/ui_car.json',
        'dlc-ui-file': 'ui/dlc_ui_car.json',
        'preview-file': 'ui/preview.jpg',
        'badge-file': 'ui/badge.png',
        'logo-file': 'logo.png',
        'skins-dir': 'skins',
      })

    def get_badge(self) -> str:
      file = self.get_path() + '/' + self.data.get('badge-file')
      if drawer.is_file(file):
        return file

    def get_logo(self) -> str:
      file = self.get_path() + '/' + self.data.get('logo-file')
      if drawer.is_file(file):
        return file

    def get_skins(self):
      skins_dir = self.get_path() + '/' + self.data.get('skins-dir')
      skins = []
      if drawer.is_folder(skins_dir):
        skin_dirs = drawer.get_folders(skins_dir)
        for path in skin_dirs:
          skins.append(SubAsset.CarSkin(path))
      return skins

  class Track(GenericAsset):
    required_files = [
      ('ui', checker.dir_exists),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.data.update({
        'category': 'tracks',
        'ui-file': 'ui/ui_track.json',
        'dlc-ui-file': 'ui/dlc_ui_car.json',
        'preview-file': 'ui/preview.png',
        'outline-file': 'ui/outline.png',
        'map-file': 'map.png',
      })

    def get_outline(self):
      file = self.get_path() + '/' + self.data.get('outline-file')
      if drawer.is_file(file):
        return file

    def get_map(self):
      file = self.get_path() + '/' + self.data.get('map-file')
      if drawer.is_file(file):
        return file

    def get_layouts(self):
      non_layout_dirs = [
        'ai', 'data', 'skins', 'ui',
      ]
      folders = drawer.get_folders(self.get_path())
      folders = [
        folder for folder in folders
        if drawer.get_basename(folder) not in non_layout_dirs
      ]
      assets = []
      for folder in folders:
        try:
          assets.append(SubAsset.TrackLayout(folder))
        except InvalidAsset:
          continue
      return assets


  class PPFilter(GenericAsset):
    required_files = [
      ('.ini', checker.path_endswith),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.data.update({
        'category': 'ppfilters',
      })

    def get_id(self):
      basename = drawer.get_basename(self.get_path())
      return basename.removesuffix('.ini')


  class Weather(GenericAsset):
    required_files = [
      ('weather.ini', checker.file_exists),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.data.update({
        'category': 'weather',
        'ui-file': 'weather.ini',
        'preview-file': 'preview.jpg',
      })

    def get_ui_info(self):
      ui_file = self.get_path() + '/' + self.data.get('ui-file')
      data = notebook.read_ini(ui_file)
      launcher_info = data.get('LAUNCHER')
      cm_info = data.get('__LAUNCHER_CM')
      data = launcher_info
      if cm_info is not None:
        data.update(cm_info)
      return data


  class App(GenericAsset):
    required_files = [
      (('.lua', '.py'), checker.has_file_ending_with_either),
    ]

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.data.update({
        'category': 'apps',
        AppLang.PYTHON: {
          'ui-file': 'ui/ui_app.json',
        },
        AppLang.LUA: {
          'ui-file': 'manifest.ini',
          'icon-file': 'icon.png',
        },
      })

    def get_lang(self):
      files = drawer.get_files(self.get_path())
      for file in files:
        if file.endswith('.py'):
          return AppLang.PYTHON
        if file.endswith('.lua'):
          return AppLang.LUA

    def get_origin(self):
      if self.get_lang() is AppLang.PYTHON:
        if self.get_id() in kunos_assets.get(self.data.get('category')):
          return AssetOrigin.KUNOS
      return AssetOrigin.MOD

    def get_icon(self):
      origin = self.get_origin()
      if origin is AppLang.LUA:
        file = self.data.get(origin).get('icon-file')
        if drawer.is_file(file):
          return file

    def get_ui_file(self):
      origin = self.get_origin()
      file = self.data.get(origin).get('ui-file')
      if drawer.is_file(file):
        return file

    def get_ui_info(self):
      ui_file = self.get_ui_file()
      if ui_file is not None:
        if ui_file.endswith('.json'):
          data = clean_ui_dict(notebook.read_json(ui_file))
        elif ui_file.endswith('.ini'):
          data = notebook.read_ini(ui_file)
        return data
