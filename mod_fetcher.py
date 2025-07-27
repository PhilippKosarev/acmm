# Imports
import pycountry
from libjam import drawer
# Internal imports
from info_gatherer import InfoGatherer
info_gatherer = InfoGatherer()

# Helper functions
def get_folders_sorted(path: str) -> list:
  folders = drawer.get_folders(path)
  folders.sort()
  return folders

def get_files_sorted(path: str) -> list:
  files = drawer.get_files(path)
  files.sort()
  return files

# Fetches the installed mods.
class ModFetcher:

  # Returns installed cars.
  def fetch_cars(self, AC_DIR: str, include: list = []) -> dict:
    cars = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = get_folders_sorted(f'{AC_DIR}/content/cars')
    for mod_path in folders:
      mod_id, mod_info, origin = info_gatherer.get_car_info(mod_path, include)
      cars[origin][mod_id] = mod_info
    return cars

  # Returns installed tracks.
  def fetch_tracks(self, AC_DIR: str, include: list = []) -> dict:
    tracks = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = get_folders_sorted(f'{AC_DIR}/content/tracks')
    for mod_path in folders:
      mod_id, mod_info, origin = info_gatherer.get_track_info(mod_path, include)
      tracks[origin][mod_id] = mod_info
    return tracks

  # Returns installed apps.
  def fetch_apps(self, AC_DIR: str, include: list = []) -> dict:
    apps = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = drawer.get_folders(f'{AC_DIR}/apps/python') + drawer.get_folders(f'{AC_DIR}/apps/lua')
    folders.sort()
    for mod_path in folders:
      mod_id, mod_info, origin = info_gatherer.get_app_info(mod_path, include)
      apps[origin][mod_id] = mod_info
    return apps

  # Returns installed PP filters.
  def fetch_ppfilters(self, AC_DIR: str, include: list = []) -> dict:
    ppfilters = {'kunos': {}, 'dlc': {}, 'mod': {}}
    files = get_files_sorted(f'{AC_DIR}/system/cfg/ppfilters')
    for mod_path in files:
      mod_id, mod_info, origin = info_gatherer.get_ppfilter_info(mod_path, include)
      ppfilters[origin][mod_id] = mod_info
    return ppfilters

  # Returns installed weather.
  def fetch_weather(self, AC_DIR: str, include: list = []) -> dict:
    weather = {'kunos': {}, 'dlc': {}, 'mod': {}}
    folders = get_folders_sorted(f'{AC_DIR}/content/weather')
    for mod_path in folders:
      mod_id, mod_info, origin = info_gatherer.get_weather_info(mod_path, include)
      weather[origin][mod_id] = mod_info
    return weather
