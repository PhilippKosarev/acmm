#! /usr/bin/env python3

# Imports
from libjam import Captain, drawer, typewriter, cloud
import sys

# Internal imports
from . import acmm
from .shared import manager, temp_dir, clean_temp_dir

# Helper functions
def format_info(
  key_to_title: dict, info: dict, indent: int = 0, align_left: bool = False,
) -> str:
  indent = ' ' * indent
  items = {}
  for key in key_to_title:
    value = info.get(key).strip()
    title = key_to_title.get(key) + ':'
    items[title] = value
  longest_title = len(sorted(items.keys(), key=len, reverse=True)[0])
  lines = []
  for title, value in items.items():
    if align_left:
      title = f'{title:<{longest_title}}'
    else:
      title = f'{title:>{longest_title}}'
    title = typewriter.bolden(title)
    lines.append(f'{indent}{title} {value}')
  return '\n'.join(lines)

# The csp subcli for acmm.
class CLI:
  'Manages your Assetto Corsa extensions'
  def csp_info(self):
    'Prints information about CSP'
    csp = manager.fetch_extension(acmm.Extension.CSP)
    if csp is None:
      print('CSP is not installed.')
      return 1
    info = csp.get_ui_info()
    size = csp.get_size()
    size, units, _ = drawer.get_readable_filesize(size)
    size = round(size, 1)
    units = units.upper()
    info.update({'size': f'{size} {units}'})
    key_to_title = {
      'version': 'Version',
      'build': 'Build number',
      'size': 'Size',
      'url': 'Development plan',
      'description': 'Description',
      # 'credits': 'Credits',
    }
    print(format_info(key_to_title, info))

  def install_csp(self):
    'Downloads and installs CSP'
    clean_temp_dir()
    typewriter.print_status('Fetching available versions...')
    versions = manager.fetch_csp_versions()
    keys = list(versions.keys())
    keys.reverse()
    typewriter.clear_lines(0)
    title = typewriter.bolden('Available versions:')
    printable_keys = []
    for i, key in enumerate(keys):
      printable_keys.append(f'{i+1}) {key}')
    printable_keys = typewriter.list_to_columns(printable_keys, spacing=2)
    print(f'{title}\n{printable_keys}\n')
    n_keys = len(keys)
    prompt = typewriter.bolden(
      f'Input which version to install (1-{n_keys}, 0 to abort): '
    )
    try:
      while True:
        choice = input(prompt).strip()
        if choice == '':
          continue
        elif choice == '0':
          return 1
        elif choice in [str(n) for n in range(1, n_keys+1)]:
          chosen_key = keys[int(choice) - 1]
          break
        elif choice in keys:
          chosen_key = choice
          break
        else:
          print('Invalid input.')
    except KeyboardInterrupt:
      print()
      return 1
    download_link = versions.get(chosen_key).get('download-link')
    def print_download_progress(todo, done):
      typewriter.print_progress('Downloading', todo, done)
    downloaded_bytes = cloud.download(download_link, print_download_progress)
    typewriter.clear_lines(0)
    out_file = temp_dir + '/download.zip'
    drawer.write_file(out_file, downloaded_bytes)
    def print_extract_progress(todo, done):
      typewriter.print_progress('Extracting', todo, done)
    out_dir = temp_dir + '/extracted'
    drawer.extract_archive(out_file, out_dir, print_extract_progress)
    typewriter.print_status('Installing...')
    csp = acmm.Extension.CSP(out_dir)
    manager.install(csp, acmm.InstallMethod.UPDATE)
    clean_temp_dir()
    print('Installed.')

  def uninstall_csp(self):
    'Deletes Custom Shaders Patch'
    csp = manager.fetch_extension(acmm.Extension.CSP)
    if csp is None:
      print('CSP is not installed')
      return 1
    csp.delete()

  def pure_info(self):
    'Prints information about Pure'
    pure = manager.fetch_extension(acmm.Extension.Pure)
    if pure is None:
      print('Pure is not installed.')
      return 1
    info = pure.get_ui_info()
    size = pure.get_size()
    size, units, _ = drawer.get_readable_filesize(size)
    size = round(size, 1)
    units = units.upper()
    key_to_title = {
      'version': 'Version',
      'author': 'Author',
      'description': 'Description',
    }
    indent = 2
    global_info = format_info({'size': 'Size'}, {'size': f'{size} {units}'}, indent, True)
    gamma_body = format_info(key_to_title, info.get('gamma'), indent, True)
    lcs_body = format_info(key_to_title, info.get('lcs'), indent, True)
    print('\n'.join([
      typewriter.bolden('Global:'),
      global_info, '',
      typewriter.bolden('Gamma:'),
      gamma_body, '',
      typewriter.bolden('LCS:'),
      lcs_body,
    ]))

  def uninstall_pure(self):
    'Deletes Pure'
    pure = manager.fetch_extension(acmm.Extension.Pure)
    if pure is None:
      print('Pure is not installed.')
      return 1
    pure.delete()


cli = CLI()

def main() -> int:
  captain = Captain(cli)
  function, args = captain.parse()
  return function(*args)

def run_as_subcli(args: list , program: str) -> int:
  captain = Captain(cli, program=program)
  function, args = captain.parse(args)
  return function(*args)

if __name__ == '__main__':
  sys.exit(main())
