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

def get_origins():
  return {'kunos': [], 'dlc': [], 'mod': []}

# Fetches the installed mods.
class ModFetcher:

  # Returns installed cars.
  def fetch_cars(self, AC_DIR: str, include: list = []) -> dict:
    cars = get_origins()
    folders = get_folders_sorted(f'{AC_DIR}/content/cars')
    for path in folders:
      mod, origin = info_gatherer.get_car_info(path, include)
      cars[origin].append(mod)
    return cars

  # Returns installed tracks.
  def fetch_tracks(self, AC_DIR: str, include: list = []) -> dict:
    tracks = get_origins()
    folders = get_folders_sorted(f'{AC_DIR}/content/tracks')
    for path in folders:
      mod, origin = info_gatherer.get_track_info(path, include)
      tracks[origin].append(mod)
    return tracks

  # Returns installed apps.
  def fetch_apps(self, AC_DIR: str, include: list = []) -> dict:
    apps = get_origins()
    folders = drawer.get_folders(f'{AC_DIR}/apps/python') + drawer.get_folders(f'{AC_DIR}/apps/lua')
    folders.sort()
    for path in folders:
      mod, origin = info_gatherer.get_app_info(path, include)
      apps[origin].append(mod)
    return apps

  # Returns installed PP filters.
  def fetch_ppfilters(self, AC_DIR: str, include: list = []) -> dict:
    ppfilters = get_origins()
    files = get_files_sorted(f'{AC_DIR}/system/cfg/ppfilters')
    for path in files:
      mod, origin = info_gatherer.get_ppfilter_info(path, include)
      ppfilters[origin].append(mod)
    return ppfilters

  # Returns installed weather.
  def fetch_weather(self, AC_DIR: str, include: list = []) -> dict:
    weather = get_origins()
    folders = get_folders_sorted(f'{AC_DIR}/content/weather')
    for path in folders:
      mod, origin = info_gatherer.get_weather_info(path, include)
      weather[origin].append(mod)
    return weather
