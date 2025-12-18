# Imports
from pathlib import Path

# Fetch functions
def get_paths(path: Path) -> iter[Path]:
  return path.iterdir()

def get_app_dirs(path: Path) -> iter[Path]:
  python_dir = path / 'python'
  app_dirs = list(python_dir.iterdir())
  lua_dir = path / 'lua'
  if lua_dir.is_dir():
    app_dirs += list(lua_dir.iterdir())
  return app_dirs
