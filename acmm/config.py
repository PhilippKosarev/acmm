# Imports
from libjam import notebook, drawer
import vdf

# Backend
import acmm

# Defining default config
likely_steam_dirs = [
  '~/.local/share/Steam',
  '~/.var/app/com.valvesoftware.Steam',
  'C:/Program Files (x86)/Steam',
]
default_steam_dir = None
for directory in likely_steam_dirs:
  if drawer.is_folder(directory):
    default_steam_dir = directory
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
if not drawer.exists(steam_dir) or not steam_dir:
  config_obj.on_error(f"Specified 'steam-directory' does not exist")
# Getting ac dir
libraryfolders = f'{steam_dir}/config/libraryfolders.vdf'
try:
  libraryfolders = vdf.loads(drawer.read_file(libraryfolders))
except FileNotFoundError:
  config_obj.on_error(
    f"Invalid Steam installation at '{steam_dir}'. "
    f"The file '{libraryfolders}' does not exist."
  )
libraryfolders = list(libraryfolders.get('libraryfolders').values())
found_in = None
# Finding the right steamapps dir
for item in libraryfolders:
  apps = item.get('apps')
  if appid in apps:
    found_in = item.get('path')
    break
if found_in is None:
  config_obj.on_error('Assetto Corsa is not installed')

# Getting assetto dir
steamapps = f'{found_in}/steamapps'
compatdata = f'{steamapps}/compatdata'
appmanifest = f'{steamapps}/appmanifest_{appid}.acf'
try:
  appmanifest = vdf.loads(drawer.read_file(appmanifest))
except FileNotFoundError:
  config_obj.on_error(
    f"Invalid Steam installation at '{steam_dir}'. "
    f"The file '{appmanifest}' does not exist."
  )
appmanifest = appmanifest.get('AppState')
install_dir = appmanifest.get('installdir')
assetto_dir = f'{steamapps}/common/{install_dir}'

try:
  acmm.Manager.check_ac_dir(assetto_dir)
except FileNotFoundError:
  config_obj.on_error('Assetto Corsa directory does not exist')
except acmm.InvalidACDir:
  config_obj.on_error('Invalid Assetto Corsa directory')
