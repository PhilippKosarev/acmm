# Imports
import os, sys, shutil, send2trash, platform, tempfile, pathlib
import zipfile, patoolib, rarfile
from .typewriter import Typewriter
from .clipboard import Clipboard
typewriter = Typewriter()
clipboard = Clipboard()

# Internal functions
joinpath = os.path.join
def realpath(path: str or list):
  if type(path) == str:
    return os.path.normpath(path)
  elif type(path) == list:
    result_list = []
    for item in path:
      result_list.append(os.path.normpath(item))
    return result_list

def outpath(path: str or list):
  if type(path) == str:
    return path.replace(os.sep, '/')
  elif type(path) == list:
    result_list = []
    for item in path:
      result_list.append(item.replace(os.sep, '/'))
    return result_list


# Deals with files
class Drawer:

  # Returns True if give a path to folder
  def is_folder(self, path: str):
    path = realpath(path)
    return os.path.isdir(path)

  # Returns True if give a path to file
  def is_file(self, path: str):
    path = realpath(path)
    return os.path.isfile(path)

  def exists(self, path: str):
    path = realpath(path)
    is_file = self.is_folder(path)
    is_folder = self.is_file(path)
    if is_file or is_folder:
      return True
    else:
      return False


  # Returns the extension of a given file (a string)
  def get_filetype(self, path: str):
    path = realpath(path)
    if self.is_folder(path):
      return "folder"
    elif self.is_file(path) is False:
      return None
    basename = self.basename(path)
    filetype = os.path.splitext(basename)[1].removeprefix('.')
    return filetype

  # Returns a list of files and folders in a given folder
  def get_all(self, path: str):
    path = realpath(path)
    relative_files = os.listdir(path)
    absolute_files = []
    for file in relative_files:
      file = joinpath(path, file)
      absolute_files.append(file)
    return outpath(absolute_files)

  # Returns a list of files in a given folder
  def get_files(self, path: str):
    path = realpath(path)
    unfiltered_files = self.get_all(path)
    files = []
    for file in unfiltered_files:
      if self.is_file:
        files.append(file)
    return outpath(files)

  # Returns a list of folders in a given folder
  def get_folders(self, path: str):
    path = realpath(path)
    folders = []
    for item in self.get_all(path):
      if self.is_folder(item):
        folders.append(item)
    return outpath(folders)

  # Returns a list of all files in a given folder
  def get_files_recursive(self, path: str):
    path = realpath(path)
    files = []
    for folder in os.walk(path, topdown=True):
      for file in folder[2]:
        file = joinpath(folder[0], file)
        files.append(file)
    return outpath(files)

  # Returns a list of all folders in a given folder
  def get_folders_recursive(self, path: str):
    path = realpath(path)
    folders = []
    for folder in os.walk(path, topdown=True):
      for item in folder[1]:
        item = joinpath(folder[0], item)
        folders.append(item)
    return outpath(folders)


  # Creates a new folder
  def make_folder(self, path):
    path = realpath(path)
    path = os.mkdir(path)
    return outpath(path)

  # Creates a new file
  def make_file(self, path):
    path = realpath(path)
    new = open(path, 'w')
    new.close()
    return outpath(path)


  # Copies given file(s)/folder(s)
  def copy(self, source: str, destination: str, overwrite=False):
    source = realpath(source)
    destination = realpath(destination)
    if self.is_file(source):
      shutil.copy(source, destination)
    elif self.is_folder(source):
      shutil.copytree(source, destination, dirs_exist_ok=overwrite)
    return outpath(destination)


  # Sends given file(s)/folder(s) to trash
  def trash(self, path: str or list):
    path = realpath(path)
    if type(path) == str:
      try:
        send2trash.send2trash(path)
      except FileNotFoundError:
        print(f"File '{path}' wasn't found, skipping sending it to trash.")
    elif type(path) == list:
      for item in path:
        try:
          send2trash.send2trash(item)
        except FileNotFoundError:
          print(f"File '{path}' wasn't found, skipping sending it to trash.")
    else:
      return None
    return outpath(path)


  # Deletes a given file (using trash_file() instead is recommended)
  def delete_file(self, path: str or list):
    path = realpath(path)
    if type(path) == str:
      if self.is_file(path):
        os.remove(path)
    elif type(path) == list:
      for item in path:
        if self.is_file(path):
          os.remove(item)
    return outpath(path)

  # Deletes a given folder (using trash() instead is recommended)
  def delete_folder(self, path: str):
    path = realpath(path)
    try:
      if self.is_folder(path):
        shutil.rmtree(path)
      else:
        return None
    except KeyboardInterrupt:
      typewriter.print("Folder deletion cancelled.")
      shutil.rmtree(path)
      sys.exit(-1)
    except PermissionError:
      typewriter.print(f"Failed to delete folder '{path}', due to insufficient permissions.")
      sys.exit(1)
    return outpath(path)

  # Returns the parent folder of given file/folder
  def get_parent(self, path: str or list):
    path = realpath(path)
    if type(path) == str:
      basename = self.basename(path)
      parent = path.removesuffix(basename)
      parent = parent.removesuffix(os.sep)
      return outpath(parent)
    elif type(path) == list:
      result_list = []
      for file in path:
        basename = self.basename(file)
        parent = file.removesuffix(basename)
        parent = parent.removesuffix(os.sep)
        result_list.append(parent)
      return outpath(result_list)

  # Returns depth of given file/folder
  def get_depth(self, path: str):
    path = realpath(path)
    depth = path.split(sep=os.sep)
    depth = len(depth)
    return depth

  def basename(self, path: str or list):
    path = realpath(path)
    if type(path) == str:
      if self.is_folder(path):
        path = os.path.basename(os.path.normpath(path))
      else:
        path = path.rsplit(os.sep,1)[-1]
      return outpath(path)
    elif type(path) == list:
      return_list = []
      for file in path:
        if self.is_file(file):
          file = os.path.basename(file)
        elif self.is_folder(file):
          file = os.path.basename(os.path.normpath(file))
        return_list.append(file)
      return outpath(return_list)

  # Searches for string in list of basenames
  def search_for_files(self, search_term: str, path: list):
    path = realpath(path)
    result_list = []
    files = self.get_files_recursive(path)
    for file in files:
      basename = self.basename(file)
      if search_term.lower() in basename.lower():
        result_list.append(file)
    return outpath(result_list)

  def search_for_folder(self, search_term: str, path: str or list):
    path = realpath(path)
    result_list = []
    if type(path) == str:
      subfolders = self.get_folders(path)
      for item in subfolders:
        basename = self.basename(item)
        if basename == search_term:
          result_list.append(item)
    elif type(path) == list:
      for subfolder in path:
        subfolders = self.get_folders(subfolder)
        for item in subfolders:
          basename = self.basename(item)
          if basename == search_term:
            result_list.append(item)
    return outpath(result_list)

  def search_for_folders(self, search_term: str, path: str or list):
    path = realpath(path)
    result_list = []
    def search(search_term: str, path: str):
      folders = self.get_folders_recursive(path)
      for folder in folders:
        basename = self.basename(folder)
        if search_term.lower() in basename.lower():
          result_list.append(folder)
    if type(path) == str:
      search(search_term, path)
    elif type(path) == list:
      for subfolder in path:
        search(search_term, subfolder)
    return outpath(result_list)

  # Finds a folder with specified files
  def find_folders_with_files(self, path: str, required_files: list):
    path = realpath(path)
    matches = []
    for req in required_files:
      matched_files = self.get_parent(self.search(req, path))
      matched_files = Clipboard().deduplicate(matched_files)
      if matched_files != []:
        matches += matched_files
    return outpath(matches)

  # Checks if a given file is an archive
  archive_types = ['zip', 'rar', '7z']
  def is_archive(self, path: str):
    path = realpath(path)
    filetype = self.get_filetype(path)
    if clipboard.is_string_in_list(self.archive_types, filetype):
      return True
    else:
      return False

  # Extracts a given archive
  def extract_archive(self, archive: str, extract_location: str, progress_function=None):
    archive = realpath(archive)
    extract_location = realpath(extract_location)
    archive_type = self.get_filetype(archive)
    archive_basename = self.basename(archive).removesuffix(f".{archive_type}")
    extract_location = joinpath(extract_location, archive_basename)
    try:
      if archive_type == 'zip': archive_function = zipfile.ZipFile
      elif archive_type == 'rar': archive_function = rarfile.RarFile
      elif archive_type == '7z':
        try:
          patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
          return extract_location
        except PatoolError:
          print("Please install the 'p7zip' package to process 7zip archives.")
          return None
      else:
        return None
      if archive_type == 'zip' or archive_type == 'rar':
        archive_obj = archive_function(archive)
        archived_files = archive_obj.namelist()
        to_extract = len(archived_files)
        extracted = 0
        for archived_file in archived_files:
          archive_obj.extract(archived_file, path=extract_location)
          extracted += 1
          if progress_function is not None:
            progress_function(extracted, to_extract)
    except KeyboardInterrupt:
      typewriter.print("Archive extraction cancelled.")
      self.delete_folder(extract_location)
      exit()
    return outpath(extract_location)

  # Returns the home folder
  def get_home(self):
    home = str(pathlib.Path.home())
    return outpath(home)

  # Returns the temporary folder
  def get_temp(self):
    temp = str(tempfile.gettempdir())
    return outpath(temp)

  def get_file_size(self, path: str):
    try:
      size = 0
      if self.is_file(path):
        size += os.path.getsize(path)
      elif self.is_folder(path):
        subfiles = self.get_files_recursive(path)
        for subfile in subfiles:
          size += os.path.getsize(subfile)
      return size
    except KeyboardInterrupt:
      typewriter.print('Program aborted while gathering size of files.')
      sys.exit(1)
