# Imports
from libjam import drawer, typewriter
import sys

# Backend
import acmm

# Configuration
from .config import assetto_dir

# Variables
manager = acmm.Manager(assetto_dir)
temp_dir = drawer.get_temp() + '/acmm'

# Functions
def clean_temp_dir():
  typewriter.print_status('Cleaning temp dir...')
  if drawer.exists(temp_dir):
    try:
      drawer.delete_folder(temp_dir)
    except PermissionError as e:
      print(f"Error deleting temp dir: permission denied. Please correct permissions for '{temp_dir}'.")
      sys.exit(1)
  drawer.make_folder(temp_dir)
  typewriter.clear_lines(0)
