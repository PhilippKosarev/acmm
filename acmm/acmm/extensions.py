# Imports
from pathlib import Path
from libjam import notebook
import re

# Internal imports
from . import utils, validate_functions, install_functions, factory

# CSP data
re_csp_credits_tag = re.compile(r'\[/?[a-zA-Z0-9_]+(?:=[^\]]+)?\]')
csp_config_dir = ['extension', 'config']
csp_paths = {
  'manifest-file': [*csp_config_dir, 'data_manifest.ini'],
  'credits-file':  [*csp_config_dir, 'data_credits.txt'],
}

# CSP functions
def get_csp_size(self) -> int:
  extension_dir = self.path / 'extension'
  dwrite_file = self.path / 'dwrite.dll'
  return utils.get_dir_size(extension_dir) + utils.get_file_size(dwrite_file)

def get_csp_manifest_file(self) -> Path:
  manifest_file = csp_paths.get('manifest-file')
  manifest_file = self.path / Path(*manifest_file)
  if manifest_file.is_file():
    return manifest_file

def get_csp_credits_file(self) -> Path:
  credits_file = csp_paths.get('credits-file')
  credits_file = self.path / Path(*credits_file)
  if credits_file.is_file():
    return credits_file

def get_csp_ui_info(self) -> dict:
  manifest_file = get_csp_manifest_file(self)
  if not manifest_file:
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
  manifest = notebook.read_ini(manifest_file)
  info = {}
  for desired_section in desired_info:
    section_values = manifest.get(desired_section)
    for original_key, renamed_key in desired_info.get(desired_section):
      value = section_values.get(original_key)
      if value is None:
        continue
      info[renamed_key] = value
  credits_file = get_csp_credits_file(self)
  if not credits_file:
    return info
  credits = credits_file.read_text()
  credits = re.sub(re_csp_credits_tag, '', credits)
  info['credits'] = credits
  # Returning
  return info

def get_csp_id(self) -> str:
  info = self.get_ui_info()
  if info is None:
    return 'csp'
  version = info.get('version')
  return f'csp_v{version}'

def delete_csp(self):
  extension_dir = self.path / 'extension'
  utils.unlink_dir(extension_dir)

# CSP function map
csp_functions = {
  'get_id': get_csp_id,
  'get_size': get_csp_size,
  'get_ui_info': get_csp_ui_info,
  'delete': delete_csp,
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
]

# Assigning to container
class Extension:
  pass
factory.assign_assets(Extension, extensions_list)
Extension = Extension()
