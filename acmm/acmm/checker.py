# Imports
from libjam import drawer

# Functions
def file_exists(path: str, file: str) -> bool:
  return drawer.is_file(path + '/' + file)

def dir_exists(path: str, directory: str) -> bool:
  return drawer.is_folder(path + '/' + directory)

def either_file_or_dir_exists(path: str, item: tuple) -> bool:
  return (
    drawer.is_file(path + '/' + item[0]) or
    drawer.is_folder(path + '/' + item[1])
  )

def path_endswith(path: str, ending: str) -> bool:
  return path.endswith(ending)

def has_file_ending_with_either(path: str, item: tuple) -> bool:
  files = drawer.get_files(path)
  for file in files:
    for ending in item:
      if file.endswith(ending):
        return True
  return False
