# Imports
from pathlib import Path
import os

# Internal imports
from . import data

# Returns True if all given items exist in root, case insensitive.
def validate(root: Path, items: list[str or tuple[str, list]]) -> bool:
  if not root.is_dir():
    return False
  entries = {entry.name.lower(): entry for entry in os.scandir(root)}
  for item in items:
    if type(item) is str:
      entry = entries.get(item.lower())
      if not entry:
        return False
      if not entry.is_file():
        return False
    else:
      item, subitems = item
      entry = entries.get(item.lower())
      if not entry:
        return False
      if not entry.is_dir():
        return False
      if not validate(entry, subitems):
        return False
  return True

# Returns True if given path is a path to a car skin.
def is_car_skin(path: Path) -> bool:
  return validate(path, [
    'preview.jpg',
    'livery.png',
  ])

# Returns True if given path is a path to a car.
def is_car(path: Path) -> bool:
  # Making sure that either data dir or file exists
  data_file = path / 'data.acd'
  data_dir = path / 'data'
  if not (data_file.is_file() or data_dir.is_dir()):
    return False
  return validate(path, [
    ('ui', []),
    ('sfx', []),
    'collider.kn5',
    'driver_base_pos.knh',
    'tyre_0_shadow.png',
    'tyre_1_shadow.png',
    'tyre_2_shadow.png',
    'tyre_3_shadow.png',
  ])

# Returns True if given path is a path to a track layout.
def is_track_layout(path: Path) -> bool:
  return validate(path.parent, [
    (path.name, [
      'map.png',
      ('data', []),
    ]),
    ('ui', [
      (path.name, [
        'ui_track.json',
        'preview.png',
        'outline.png',
      ]),
    ]),
  ])

# Returns True if given path is a path to a track.
def is_track(path: Path) -> bool:
  return validate(path, [
    ('ui', []),
    path.name + '.kn5',
  ])

# Returns True if given path is a path to a ppfilter.
def is_ppfilter(path: Path) -> bool:
  if not path.is_file():
    return False
  if not path.name.endswith('.ini'):
    return False
  text = path.read_text(errors='ignore')
  required_texts = ['[ABOUT]', 'YEBIS']
  for required_text in required_texts:
    if required_text not in text:
      return False
  return True

# Returns True if given path is a path to weather.
def is_weather(path: Path) -> bool:
  return validate(path, [
    'weather.ini',
  ])

# Returns True if given path is a path to a Python app.
def is_python_app(path: Path) -> bool:
  return validate(path, [
    path.name + '.py',
  ])

# Returns True if given path is a path to a Lua app.
def is_lua_app(path: Path) -> bool:
  return validate(path, [
    path.name + '.lua',
    'manifest.ini',
    'icon.png',
  ])

# Returns True if given path is a path to an app.
def is_app(path: Path) -> bool:
  return is_python_app(path) or is_lua_app(path)

# Returns True if given path is a path to CSP.
def is_csp(path: Path) -> bool:
  if not path.is_dir():
    return False
  common_files = data.get('csp-common-files')
  return validate(path, common_files)

# Returns True if given path is a path to Pure.
def is_pure(path: Path) -> bool:
  if not path.is_dir():
    return False
  common_files = data.get('pure-common-files')
  return validate(path, common_files)
