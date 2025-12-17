# Imports
from pathlib import Path
from libjam import notebook
import html, re

# Shorthand vars
re_html_br_tag = re.compile('<.*?br.*?>')

# Gets all paths from given directory, recursively.
def get_paths_recursive(directory: Path) -> list[Path]:
  paths = []
  for path in directory.iterdir():
    paths.append(path)
    if path.is_dir():
      paths += get_paths_recursive(path)
  return paths

# Deletes the given directory
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

# Unescapes html sequences and like line break tags in a given dict.
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

# Reads a json file to a dict and unescapes html sequences.
def read_json(path: Path) -> dict:
  data = notebook.read_json(str(path))
  data = unescape_json_dict(data)
  return data

# Returns given path if it is a file, otherwise returns None.
def return_if_file(path: Path) -> Path or None:
  if path.is_file():
    return path
