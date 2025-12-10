#! /usr/bin/env python3

# Imports
from libjam import Captain, drawer, typewriter, cloud
import sys, os, time, math

# Internal imports
import acmm
from .shared import manager, temp_dir, clean_temp_dir

# Helper functions
def get_csp() -> acmm.Extension.CSP:
  return manager.fetch_extension(acmm.Extension.CSP)

# The csp subcli for acmm.
class CLI:
  'Manages your CSP installation'
  def info(self):
    'Prints information about CSP'
    csp = get_csp()
    if csp is None:
      print('CSP is not installed.')
      return 1
    info = csp.get_ui_info()
    size, units, _ = csp.get_size(human_readable=True)
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
    items = {}
    for key in key_to_title:
      value = info.get(key).strip()
      title = key_to_title.get(key)
      items[title] = value
    longest_title = len(sorted(items.keys(), key=len, reverse=True)[0])
    lines = []
    for title, value in items.items():
      title = f'{title:>{longest_title}}'
      title = typewriter.bolden(title + ':')
      lines.append(f'{title} {value}')
    print('\n'.join(lines))

  def install(self):
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

  def uninstall(self):
    'Deletes Custom Shaders Patch'
    csp = get_csp()
    if csp is None:
      print('CSP is not installed')
      return 1
    csp.trash()


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
