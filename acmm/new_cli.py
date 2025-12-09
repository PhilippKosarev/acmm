#! /usr/bin/env python3

# Imports
from libjam import Captain, drawer, typewriter, flashcard
import sys, os, time, math

# Internal imports
from config import assetto_dir
import acmm

# Helper vars
TEMP = drawer.get_temp() + '/acmm'
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
    typewriter.print_status('Cleaning temp dir...')
    drawer.delete_folder(TEMP)
  drawer.make_folder(TEMP)
  typewriter.clear_lines(0)

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

def filter_assets_by_origin(assets: list, opts: dict) -> list:
  filtered_assets = []
  for asset in assets:
    if opts.get('all'):
      filtered_assets.append(asset)
    elif opts.get('kunos'):
      if asset.get_origin() is acmm.AssetOrigin.KUNOS:
        filtered_assets.append(asset)
    else:
      if asset.get_origin() is acmm.AssetOrigin.MOD:
        filtered_assets.append(asset)
  return filtered_assets

def get_installed_assets(manager: acmm.Manager, opts: dict) -> list:
  asset_classes = acmm.Asset.get_asset_classes()
  assets = []
  for asset_class in asset_classes:
    # Checking if category is enabled
    key = asset_class_to_key(asset_class)
    enabled = opts.get(key)
    if enabled is not None:
      if not enabled:
        continue
    # Fetching
    assets += (
      filter_assets_by_origin(manager.fetch_assets(asset_class), opts)
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
      ' '.join(heading) + '\n' + typewriter.list_to_columns(asset_ids, 0, 2, 2) + '\n'
    )
  print('\n'.join(sections))

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
  'A CLI mod manager for Assetto Corsa'
  def __init__(self, ac_dir: str):
    self.manager = acmm.Manager(ac_dir)

  def list(self):
    'Lists installed mods'
    assets = get_installed_assets(self.manager, opts)
    if len(assets) == 0:
      typewriter.print('No mods found.')
    else:
      print_assets(assets, opts.get('size'))
    return 0

  def install(self, path: str, *additional_paths):
    'Installs the specified mod(s)'
    # Combining paths
    paths = [path] + list(additional_paths)
    # Checking paths
    for path in paths:
      if not drawer.exists(path):
        print(f"{path}: file not found.")
        return 1
      if drawer.is_file(path) and not drawer.is_archive_supported(path):
        print(f"{path}: unsupported archive type.")
        return 1
    # Cleaning temp dir
    clean_temp_dir()
    unpacked = []
    # Unpacking
    try:
      for path in paths:
        if drawer.is_file(path):
          basename = drawer.get_basename(path)
          def print_extract_progress(done: int, todo: int):
            typewriter.print_progress(f"Extracting '{basename}'", done, todo)
          out_dir = TEMP + '/' + basename
          drawer.extract_archive(path, out_dir, print_extract_progress)
        else:
          out_dir = path
        unpacked.append(out_dir)
    except KeyboardInterrupt:
      typewriter.clear_lines(0)
      print('Archive extraction aborted.')
      return 130
    # Searching for mods
    typewriter.print_status('Searching for mods...')
    try:
      assets = []
      for path in unpacked:
        assets += self.manager.find(path)
    except KeyboardInterrupt:
      typewriter.clear_lines(0)
      print('Mod search aborted.')
      return 130
    typewriter.clear_lines(0)
    # Checking found mods
    if len(assets) == 0:
      print('No mods found.')
      return 0
    # Getting user confirmation
    print_assets(assets, opts.get('size'))
    try:
      if not flashcard.yn_prompt("Install listed mods?"):
        print("Installation cancelled.")
        return 0
    except KeyboardInterrupt:
      print()
      return 130
    # Installing
    installed = []
    n_assets = len(assets)
    for asset in assets:
      asset_id = asset.get_id()
      try:
        typewriter.print_progress(f"Installing '{asset_id}'", len(installed), n_assets)
        asset = self.manager.install(asset, acmm.InstallMethod.UPDATE)
        installed.append(asset)
      except KeyboardInterrupt:
        typewriter.print('Installation aborted.')
        if len(installed) == 0:
          print('No mods were installed yet.')
        else:
          print('Already installed these mods:')
          print_assets(installed, opts.get('size'))
        return 130
      except NotImplementedError:
        print(f"Error: Mod '{asset_id}' is not installable. Aborting installation.")
        if len(installed) > 0:
          print('Already installed these mods:')
          print_assets(installed, opts.get('size'))
        return 1
    clean_temp_dir()
    print(f"Installed {len(installed)} mods.")
    return 0

  def remove(self, *mod_id: str):
    'Removes specified mod(s)'
    if not mod_id:
      mod_id = ['']
    # Fetching and filtering mods
    assets = get_installed_assets(self.manager, opts)
    assets = filter_by_id(assets, mod_id)
    n_assets = len(assets)
    if len(assets) == 0:
      typewriter.print('No mods found matching any of the terms.')
      return 0
    print_assets(assets, opts.get('size'))
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
        typewriter.print_status(f"Deleting '{asset_id}'...")
        time.sleep(delay)
        asset.trash()
        # drawer.trash_path(asset_path)
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


# Creating the CLI
cli = CLI(assetto_dir)
captain = Captain(cli)
# Adding options for filtering by asset category
fetchable_categories = [
  asset_class_to_key(asset_class)
  for asset_class in acmm.Asset.get_asset_classes()
]
for category in fetchable_categories:
  captain.add_option(
    category, [category, category[0]],
    f'Only list/remove {category} mods',
  )
# Adding other options
captain.add_option('all',   ['all', 'A'],   'Do not filter out Kunos assets')
captain.add_option('kunos', ['kunos', 'k'], 'Filter out non Kunos assets')
captain.add_option('size',  ['size', 's'],  'Show mod size on disk')

def main() -> int:
  # Parsing user input
  global opts
  function, args, opts = captain.parse()
  # Enabling all filters if none are active
  n_enabled_categories = sum([
    1 for category in fetchable_categories if opts.get(category)
  ])
  if n_enabled_categories == 0:
    for category in fetchable_categories:
      opts[category] = True
  # Running and returning
  return function(*args)

if __name__ == '__main__':
  sys.exit(main())
