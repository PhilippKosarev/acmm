# Imports
from pathlib import Path
from libjam import notebook
import os, re

# Internal imports
from . import data, utils, validate_functions, install_functions, factory

# CSP data
re_csp_credits_tag = re.compile(r'\[/?[a-zA-Z0-9_]+(?:=[^\]]+)?\]')

# Size getters
def get_size(root: Path, items: list) -> int:
  size = 0
  entries = {entry.name.lower(): entry for entry in os.scandir(root)}
  for item in items:
    if type(item) is str:
      entry = entries.get(item.lower())
      if not entry:
        continue
      if not entry.is_file():
        continue
      size += os.stat(entry).st_size
    else:
      item, subitems = item
      entry = entries.get(item.lower())
      if not entry:
        continue
      if not entry.is_dir():
        continue
      size += get_size(entry, subitems)
  return size

def get_csp_size(self) -> int:
  extension_dir = self.path / 'extension'
  dwrite_file = self.path / 'dwrite.dll'
  return utils.get_dir_size(extension_dir) + utils.get_file_size(dwrite_file)

def get_pure_size(self) -> int:
  all_files = data.get('pure-all-files')
  return get_size(self.path, all_files)

def get_sol_size(self) -> int:
  all_files = data.get('sol-all-files')
  return get_size(self.path, all_files)

# UI info getters
def get_csp_ui_info(self) -> dict:
  manifest_file = self.path / 'extension' / 'config' / 'data_manifest.ini'
  if not manifest_file.is_file():
    return {}
  desired_info = {
    # 'ℹ' is different from 'i' here
    'ℹ': [
      ('preview',     'preview'),
      ('description', 'description'),
      ('url',         'url'),
    ],
    'VERSION': [
      ('shaders_patch',       'version'),
      ('shaders_patch_build', 'build'),
    ],
  }
  # Reading manifest
  manifest = notebook.read_ini(str(manifest_file))
  info = {}
  for desired_section in desired_info:
    section_values = manifest.get(desired_section)
    for original_key, renamed_key in desired_info.get(desired_section):
      value = section_values.get(original_key)
      if value is None:
        continue
      info[renamed_key] = value
  # Credits
  credits_file = self.path / 'extension' / 'config' / 'data_credits.txt'
  if not credits_file.is_file():
    return info
  credits = credits_file.read_text()
  credits = re.sub(re_csp_credits_tag, '', credits)
  info['credits'] = credits
  # Returning
  return info

def get_pure_ui_info(self) -> dict:
  weather_dir = self.path / 'extension' / 'weather'
  gamma_manifest = weather_dir / 'pure' / 'manifest.ini'
  lcs_manifest = weather_dir / 'Pure LCS' / 'manifest.ini'
  gamma_data = notebook.read_ini(str(gamma_manifest)).get('ABOUT')
  data = {'gamma': gamma_data}
  if lcs_manifest.is_file():
    data['lcs'] = notebook.read_ini(str(lcs_manifest)).get('ABOUT')
  return data

def get_sol_ui_info(self) -> dict:
  manifest_file = self.path / 'extension' / 'weather' / 'sol' / 'manifest.ini'
  data = notebook.read_ini(str(manifest_file)).get('ABOUT')
  return data

# ID getters
def get_csp_id(self) -> str:
  info = self.get_ui_info()
  if info is None:
    return 'csp'
  version = info.get('version')
  return f'csp_v{version}'

def get_pure_id(self) -> str:
  info = self.get_ui_info().get('gamma')
  if info is None:
    return 'pure'
  version = info.get('version')
  return f'pure_v{version}'

def get_sol_id(self) -> str:
  info = self.get_ui_info()
  if info is None:
    return 'sol'
  version = info.get('version')
  return f'sol_v{version}'

# Delete functions
def delete(root: Path, items: list[str or tuple[str, list]]):
  assert items
  entries = {entry.name.lower(): entry for entry in os.scandir(root)}
  for item in items:
    if type(item) is str:
      entry = entries.get(item.lower())
      if not entry:
        continue
      if not entry.is_file():
        continue
      os.remove(entry)
    else:
      item, subitems = item
      entry = entries.get(item.lower())
      if not entry:
        continue
      if not entry.is_dir():
        continue
      delete(entry, subitems)
  if len(list(os.scandir(root))) == 0:
    os.rmdir(root)

def delete_csp(self):
  extension_dir = self.path / 'extension'
  utils.unlink_dir(extension_dir)

def delete_pure(self):
  all_files = data.get('pure-all-files')
  delete(self.path, all_files)

def delete_sol(self):
  all_files = data.get('sol-all-files')
  delete(self.path, all_files)

# Mapping functions
csp_functions = {
  'get_id': get_csp_id,
  'get_size': get_csp_size,
  'get_ui_info': get_csp_ui_info,
  'delete': delete_csp,
}
pure_functions = {
  'get_id': get_pure_id,
  'get_size': get_pure_size,
  'get_ui_info': get_pure_ui_info,
  'delete': delete_pure,
}
sol_functions = {
  'get_id': get_sol_id,
  'get_size': get_sol_size,
  'get_ui_info': get_sol_ui_info,
  'delete': delete_sol,
}

# Creating extensions
extensions_list = [
  (
    'CSP',
    None,
    validate_functions.is_csp,
    install_functions.install_csp,
    [],
    csp_functions,
  ),
  (
    'Pure',
    None,
    validate_functions.is_pure,
    install_functions.install_pure,
    [],
    pure_functions,
  ),
  (
    'SOL',
    None,
    validate_functions.is_sol,
    install_functions.install_sol,
    [],
    sol_functions,
  ),
]

Extension = factory.create('Extension', extensions_list)
