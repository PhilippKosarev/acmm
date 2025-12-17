# Imports
from pathlib import Path
import shutil

# Internal imports
from .shared import *

# Install functions
def base_install(
  source: Path, destination: Path, install_method: InstallMethod,
) -> str:
  if install_method is InstallMethod.CLEAN:
    if destination.exists():
      destination.unlink()
    source.copy_into(destination)
  elif install_method is InstallMethod.UPDATE:
    if source.is_dir():
      destination = destination / source.name
      shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
      source.copy_into(destination)
  else:
    raise ValueError(f"Invalid install_method '{install_method}'")

def install_generic(
  asset_path: Path, install_dir: str, install_method: InstallMethod,
) -> Path:
  # Getting info
  base_install(asset_path, install_dir, install_method)
  return install_dir / asset_path.name

def install_app(
  asset_path: Path, install_dir: str, install_method: InstallMethod,
) -> Path:
  # Getting info
  lang_to_dir = {
    AppLang.PYTHON: 'python',
    AppLang.LUA: 'lua',
  }
  py_file = asset_path / asset_path.name + '.py'
  lua_file = asset_path / asset_path.name + '.lua'
  if py_file.is_file():
    lang = AppLang.PYTHON
  elif lua_file.is_file():
    lang = AppLang.LUA
  else:
    raise FileNotFoundError("Could not find the app's script file")
  lang_dir = lang_to_dir.get(lang)
  install_dir = install_dir / lang_dir
  base_install(asset_path, install_dir, install_method)
  return install_dir / asset_path.name

def install_csp(
  asset_path: Path, install_dir: Path, install_method: InstallMethod,
) -> Path:
  dwrite_file = asset_path / 'dwrite.dll'
  extension_dir = asset_path / 'extension'
  for destination in [dwrite_file, extension_dir]:
    base_install(destination, install_dir, install_method)
  return install_dir
