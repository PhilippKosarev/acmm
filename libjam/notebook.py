# Imports
import os, tomllib
from .drawer import Drawer

# Jam classes
drawer = Drawer()

# Pre-requisites
script_folder = os.path.dirname(os.path.realpath(__file__))
script_folder = drawer.get_parent(script_folder)
config_template_file = f"{script_folder}/config.toml.in"
config_template = open(config_template_file, 'r').read()

# Deals with configs and reading/writing files
class Notebook:

  # Checking if config exists, and creating one if it does not
  def check_config(self, config_file: str):
    config_folder = drawer.get_parent(config_file)
    if drawer.is_folder(config_folder) is False:
      drawer.make_folder(config_folder)
    if drawer.is_file(config_file) is False:
      drawer.make_file(config_file)
      with open(config_file, 'w') as config:
        config.write(config_template)
      print(f"Created configuration file in '{config_folder}'.")
    return config_file

  # parsing a toml config
  def read_toml(self, config_file: str):
    os.path.normpath(config_file)
    # Parsing config
    data = open(config_file, 'r').read()
    try:
      data = tomllib.loads(data)
      for category in data:
        for item in data.get(category):
          path = data.get(category).get(item)
          if type(path) == str:
            data[category][item] = path.replace(os.sep, '/')
      return data
    except:
      print(f"Encountered error reading '{config_file}'")
      print(f"Contents of '{config_file}':")
      print(data)
      return None
