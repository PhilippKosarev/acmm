# Imports
from pathlib import Path

# Gets all paths from given directory, recursively.
def get_paths_recursive(directory: Path) -> list[Path]:
  paths = []
  for path in directory.iterdir():
    paths.append(path)
    if path.is_dir():
      paths += get_paths_recursive(path)
  return paths

def unlink_dir(directory: Path):
  for path in directory.iterdir():
    if path.is_dir():
      unlink_dir(path)
    else:
      path.unlink()
  directory.rmdir()

# Returns the size of a given file.
def get_file_size(path: Path) -> int:
  return path.stat().st_size

# Returns the size of a given directory.
def get_dir_size(path: Path) -> int:
  size = get_file_size(path)
  subpaths = get_paths_recursive(path)
  for subpath in subpaths:
    size += get_file_size(subpath)
  return size

# Returns the size of a given file or directory.
def get_size(path: Path) -> int:
  if path.is_dir():
    return get_dir_size(path)
  return get_file_size(path)
