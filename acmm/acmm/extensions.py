# Imports
from libjam import notebook
from pathlib import Path
import re

# Internal imports
from .base_asset import BaseAsset
from . import validate_functions, shared

# Variables
re_csp_credits_tag = re.compile(r'\[/?[a-zA-Z0-9_]+(?:=[^\]]+)?\]')

# A container for extension classes.
class Extension:

  class CSP(BaseAsset):
    validate = staticmethod(validate_functions.is_csp)
    def __init__(self, path):
      super().__init__(path)
      path = self.get_path()
      config_dir = path / 'extension' / 'config'
      self.data.update({
        'manifest-file': config_dir / 'data_manifest.ini',
        'credits-file': config_dir / 'data_credits.txt',
      })

    def get_id(self) -> str:
      info = self.get_ui_info()
      if info is None:
        return 'csp'
      version = info.get('version')
      return f'csp_v{version}'

    # Returns the size in bytes
    def get_size(self) -> int:
      path = self.get_path()
      extension_dir = path / 'extension'
      dwrite_file = path / 'dwrite.dll'
      size = 0
      size += extension_dir.stat().st_size
      size += dwrite_file.stat().st_size
      return size

    def get_manifest_file(self) -> Path:
      manifest_file = self.data.get('manifest-file')
      if manifest_file.is_file():
        return manifest_file

    def get_credits_file(self) -> Path:
      credits_file = self.data.get('credits-file')
      if credits_file.is_file():
        return credits_file

    def get_ui_info(self) -> dict:
      manifest_file = self.get_manifest_file()
      if not manifest_file:
        return
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
      credits_file = self.get_credits_file()
      if not credits_file:
        info
      credits = credits_file.read_text()
      credits = re.sub(re_csp_credits_tag, '', credits)
      info['credits'] = credits
      # Returning
      return info

    def delete(self):
      path = self.get_path()
      extension_dir = path / 'extension'
      shared.unlink_dir(extension_dir)


  # class Pure:
  #   pass


  # class SOL:
  #   pass
