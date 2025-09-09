# Imports
from libjam import drawer, notebook, typewriter
from enum import Enum
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings, pycountry, re

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Internal imports
from .data import data
from .shared import *

# Shorthand vars
kunos_assets = data.get('kunos-assets')
asset_paths = data.get('asset-paths')

# Enums
class AssetOrigin(Enum):
  MOD = 0
  KUNOS = 2
  DLC = 1

class AppLang(Enum):
  PYTHON = 0
  LUA = 1

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


class BaseAsset:
  def __init__(self, path: str):
    if not drawer.exists(path):
      raise FileNotFoundError(f"Path '{path}' does not lead to a file or directory.")
    self.path = path
    self.paths = {}

  def get_path(self) -> str:
    return self.path

  def get_id(self) -> str:
    return drawer.get_basename(self.path)

  def get_size(self, human_readable: bool = False) -> int or tuple:
    size = drawer.get_filesize(self.path)
    if human_readable:
      return drawer.get_readable_filesize(size)
    return size

  def get_ui_file(self) -> str:
    ui_file = self.paths.get('ui-file')
    if drawer.is_file(ui_file):
      return ui_file

  def get_ui_info(self) -> dict:
    ui_file = self.get_ui_file()
    if ui_file is None:
      return None
    data = notebook.read_json(ui_file)
    return clean_ui_dict(data)

  def get_flag(self, AC_DIR: str, ui_info: dict) -> str:
    country = ui_info.get('country')
    if country is None:
      return None
    country = country.replace('.', '').strip()
    country = pycountry.countries.get(name=country)
    if country is None:
      return None
    iso_3166 = country.alpha_3
    flag = f'{AC_DIR}/content/gui/NationFlags/{iso_3166}.png'
    if drawer.is_file(flag):
      return flag

  def get_preview(self):
    preview = self.paths.get('preview-file')
    if drawer.is_file(preview):
      return preview

class GenericAsset(BaseAsset):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.category = None

  def get_origin(self) -> AssetOrigin:
    kunos_category_assets = kunos_assets.get(self.category)
    if kunos_category_assets is not None:
      if self.get_id() in kunos_category_assets:
        ui_file = self.paths.get('dlc-ui-file')
        if ui_file is not None:
          if drawer.is_file(ui_file):
            return AssetOrigin.DLC
        return AssetOrigin.KUNOS
    return AssetOrigin.MOD

  def get_preview(self):
    if self.get_origin() is AssetOrigin.DLC:
      preview = self.paths.get('dlc-preview-file')
      if not drawer.is_file(preview):
        preview = self.paths.get('preview-file')
    else:
      preview = self.paths.get('preview-file')
    if drawer.is_file(preview):
      return preview

  def get_ui_file(self) -> str:
    if self.get_origin() == AssetOrigin.DLC:
      ui_file = self.paths.get('dlc-ui-file')
    else:
      ui_file = self.paths.get('ui-file')
    if drawer.is_file(ui_file):
      return ui_file

  def get_ui_info(self) -> dict:
    ui_file = self.get_ui_file()
    if ui_file is None:
      return None
    data = notebook.read_json(ui_file)
    return clean_ui_dict(data)

# A container for asset classes.
class Asset:

  class Car(GenericAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.category = 'cars'
      self.paths = {
        'ui-file': f'{self.path}/ui/ui_car.json',
        'dlc-ui-file': f'{self.path}/ui/dlc_ui_car.json',
        'preview-file': f'{self.path}/ui/preview.jpg',
        'install-dir': asset_paths.get(self.category),
      }

    def get_badge(self) -> str:
      file = f"{self.path}/ui/badge.png"
      if drawer.is_file(file):
        return file

    def get_logo(self) -> str:
      file = f"{self.path}/logo.png"
      if drawer.is_file(file):
        return file

    def get_skins(self):
      skins_dir = f"{self.path}/skins"
      if drawer.is_folder(skins_dir):
        skins = []
        skin_dirs = drawer.get_folders(skins_dir)
        for path in skin_dirs:
          skins.append(Asset.CarSkin(path))
        return skins


  class CarSkin(BaseAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.paths = {
        'ui-file': f'{self.path}/ui_skin.json',
        'preview-file': f'{self.path}/preview.jpg',
        'livery-file': f'{self.path}/livery.png',
      }

    def get_livery(self):
      file = self.paths.get('livery-file')
      if drawer.is_file(file):
        return file


  class Track(GenericAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.category = 'tracks'
      self.paths = {
        'ui-file': f'{self.path}/ui/ui_track.json',
        'dlc-ui-file': f'{self.path}/ui/dlc_ui_car.json',
        'preview-file': f'{self.path}/ui/preview.png',
        'outline-file': f'{self.path}/ui/outline.png',
        'map-file': f'{self.path}/map.png',
        'install-dir': asset_paths.get('tracks'),
      }

    def get_outline(self):
      file = self.paths.get('outline-file')
      if drawer.is_file(file):
        return file

    def get_map(self):
      file = self.paths.get('map-file')
      if drawer.is_file(file):
        return file

    def get_layouts(self):
      layouts_dir = f"{self.path}/ui"
      if drawer.is_folder(skins_dir):
        layouts = []
        layout_dirs = drawer.get_folders(skins_dir)
        for path in layout_dirs:
          layouts.append(Asset.TrackLayout(path))
        return layouts


  class TrackLayout(BaseAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.paths = {
        'ui-file': f'{self.path}/ui_track.json',
        'preview-file': f'{self.path}/preview.png',
        'outline-file': f'{self.path}/outline.png',
      }

    def get_outline(self):
      file = self.paths.get('outline-file')
      if drawer.is_file(file):
        return file


  class PPFilter(GenericAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.category = 'ppfilters'

    def get_id(self):
      basename = drawer.get_basename(self.path)
      return basename.removesuffix('.ini')


  class Weather(GenericAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.category = 'weather'
      self.paths = {
        'ui-file': f'{self.path}/weather.ini',
        'preview-file': f'{self.path}/preview.jpg',
      }

    def get_ui_info(self):
      ui_file = f'{self.path}/weather.ini'
      data = notebook.read_ini(ui_file)
      launcher_info = data.get('LAUNCHER')
      cm_info = data.get('__LAUNCHER_CM')
      data = launcher_info
      if cm_info is not None:
        data.update(cm_info)
      return data

    def get_preview(self):
      file = self.paths.get('preview-file')
      if drawer.is_file(file):
        return file


  class App(GenericAsset):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.category = 'apps'
      self.paths = {
        'python': {
          'ui-file': f'{self.path}/ui/ui_app.json',
        },
        'lua': {
          'ui-file': f'{self.path}/manifest.ini',
          'icon-file': f'{self.path}/icon.png',
        },
      }

    def get_lang(self):
      files = drawer.get_files(self.path)
      for file in files:
        if file.endswith('.py'):
          return AppLang.PYTHON
        if file.endswith('.lua'):
          return AppLang.LUA

    def get_origin(self):
      if self.get_lang() is AppLang.PYTHON:
        basename = drawer.get_basename(self.path)
        if basename in kunos_assets.get(self.category):
          return AssetOrigin.KUNOS
      return AssetOrigin.MOD

    def get_icon(self):
      if self.get_origin() is AppLang.LUA:
        file = self.paths.get('lua').get('icon-file')
        if drawer.is_file(file):
          return file

    def get_ui_file(self):
      match self.get_origin():
        case AppLang.PYTHON:
          file = self.paths.get('python').get('ui-file')
        case AppLang.LUA:
          file = self.paths.get('python').get('ui-file')
      if drawer.is_file(file):
        return file

    def get_ui_info(self):
      ui_file = self.get_ui_file()
      if ui_file is None:
        return None
      data = None
      if ui_file.endswith('.json'):
        data = clean_ui_dict(notebook.read_json(ui_file))
      elif ui_file.endswith('.ini'):
        data = clean_ui_dict(notebook.read_ini(ui_file))
      else:
        raise NotImplementedError()
      return data

  class CSP:
    def __init__(self, path: str):
      if not drawer.is_folder(f'{path}/extension'):
        raise FileNotFoundError(f"Path '{path}' does not lead to a CSP directory.")
      self.path = path

    def get_path(self) -> str:
      return self.path

    def get_size(self, human_readable: bool = False) -> int or tuple:
      size = drawer.get_filesize(f'{self.path}/extension')
      if human_readable:
        return drawer.get_readable_filesize(size)
      return size

    def get_ui_info(self):
      # Shit naming
      l = [
        (
          'data_manifest.ini',
          {
            # 'ℹ' is different from 'i' here
            'ℹ': {'preview': 'preview', 'description': 'description', 'url': 'url'},
            'VERSION': {'shaders_patch': 'version', 'shaders_patch_build': 'build'},
          }
        )
      ]
      # God will not be happy about sins committed here
      info = {}
      for ini_file, desired_info in l:
        ini_file = f'{self.path}/extension/config/{ini_file}'
        if not drawer.is_file(ini_file):
          continue
        ini_data = notebook.read_ini(ini_file)
        for desired_section in desired_info:
          if desired_section not in ini_data:
            continue
          ini_items = ini_data.get(desired_section)
          desired_items = desired_info.get(desired_section)
          for desired_item in desired_items:
            if desired_item not in ini_items:
              continue
            key = desired_items.get(desired_item)
            value = ini_items.get(desired_item)
            info[key] = value
      # Adding credits
      credits_file = f'{self.path}/extension/config/data_credits.txt'
      if drawer.is_file(credits_file):
        info['credits-file'] = credits_file
        text = drawer.read_file(credits_file)
        # Say thank you to ChatGPT for the regex
        info['credits'] = re.sub(r'\[/?[a-zA-Z0-9_]+(?:=[^\]]+)?\]', '', text)
      # Returning
      return info

    def get_id(self) -> str:
      info = self.get_ui_info()
      if info is None:
        return 'csp'
      version = info.get('version')
      return f'csp_v{version}'
