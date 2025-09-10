#! /usr/bin/env python3

# Imports
from libjam import captain, drawer, typewriter, notebook, flashcard
import sys, os, time, math

# Internal imports
import acmm

# Handling config
HOME = drawer.get_home()
TEMP = drawer.get_temp() + '/acmm'
script_folder = os.path.dirname(os.path.realpath(__file__))
CONFIG_TEMPLATE_FILE = f"{script_folder}/config.toml.in"
CONFIG_DIR = f"{HOME}/.config/acmm"
CONFIG_FILE = f"{CONFIG_DIR}/config.toml"
notebook.check_config(CONFIG_TEMPLATE_FILE, CONFIG_FILE)
config = notebook.read_toml(CONFIG_FILE)

# Helper functions
def clean_temp_dir():
  if drawer.exists(TEMP):
    typewriter.print_status("Cleaning temp dir...")
    drawer.delete_folder(TEMP)
  drawer.make_folder(TEMP)

def get_ac_dir():
  # Checking AC_DIR
  ## Likely AC_DIR locations
  assettocorsa = acmm.data.get('ac_path_suffix')
  likely_ac_dirs = acmm.data.get('likely_ac_dirs')
  ## Getting AC_DIR
  paths = config.get('paths')
  if paths is not None:
    AC_DIR = paths.get("AC_DIR")
    if AC_DIR is None:
      for directory in likely_ac_dirs:
        if drawer.is_folder(directory):
          AC_DIR = directory
  else:
    AC_DIR = None
  # Checking AC_DIR
  if AC_DIR is None:
    print(
      f"""Assetto Corsa not found.
If Assetto Corsa is not installed in the default location, you might need to specify the path to '{assettocorsa}' in '{CONFIG_FILE}'."""
    )
    return None
  elif not drawer.is_folder(AC_DIR):
    print(
      f"""Path to Assetto Corsa specified in '{CONFIG_FILE}' does not exist."""
    )
    return None
  return AC_DIR

asset_info = {
  acmm.Asset.Car: {
    'title': 'Cars',
  },
  acmm.Asset.Track: {
    'title': 'Tracks',
  },
  acmm.Asset.PPFilter: {
    'title': 'PP Filters',
  },
  acmm.Asset.Weather: {
    'title': 'Weather',
  },
  acmm.Asset.App: {
    'title': 'Apps',
  },
  acmm.Asset.CSP: {
    'title': 'CSP',
  },
}

class AssetCategory:
  def __init__(self, assets: list):
    assets.sort(key=lambda asset: asset.get_id())
    self.size = sum([asset.get_size() for asset in assets])
    self.assets = tuple(assets)

  def __len__(self):
    return len(self.assets)

  def get_assets(self):
    return list(self.assets)

  def get_title(self):
    return asset_info.get(type(self.assets[0])).get('title')

  def get_print_string(self):
    asset_ids = [asset.get_id() for asset in self.assets]
    asset_ids = typewriter.list_to_columns(asset_ids)
    title = typewriter.bolden(self.get_title() + ':')
    size, units, _ = drawer.get_readable_filesize(self.size)
    size = f'{round(size, 1)} {units.upper()}'
    return f'{title} ( {len(self.assets)} | {size} )\n{asset_ids}\n'

  def print(self):
    typewriter.print(self.get_print_string())

class CategoryCollection:
  def __init__(self, categories: list):
    self.categories = tuple(categories)

  def __len__(self):
    return len(self.categories)

  def get_collections(self):
    return list(self.collections)

  def get_assets(self):
    assets = []
    for collection in self.categories:
      assets += collection.get_assets()
    return assets

  def print(self):
    strings = [category.get_print_string() for category in self.categories]
    typewriter.print('\n'.join(strings))

def filter_assets_by_origin(assets: list, options: dict):
  filtered_assets = []
  for asset in assets:
    if options.get('all'):
      filtered_assets.append(asset)
      continue
    elif options.get('kunos'):
      if asset.get_origin() is acmm.AssetOrigin.KUNOS:
        filtered_assets.append(asset)
        continue
    else:
      if asset.get_origin() is acmm.AssetOrigin.MOD:
        filtered_assets.append(asset)
        continue
  return filtered_assets

def get_installed_collection(fetcher: acmm.Fetcher, options: dict) -> CategoryCollection:
  asset_categories = []
  for category in acmm.FetchableAssetCategory:
    # Checking if category is enabled
    key = category.name.lower()
    enabled = options.get(key)
    if enabled is not None:
      if not enabled:
        continue
    # Fetching
    assets = fetcher.fetch(category)
    assets = filter_assets_by_origin(assets, options)
    if len(assets) > 0:
      asset_categories.append(AssetCategory(assets))
  return CategoryCollection(asset_categories)

def search_by_ids(
  search_terms: list, fetcher: acmm.Fetcher, options: dict,
) -> CategoryCollection:
  asset_categories = []
  for category in acmm.FetchableAssetCategory:
    # Checking if category is enabled
    key = category.name.lower()
    enabled = options.get(key)
    if enabled is not None:
      if not enabled:
        continue
    # Fetching
    assets = []
    for term in search_terms:
      assets += fetcher.search_by_id(category, term)
    assets = filter_assets_by_origin(assets, options)
    if len(assets) > 0:
      asset_categories.append(AssetCategory(assets))
  return CategoryCollection(asset_categories)

def get_delay(num: int, delay_min: float, delay_max: float):
  # Getting normalised inverse log
  try:
    delay = 1 / (math.log2(1 + num) * 0.5) * 0.5
  except (ValueError, ZeroDivisionError):
    delay = 1
  # Remapping
  delay = (delay * (delay_max - delay_min)) + delay_min
  return delay

# The command line interface for acmm.
class CLI:

  def __init__(self, AC_DIR: str):
    self.fetcher = acmm.Fetcher(AC_DIR)
    self.finder = acmm.Finder()
    self.installer = acmm.Installer(AC_DIR)

  # Lists installed mods.
  def list(self, args, options):
    collection = get_installed_collection(self.fetcher, options)
    if len(collection) == 0:
      typewriter.print('No mods found.')
    else:
      collection.print()
    return 0

  # Deletes request mods.
  def remove(self, args, options):
    # Fetching and filtering mods
    collection = search_by_ids(args, self.fetcher, options)
    if len(collection) == 0:
      typewriter.print('No mods found.')
      return 0
    collection.print()
    assets = collection.get_assets()
    try:
      if not flashcard.yn_prompt(f'Remove the listed {len(assets)} mods?'):
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Deleting
    delay = get_delay(num=len(assets), delay_min=0, delay_max=0.2)
    deleted = []
    for asset in assets:
      asset_id = asset.get_id()
      try:
        asset_path = asset.get_path()
        typewriter.print_status(f"Deleting '{asset_id}'...")
        time.sleep(delay)
        drawer.trash_path(asset_path)
      except KeyboardInterrupt:
        typewriter.print(f'Deletion aborted.')
        if len(deleted) == 0:
          typewriter.print('No mods were deleted.')
        else:
          typewriter.print('Already deleted these mods:')
          print(typewriter.list_to_columns(deleted))
        return 130
      deleted.append(asset_id)
    # Returning
    typewriter.print(f"Deleted {len(deleted)} mods.")
    return 0

  # Interface to install mods.
  def install(self, args, options):
    clean_temp_dir()
    unpacked = []
    # Processing mod paths
    for path in args:
      if not drawer.exists(path):
        typewriter.print(f"File '{path}' not found.")
        return -1
      # Unpacking
      if drawer.get_filetype(path) != 'folder':
        if not drawer.is_archive_supported(path):
          return typewriter.print(f"Unsupported file '{path}'")
        basename = drawer.get_basename(path)
        def print_extract_progress(done: int, todo: int):
          typewriter.print_progress(f"Extracting '{basename}'", done, todo)
        typewriter.print_status(f"Extracting '{basename}'...")
        try:
          drawer.extract_archive(
            path, TEMP, progress_function=print_extract_progress,
          )
        except KeyboardInterrupt:
          typewriter.print('Archive extraction aborted.')
          return 130
      else:
        unpacked.append(path)
    # Searching for mods
    typewriter.print_status('Searching for mods...')
    try:
      categories = [AssetCategory(i) for i in self.finder.find(TEMP)]
    except KeyboardInterrupt:
      typewriter.print('Mod search aborted.')
      return 130
    collection = CategoryCollection(categories)
    # Checking found mods
    if len(collection) == 0:
      typewriter.print('No mods found.')
      return 0
    # Getting user confirmation
    collection.print()
    try:
      if not flashcard.yn_prompt("Install listed mods?"):
        typewriter.print("Installation cancelled.")
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Installing mods
    assets = collection.get_assets()
    installed = []
    for asset in assets:
      asset_id = asset.get_id()
      try:
        typewriter.print_progress(f"Installing '{asset_id}'", len(installed), len(assets))
        asset = self.installer.install(asset, acmm.InstallMethod.UPDATE)
        installed.append(asset)
      except KeyboardInterrupt:
        typewriter.print('Installation aborted.')
        if len(installed) == 0:
          print('No mods were installed yet.')
        else:
          print('Already installed these mods:')
          asset_ids = [asset.get_id() for asset in installed]
          print(typewriter.list_to_columns(asset_ids))
        return 130
      except NotImplementedError:
        print(f"Error: Mod '{asset_id}' is not installable. Aborting installation.")
        if len(installed) > 0:
          print('Already installed these mods:')
          asset_ids = [asset.get_id() for asset in installed]
          print(typewriter.list_to_columns(asset_ids))
        return 1
    clean_temp_dir()
    typewriter.print(f"Installed {len(installed)} mods.")
    return 0


def main():
  AC_DIR = get_ac_dir()
  if AC_DIR is None:
    return 1
  cli = CLI(AC_DIR)

  # Commands and options
  description = 'A CLI mod manager for Assetto Corsa'
  commands = {
    'list': {
      'function': cli.list,
      'description': 'Lists installed mods',
    },
    # 'show': {
    #   'function': cli.show,
    #   'description': "Shows information about a mod",
    #   'arguments': ['mod id'],
    # },
    # 'csp-info': {
    #   'function': cli.csp_info,
    #   'description': "Shows CSP information",
    # },
    'install': {
      'function': cli.install,
      'description': 'Installs the specified mod(s)',
      'arguments': ['*paths'],
    },
    'remove': {
      'function': cli.remove,
      'description': 'Removes specified mod(s)',
      'arguments': ['*mod id'],
    },
  }
  fetchable_categories = [
    category.name.lower()
    for category in acmm.FetchableAssetCategory
  ]
  options = {}
  for category in fetchable_categories:
    options[category] = {
      'long': [category], 'short': [category[0]],
      'description': f'Only list/remove {category}',
    }
  options.update({
    'all': {
      'long': ['all'], 'short': ['A'],
      'description': 'Do not filter out Kunos assets',
    },
    'kunos': {
      'long': ['kunos'], 'short': ['k'],
      'description': 'Filter out non Kunos assets',
    },
  })

  # Parsing user input
  function, arguments, options = captain.sail(description, commands, options)

  # Enabling all filters if none are active
  enabled_categories = []
  for category in fetchable_categories:
    if options.get(category):
      enabled_categories.append(category)
  if len(enabled_categories) == 0:
    for category in fetchable_categories:
      options[category] = True

  # Running
  return function(arguments, options)

def main_cli():
  return main()

if __name__ == '__main__':
  sys.exit(main())
