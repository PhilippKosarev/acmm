#! /usr/bin/env python3

# Imports
from libjam import Captain, drawer, typewriter, flashcard
from pathlib import Path
import sys, time, math

# Internal imports
from . import acmm
from .shared import manager, get_temp_dir
from . import extension_cli

# Helper vars
asset_titles = {
  acmm.Asset.Car: 'Cars',
  acmm.Asset.Track: 'Tracks',
  acmm.Asset.PPFilter: 'PP Filters',
  acmm.Asset.Weather: 'Weather',
  acmm.Asset.App: 'Apps',
}

# Helper functions
def asset_class_to_key(asset_class: acmm.Asset) -> str:
  return asset_class.__name__.lower()

def get_installed_assets() -> list[acmm.Asset]:
  asset_classes = acmm.Asset.get_classes()
  all_assets = []
  for asset_class in asset_classes:
    # Checking if category is enabled
    key = asset_class_to_key(asset_class)
    enabled = opts.get(key)
    if not enabled:
      continue
    # Fetching
    assets = manager.fetch_assets(asset_class)
    filtered_assets = []
    for asset in assets:
      if opts.get('all'):
        filtered_assets.append(asset)
      elif opts.get('kunos') and opts.get('dlc'):
        if asset.get_origin() is not acmm.AssetOrigin.MOD:
          filtered_assets.append(asset)
      elif opts.get('kunos'):
        if asset.get_origin() is not acmm.AssetOrigin.KUNOS:
          filtered_assets.append(asset)
      elif opts.get('dlc'):
        if asset.get_origin() is acmm.AssetOrigin.DLC:
          filtered_assets.append(asset)
      else:
        if asset.get_origin() is acmm.AssetOrigin.MOD:
          filtered_assets.append(asset)
    all_assets += filtered_assets
  return all_assets

def filter_by_id(
  assets: list[acmm.Asset], search_terms: list,
) -> list[acmm.Asset]:
  matching = []
  search_terms = [search_term.lower() for search_term in search_terms]
  for asset in assets:
    asset_id = asset.get_id()
    for search_term in search_terms:
      if search_term in asset_id.lower():
        matching.append(asset)
  return matching

def categorise_assets(assets: list[acmm.Asset]) -> list[acmm.Asset]:
  categories = {}
  for asset in assets:
    key = asset_class_to_key(type(asset))
    if key not in categories:
      categories[key] = [asset]
    else:
      categories[key].append(asset)
  return list(categories.values())

def print_assets(assets: list[acmm.Asset]):
  categories = categorise_assets(assets)
  sections = []
  for assets in categories:
    asset_class = assets[0].__class__
    if hasattr(acmm.Extension, asset_class.__name__):
      title = 'Extensions'
    else:
      title = asset_titles.get(asset_class)
      assert title
    # Making a category heading
    heading = typewriter.bolden(title + ': ')
    if opts.get('size'):
      size = sum([asset.get_size() for asset in assets])
      size, units, _ = drawer.get_readable_filesize(size)
      size = round(size, 1)
      units = units.upper()
      heading += f'( {len(assets)} | {size} {units} )'
    else:
      heading += f'({len(assets)})'
    # Making asset_id list
    asset_ids = [asset.get_id() for asset in assets]
    asset_ids.sort()
    # Adding quotes around asset ids with spaces
    for i, asset_id in enumerate(asset_ids):
      if ' ' in asset_id:
        asset_ids[i] = f'"{asset_id}"'
    asset_ids = typewriter.list_to_columns(asset_ids, 0, 2, 2)
    # Appending section
    sections.append(f'{heading}\n{asset_ids}\n')
  # Printing
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

class CLI:
  'A CLI mod manager for Assetto Corsa'
  def list(self):
    'List installed mods'
    assets = get_installed_assets()
    if not assets:
      print('No mods found.')
    else:
      print_assets(assets)

  def install(self, path: str, *additional_paths):
    'Install the specified mod(s)'
    # Checking paths
    paths = [path] + list(additional_paths)
    for i in range(len(paths)):
      path = Path(paths[i])
      if not path.exists():
        print(f"{path}: file not found.")
        return 1
      if path.is_file() and not drawer.is_archive_supported(str(path)):
        print(f"{path}: unsupported filetype.")
        return 1
      paths[i] = path
    # Unpacking
    with get_temp_dir() as temp_dir:
      try:
        unpacked = []
        for path in paths:
          if path.is_file():
            out_dir = Path(temp_dir) / path.name
            def print_extract_progress(done: int, todo: int):
              typewriter.print_progress(f"Extracting '{path.name}'", done, todo)
            drawer.extract_archive(str(path), str(out_dir), print_extract_progress)
            typewriter.clear_lines(0)
            unpacked.append(out_dir)
          else:
            unpacked.append(path)
      except KeyboardInterrupt:
        typewriter.clear_lines(0)
        print('Archive extraction aborted.')
        return 130
      # Searching for mods
      assets = manager.find_assets(unpacked)
      # Checking found mods
      if not assets:
        print('No mods found.')
        return 0
      # Getting user confirmation
      print_assets(assets)
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
          asset = manager.install(asset, acmm.InstallMethod.UPDATE)
          installed.append(asset)
        except KeyboardInterrupt:
          typewriter.clear_lines(0)
          typewriter.print('Installation aborted.')
          if len(installed) == 0:
            print('No mods were installed yet.')
          else:
            print('Already installed these mods:')
            print_assets(installed)
          return 130
        except NotImplementedError:
          typewriter.clear_lines(0)
          print(f"Error: Mod '{asset_id}' is not installable. Aborting installation.")
          if len(installed) > 0:
            print('Already installed these mods:')
            print_assets(installed)
          return 1
      typewriter.clear_lines(0)
      print(f'Installed {len(installed)} mods.')

  def remove(self, *mod_id):
    'Remove specified mod(s)'
    if not mod_id:
      mod_id = ['']
    # Fetching and filtering mods
    assets = get_installed_assets()
    assets = filter_by_id(assets, mod_id)
    n_assets = len(assets)
    if len(assets) == 0:
      typewriter.print('No mods found matching any of the terms.')
      return 0
    print_assets(assets)
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
        asset.delete()
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

  def extension(self, *args):
    'Manage your extensions'
    return extension_cli.run_as_subcli(args, 'acmm-extension')


# Creating the CLI
cli = CLI()
captain = Captain(cli)
# Adding options for filtering by asset category
fetchable_categories = [
  asset_class_to_key(asset_class)
  for asset_class in acmm.Asset.get_classes()
]
for category in fetchable_categories:
  captain.add_option(
    category, [category, category[0]],
    f'Filter for {category} assets',
  )
# Adding other options
captain.add_option('all',   ['all', 'A'],   'Show all assets')
captain.add_option('kunos', ['kunos', 'k'], 'Show Kunos assets')
captain.add_option('dlc',   ['dlc', 'd'],   'Show DLC assets')
captain.add_option('size',  ['size', 's'],  "Show mods' disk usage")

def main() -> int:
  # Checking whether to use the extension subcli
  all_args = sys.argv[1:]
  for i, arg in enumerate(all_args):
    if arg.startswith('-'):
      continue
    if arg == 'extension':
      return cli.extension(*all_args[i+1:])
  # Parsing user input
  global opts
  function, args, opts = captain.parse(all_args)
  # Enabling all filters if none are active
  enabled_categories = 0
  for category in fetchable_categories:
    if opts.get(category):
      enabled_categories += 1
  if enabled_categories == 0:
    for category in fetchable_categories:
      opts[category] = True
  # Running and returning
  return function(*args)

if __name__ == '__main__':
  sys.exit(main())
