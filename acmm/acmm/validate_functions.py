# Imports
from pathlib import Path

# Internal imports
from . import data

# Internal functions
def find_case_insensitive(path: Path) -> Path:
  if not path.parent.exists():
    return None
  basename = path.name.lower()
  for subpath in path.parent.iterdir():
    if subpath.name.lower() == basename:
      return subpath
  return None

# Returns True if all given dirs and files exist, case insensitive.
def validate_dirs_and_files(dirs: list[Path], files: list[Path]) -> bool:
  for directory in dirs:
    if not directory.is_dir():
      directory = find_case_insensitive(directory)
      if not directory:
        return False
      if not directory.is_dir():
        return False
  for file in files:
    if not file.is_file():
      file = find_case_insensitive(file)
      if not file:
        return False
      if not file.is_file():
        return False
  return True

# Returns True if given path is a path to CSP.
def is_csp(path: Path) -> bool:
  if not path.is_dir():
    return False
  csp_data = data.get('csp')
  common_dirs = csp_data.get('common-dirs')
  common_files = csp_data.get('common-files')
  for pathlist in common_dirs:
    subdir = path / Path(*pathlist)
    if not subdir.is_dir():
      return False
  for pathlist in common_files:
    subfile = path / Path(*pathlist)
    if not subfile.is_file():
      return False
  return True

# Returns True if given path is a path to a car skin.
def is_car_skin(path: Path) -> bool:
  preview_file = path / 'preview.jpg'
  livery_file = path / 'livery.png'
  required_dirs = [path]
  required_files = [preview_file, livery_file]
  return validate_dirs_and_files(required_dirs, required_files)

# Returns True if given path is a path to a car.
def is_car(path: Path) -> bool:
  # Making sure that either data dir or file exists
  data_file = path / 'data.acd'
  data_dir = path / 'data'
  if not (data_file.is_file() or data_dir.is_dir()):
    return False
  # Required dirs
  ui_dir = path / 'ui'
  sfx_dir = path / 'sfx'
  required_dirs = [path, ui_dir, sfx_dir]
  # Required files
  collider_file = path / 'collider.kn5'
  driver_pos_file = path / 'driver_base_pos.knh'
  tyre_shadow_files = [path / f'tyre_{i}_shadow.png' for i in range(4)]
  required_files = tyre_shadow_files + [collider_file, driver_pos_file]
  return validate_dirs_and_files(required_dirs, required_files)

# Returns True if given path is a path to a track layout.
def is_track_layout(path: Path) -> bool:
  data_dir = path / 'data'
  map_file = path / 'map.png'
  ui_dir = path.parent / 'ui' / path.name
  ui_file = ui_dir / 'ui_track.json'
  preview_file = ui_dir / 'preview.png'
  outline_file = ui_dir / 'outline.png'
  required_dirs = [path, data_dir, ui_dir]
  required_files = [map_file, ui_file, preview_file, outline_file]
  return validate_dirs_and_files(required_dirs, required_files)

# Returns True if given path is a path to a track.
def is_track(path: Path) -> bool:
  track_basename = path.name + '.kn5'
  track_file = path / track_basename
  ui_dir = path / 'ui'
  required_dirs = [path, ui_dir]
  required_files = [track_file]
  return validate_dirs_and_files(required_dirs, required_files)

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
  if not path.is_dir():
    return False
  for subpath in path.iterdir():
    if not subpath.is_file():
      continue
    if subpath.name == 'weather.ini':
      return True
  return False

# Returns True if given path is a path to a Python app.
def is_python_app(path: Path) -> bool:
  if not path.is_dir():
    return False
  py_basename = path.name + '.py'
  py_file = path / py_basename
  return py_file.is_file()

# Returns True if given path is a path to a Lua app.
def is_lua_app(path: Path) -> bool:
  manifest_file = path / 'manifest.ini'
  icon_file = path / 'icon.png'
  lua_basename = path.name + '.lua'
  lua_file = path / lua_basename
  required_dirs = [path]
  required_files = [manifest_file, icon_file, lua_file]
  return validate_dirs_and_files(required_dirs, required_files)

# Returns True if given path is a path to an app.
def is_app(path: Path) -> bool:
  return is_python_app(path) or is_lua_app(path)
