# Imports
from libjam import drawer, typewriter
from pathlib import Path
import sys, tempfile

# Backend
import acmm

# Configuration
from .config import assetto_dir

# Variables
manager = acmm.Manager(assetto_dir)
def get_temp_dir() -> Path:
  temp_dir = tempfile.TemporaryDirectory(prefix='acmm-')
  return Path(temp_dir.name)
