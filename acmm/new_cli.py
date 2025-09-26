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

# Helper vars
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
}

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

def asset_class_to_key(asset_class: acmm.Asset) -> str:
  return asset_class.__name__.lower()

def categorise_assets(assets: list) -> list:
  categories = {}
  for asset in assets:
    key = asset_class_to_key(type(asset))
    if key not in categories:
      categories[key] = [asset]
    else:
      categories[key].append(asset)
  return list(categories.values())

def filter_assets_by_origin(assets: list, options: dict) -> list:
  filtered_assets = []
  for asset in assets:
    if options.get('all'):
      filtered_assets.append(asset)
    elif options.get('kunos'):
      if asset.get_origin() is acmm.AssetOrigin.KUNOS:
        filtered_assets.append(asset)
    else:
      if asset.get_origin() is acmm.AssetOrigin.MOD:
        filtered_assets.append(asset)
  return filtered_assets

def get_installed_assets(manager: acmm.Manager, options: dict) -> list:
  asset_classes = acmm.Asset.get_asset_classes()
  assets = []
  for asset_class in asset_classes:
    # Checking if category is enabled
    key = asset_class_to_key(asset_class)
    enabled = options.get(key)
    if enabled is not None:
      if not enabled:
        continue
    # Fetching
    assets += (
      filter_assets_by_origin(manager.fetch_assets(asset_class), options)
    )
  return assets

def filter_by_id(
  assets: list, search_terms: list,
) -> list:
  matching = []
  search_terms = [search_term.lower() for search_term in search_terms]
  for asset in assets:
    asset_id = asset.get_id()
    for search_term in search_terms:
      if search_term in asset_id.lower():
        matching.append(asset)
  return matching

def print_assets(assets: list, include_size: bool):
  categories = categorise_assets(assets)
  sections = []
  for assets in categories:
    heading = [
      typewriter.bolden(asset_info.get(type(assets[0])).get('title') + ':'),
      '(',
      str(len(assets)),
    ]
    if include_size:
      size = sum([asset.get_size() for asset in assets])
      size = drawer.get_readable_filesize(size)
      heading += [
        '|',
        str(round(size[0], 1)),
        size[1].upper(),
      ]
    heading += [')']
    asset_ids = [asset.get_id() for asset in assets]
    asset_ids.sort()
    for index in range(len(asset_ids)):
      asset_id = asset_ids[index]
      if ' ' in asset_id:
        asset_id = f'"{asset_id}"'
        asset_ids[index] = asset_id
    sections.append(
      ' '.join(heading) + '\n' + typewriter.list_to_columns(asset_ids) + '\n'
    )
  typewriter.print('\n'.join(sections))

def get_delay(num: int, delay_min: float, delay_max: float) -> float:
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
    self.manager = acmm.Manager(AC_DIR)

  # Lists installed mods.
  def list(self, args, options):
    assets = get_installed_assets(self.manager, options)
    if len(assets) == 0:
      typewriter.print('No mods found.')
    else:
      print_assets(assets, options.get('size'))
    return 0

  # Deletes request mods.
  def remove(self, args, options):
    # Fetching and filtering mods
    assets = get_installed_assets(self.manager, options)
    assets = filter_by_id(assets, args)
    n_assets = len(assets)
    if len(assets) == 0:
      typewriter.print('No mods found matching any of the terms.')
      return 0
    print_assets(assets, options.get('size'))
    try:
      if not flashcard.yn_prompt(f'Remove the listed {n_assets} mods?'):
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Deleting
    delay = get_delay(num=n_assets, delay_min=0, delay_max=0.2)
    deleted = []
    for asset in assets:
      asset_id = asset.get_id()
      try:
        asset_path = asset.get_path()
        typewriter.print_status(f"Deleting '{asset_id}'...")
        time.sleep(delay)
        drawer.trash_path(asset_path)
      except KeyboardInterrupt:
        typewriter.print('Deletion aborted.')
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
    # Unpacking
    try:
      for path in args:
        if drawer.is_file(path):
          if not drawer.is_archive_supported(path):
            typewriter.print(f"Unsupported file '{path}'.")
            return 1
          basename = drawer.get_basename(path)
          def print_extract_progress(done: int, todo: int):
            typewriter.print_progress(f"Extracting '{basename}'", done, todo)
          typewriter.print_status(f"Extracting '{basename}'...")
          path = drawer.extract_archive(path, TEMP, print_extract_progress)
        elif not drawer.is_folder(path):
          typewriter.print(f"File '{path}' not found.")
          return -1
        unpacked.append(path)
    except KeyboardInterrupt:
      typewriter.print('Archive extraction aborted.')
      return 130
    # Searching for mods
    typewriter.print_status('Searching for mods...')
    try:
      assets = []
      for path in unpacked:
        assets += self.manager.find(path)
    except KeyboardInterrupt:
      typewriter.print('Mod search aborted.')
      return 130
    # Checking found mods
    if len(assets) == 0:
      typewriter.print('No mods found.')
      return 0
    # Getting user confirmation
    print_assets(assets, True)
    try:
      if not flashcard.yn_prompt("Install listed mods?"):
        typewriter.print("Installation cancelled.")
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Installing
    installed = []
    to_install = len(assets)
    for asset in assets:
      asset_id = asset.get_id()
      try:
        typewriter.print_progress(f"Installing '{asset_id}'", len(installed), to_install)
        asset = self.manager.install(asset, acmm.InstallMethod.UPDATE)
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
    asset_class_to_key(asset_class)
    for asset_class in acmm.Asset.get_asset_classes()
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
    'size': {
      'long': ['size'], 'short': ['s'],
      'description': 'Show category size',
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
