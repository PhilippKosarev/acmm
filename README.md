# acmm
A cross-platform mod manager for Assetto Corsa written in Python.

## Using the CLI
The built-in CLI can list, install and remove mods.
```
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
```
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

Here, the `car_assets` list will hold objects of type `acmm.Asset.Car`, but you can also initialise an asset yourself:
```py
import os
cars_dir = assetto_dir / 'content' / 'cars'
car_dir = cars_dir / next(cars_dir.iterdir())
car = acmm.Asset.Car(car_dir)
```

However, if the given `car_dir` does not lead to a valid directory you will get an `acmm.InvalidAsset` exception.

If we have a valid car asset, we can access its methods:
```py
>>> car
<Car asset 'abarth500' at 0x7f111b506350>
>>> car.get_id()
'abarth500'
>>> car.get_size()
139015318
car.get_origin()
<AssetOrigin.KUNOS: 1>
>>> car.get_ui_info()
{'name': 'Abarth 500 EsseEsse', 'brand': 'Abarth', 'description': 'Turning the modern Fiat 500 into an Abarth meant lowering the ride, adding a turbocharger to the 1.4-litre engine (no mean feat under that tiny bonnet), giving it Torque Transfer Control for more aggressive cornering and improving the aerodynamics with side-skirts and spoilers.\n\n\n\t\n\tThe little Abarth is fast, very agile and plenty of fun.', 'tags': ['#small sports', 'fwd', 'manual', 'turbo', 'street', 'hot hatchback', 'italy'], 'class': 'street', 'specs': {'bhp': '160bhp', 'torque': '230Nm', 'weight': '1025kg', 'topspeed': '211km/h', 'acceleration': '7.4s 0-100', 'pwratio': '6.40kg/hp', 'range': 68}, 'torqueCurve': [['0', '0'], ['500', '130'], ['1000', '147'], ['1500', '162'], ['2000', '167'], ['2500', '179'], ['3000', '230'], ['3500', '230'], ['4000', '223'], ['4500', '221'], ['5000', '223'], ['5500', '207'], ['5750', '199'], ['6000', '189'], ['6500', '172']], 'powerCurve': [['0', '0'], ['500', '9'], ['1000', '21'], ['1500', '34'], ['2000', '47'], ['2500', '63'], ['3000', '97'], ['3500', '114'], ['4000', '125'], ['4500', '140'], ['5000', '157'], ['5500', '160'], ['5750', '161'], ['6000', '159'], ['6500', '157']]}
>>> car.get_preview_file()
# This doesn't return anything because the preview file does not exist
>>> skins = car.get_skins()
>>> skins
[<CarSkin asset '0_white_scorpion' at 0x7f111b4158b0>, <CarSkin asset 'black_red' at 0x7f111b4159a0>, <CarSkin asset 'grey_white' at 0x7f111b40c210>, <CarSkin asset 'light_blue' at 0x7f111b40c3d0>, <CarSkin asset 'light_blue_scorpion' at 0x7f111b408fc0>, <CarSkin asset 'pearl' at 0x7f111b99fd10>, <CarSkin asset 'pearl_scorpion' at 0x7f111b99fe90>, <CarSkin asset 'red_scorpion' at 0x7f111b404680>, <CarSkin asset 'red_white' at 0x7f111b404730>, <CarSkin asset 'white' at 0x7f111b36ac10>]
>>> skin = skins[0]
>>> skin
<CarSkin asset '0_white_scorpion' at 0x7f111b4158b0>
>>> skin.get_id()
'0_white_scorpion'
>>> skin.get_size()
6393091
>>> skin.get_ui_info()
{'skinname': 'White Scorpion', 'drivername': '', 'country': '', 'team': '', 'number': '0', 'priority': 10}
>>> skin.get_preview_file()
PosixPath('/home/philipp/.local/share/Steam/steamapps/common/assettocorsa/content/cars/abarth500/skins/0_white_scorpion/preview.jpg')
>>> skin.get_livery_file()
PosixPath('/home/philipp/.local/share/Steam/steamapps/common/assettocorsa/content/cars/abarth500/skins/0_white_scorpion/livery.png')
```

For more examples on how to use acmm you can take a look at the code of the built-in CLI.