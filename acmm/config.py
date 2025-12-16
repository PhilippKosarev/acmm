# Imports
from libjam import notebook
from pathlib import Path
import vdf

# Backend
import acmm

home = Path.home()
anchor = Path(home.anchor)

# Defining default config
likely_steam_dirs = [
  home / '.local' / 'share' / 'Steam',
  home / '.var' / 'app' / 'com.valvesoftware.Steam' / 'data' / 'Steam',
  anchor / 'Program Files (x86)' / 'Steam',
  anchor / 'Program Files' / 'Steam',
]
default_steam_dir = None
for path in likely_steam_dirs:
  if path.is_dir():
    default_steam_dir = path
    break
default_values = {
  'steam-directory': default_steam_dir,
}
# Required config contents
template = '''\
# This is a configuration file for the acmm CLI
# https://github.com/PhilippKosarev/acmm

# Overrides the default detection
# steam-directory = ''
'''

# Initialising config
ledger = notebook.Ledger('acmm')
config_obj = ledger.init_config('config', default_values, template)
config_dict = config_obj.read()

# Getting steam dir
appid = '244210'
steam_dir = config_dict.get('steam-directory')
if steam_dir is None:
  config_obj.on_error(
    'Could not automatically find the Steam installation. '
    "Please specify the 'steam-directory' manually the config."
  )
steam_dir = Path(steam_dir)
if not steam_dir.is_dir():
  config_obj.on_error(f"Specified 'steam-directory' does not exist")
# Getting ac dir
libraryfolders_file = steam_dir / 'config' / 'libraryfolders.vdf'
if not libraryfolders_file.is_file():
  config_obj.on_error(
    f"Invalid Steam installation at '{steam_dir}'. "
    f"The file '{libraryfolders_file}' does not exist."
  )
libraryfolders = libraryfolders_file.read_text()
libraryfolders = vdf.loads(libraryfolders)
libraryfolders = list(libraryfolders.get('libraryfolders').values())
library_folder = None
# Finding the right steamapps dir
for item in libraryfolders:
  apps = item.get('apps')
  if appid in apps:
    library_folder = item.get('path')
    break
if library_folder is None:
  config_obj.on_error('Could not find Assetto Corsa')

# Getting assetto dir
library_dir = Path(library_folder)
steamapps_dir = library_dir / 'steamapps'
compatdata_dir = steamapps_dir / 'compatdata'
appmanifest_file = steamapps_dir / f'appmanifest_{appid}.acf'

if not appmanifest_file.is_file():
  config_obj.on_error(
    f"Invalid Steam installation at '{steam_dir}'. "
    f"The file '{appmanifest}' does not exist."
  )

appmanifest = appmanifest_file.read_text()
appmanifest = vdf.loads(appmanifest)
install_dir = appmanifest.get('AppState').get('installdir')
assetto_dir = steamapps_dir / 'common' / install_dir

try:
  acmm.Manager.check_assetto_dir(assetto_dir)
except FileNotFoundError:
  config_obj.on_error('Assetto Corsa directory does not exist')
except NotADirectoryError:
  config_obj.on_error('What the hell did you do to your Assetto Corsa installation?')
except acmm.InvalidAssettoDir:
  config_obj.on_error('Invalid Assetto Corsa directory')
