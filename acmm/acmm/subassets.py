# Imports
from pathlib import Path

# Internal imports
from . import utils, validate_functions, generic_functions, factory

# Size getters
def get_track_layout_size(self) -> int:
  size = utils.get_dir_size(self.path)
  ui_dir = self.get_ui_dir()
  if ui_dir.is_dir():
    size += utils.get_dir_size(ui_dir)
  return size

# UI info getters
def get_car_skin_ui_info(self) -> dict:
  ui_file = self.path / 'ui_skin.json'
  if not ui_file.is_file():
    return
  return utils.read_json(ui_file)

def get_track_layout_ui_info(self) -> dict:
  ui_dir = self.get_ui_dir()
  ui_file = ui_dir / 'ui_track.json'
  if not ui_file.is_file():
    return
  return utils.read_json(ui_file)

# Preview file getters
def get_car_skin_preview_file(self) -> Path:
  return utils.return_if_file(self.path / 'preview.jpg')

def get_track_layout_preview_file(self) -> Path:
  ui_dir = self.get_ui_dir()
  return utils.return_if_file(ui_dir / 'preview.png')

# Car skin-specific functions
def get_car_skin_livery_file(self) -> Path:
  return utils.return_if_file(self.path / 'livery.png')

# Track layout-specific functions
def get_track_layout_map_file(self) -> Path:
  return utils.return_if_file(self.path / 'map.png')

def get_track_layout_ui_dir(self) -> Path:
  ui_dir = self.path.parent / 'ui' / self.path.name
  return ui_dir

def get_track_layout_outline_file(self) -> Path:
  ui_dir = self.get_ui_dir()
  return utils.return_if_file(ui_dir / 'outline.png')

# delete functions
def delete_track_layout(self):
  ui_dir = self.get_ui_dir()
  if ui_dir.is_dir():
    utils.unlink_dir(self.ui_dir)
  utils.unlink_dir(self.path)

# Mapping functions
car_skin_functions = {
  'get_id': generic_functions.get_id,
  'get_size': generic_functions.get_size,
  'get_ui_info': get_car_skin_ui_info,
  'get_preview_file': get_car_skin_preview_file,
  'delete': generic_functions.delete,
  'get_livery_file': get_car_skin_livery_file,
}
track_layout_functions = {
  'get_id': generic_functions.get_id,
  'get_size': get_track_layout_size,
  'get_ui_info': get_track_layout_ui_info,
  'get_preview_file': get_track_layout_preview_file,
  'delete': delete_track_layout,
  'get_map_file': get_track_layout_map_file,
  'get_ui_dir': get_track_layout_ui_dir,
  'get_outline_file': get_track_layout_outline_file,
}

# Constructing subassets
subasset_list = [
  (
    'CarSkin',
    None,
    validate_functions.is_car_skin,
    None,
    ['skins'],
    car_skin_functions,
  ),
  (
    'TrackLayout',
    None,
    validate_functions.is_track_layout,
    None,
    [],
    track_layout_functions,
  ),
]

class SubAsset:
  pass
factory.assign_assets(SubAsset, subasset_list)
SubAsset = SubAsset()
