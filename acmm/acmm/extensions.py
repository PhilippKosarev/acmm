# Imports
from libjam import drawer, notebook
import re

# Internal imports
from .base_asset import BaseAsset
from . import checker

# A container for extension classes.
class Extension:

  class CSP(BaseAsset):
    checks = [
      (checker.file_exists, 'dwrite.dll'),
      (checker.dir_exists,  'extension'),
    ]

    def __init__(self):
      super().__init__(*args, **kwargs)
      self.data.update({
        'manifest-file': f'{self.path}/extension/config/data_manifest.ini',
        'credits-file': f'{self.path}/extension/config/data_credits.txt',
      })

    def get_size(self, human_readable: bool = False) -> int or tuple:
      size = drawer.get_filesize(f'{self.path}/extension')
      size += drawer.get_filesize(f'{self.path}/dwrite.dll')
      if human_readable:
        return drawer.get_readable_filesize(size)
      return size

    def get_manifest_file(self):
      file = self.data.get('manifest-file')
      if drawer.is_file(file):
        return file

    def get_credits_file(self):
      file = self.data.get('credits-file')
      if drawer.is_file(file):
        return file

    def get_ui_info(self):
      info = {}
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
      manifest_file = self.get_manifest_file()
      if manifest_file is not None:
        manifest = notebook.read_ini(ini_file)
        for desired_section in desired_info:
          section_values = manifest.get(desired_section)
          for original_key, renamed_key in desired_info.get(desired_section):
            value = section_values.get(original_key)
            if value is None:
              continue
            info[renamed_key] = value
      # Adding credits
      credits_file = self.get_credits_file()
      if credits_file is not None:
        text = drawer.read_file(credits_file)
        info['credits'] = re.sub(r'\[/?[a-zA-Z0-9_]+(?:=[^\]]+)?\]', '', text)
      # Returning
      return info

    def get_id(self) -> str:
      info = self.get_ui_info()
      if info is None:
        return 'csp'
      version = info.get('version')
      return f'csp_v{version}'


  # class Pure:
  #   pass


  # class SOL:
  #   pass
