# acmm
A cross-platform mod manager for Assetto Corsa written in Python.

## Using the CLI
The built-in CLI can list, install and remove mods.
```sh
$ acmm --help
A CLI mod manager for Assetto Corsa.

Synopsis:
  acmm [OPTION]... COMMAND [ARGS]...

Commands:
  list      - List installed mods.
  install   - Install the specified mod(s).
  remove    - Remove specified mod(s).
  extension - Manage your extensions.

Usage:
  acmm install <PATH> [ADDITIONAL PATHS]...
  acmm remove [MOD ID]...
  acmm extension [ARGS]...

Options:
  -c, --car      - Only list/remove car mods.
  -t, --track    - Only list/remove track mods.
  -w, --weather  - Only list/remove weather mods.
  -a, --app      - Only list/remove app mods.
  -p, --ppfilter - Only list/remove ppfilter mods.
  -A, --all      - Do not filter out Kunos assets.
  -k, --kunos    - Filter out non Kunos assets.
  -s, --size     - Show mod size on disk.
  -h, --help     - Prints this page.
```

You can also manage your extensions (CSP, Pure and SOL) through the `extension` subcli.
```sh
$ acmm extension --help
Manage your Assetto Corsa extensions.

Synopsis:
  acmm-extension [OPTION]... COMMAND [ARGS]...

Commands:
  show-csp       - Print information about CSP.
  install-csp    - Download and install CSP.
  uninstall-csp  - Delete Custom Shaders Patch.
  show-pure      - Print information about Pure.
  uninstall-pure - Delete Pure.
  show-sol       - Print information about SOL.
  uninstall-sol  - Delete SOL.

Options:
  -h, --help - Prints this page.
```

## Installing
You can run this command to install the latest bleeding edge version. There is no stable version yet, but I try to keep the main branch in working order.
```sh
pip install git+https://github.com/PhilippKosarev/acmm.git
```

## Using the library
The `acmm` library provides a few crucial classes for you to work with, but it all starts with the manager. The acmm manager is used to fetch, find and install assets and extensions. It takes a single parameter `assetto_dir`, which can be a string, Path or other path-like object. Here is an example:
```py
from pathlib import Path
import acmm
assetto_dir = Path.home() / '.local' / 'share' / 'Steam' / 'steamapps' / 'common' / 'assettocorsa'
manager = acmm.Manager(assetto_dir)
```

Then, using the manager, we can, for example, fetch either all of the installed assets, or just one type of asset:
```py
all_assets = manager.fetch_assets()
car_assets = manager.fetch_assets(acmm.Asset.Car)
```

Here, the `car_assets` list will hold objects of type `acmm.Asset.Car`, but you can also initialise an asset yourself.
```py
cars_dir = assetto_dir / 'content' / 'cars'
car_dir = cars_dir / os.listdir(assetto_dir)[1]
car = acmm.Asset.Car(car_dir)
```

However, if the given `car_dir` does not lead to a valid directory you will get an `acmm.InvalidAsset` exception.

For more examples on how to use acmm you can take a look at the code of the built-in CLI.