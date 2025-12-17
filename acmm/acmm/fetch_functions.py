# Imports
from pathlib import Path

# Fetch functions
def get_dirs(path: Path) -> list[Path]:
  dirs = [subpath for subpath in path.iterdir() if subpath.is_dir()]
  return dirs

def get_files(path: Path) -> list[Path]:
  files = [subpath for subpath in path.iterdir() if subpath.is_file()]
  return files

def get_app_dirs(path: Path) -> list[Path]:
  python_dir = path / 'python'
  app_dirs = get_dirs(python_dir)
  lua_dir = path / 'lua'
  if lua_dir.is_dir():
    app_dirs += get_dirs(lua_dir)
  return app_dirs
