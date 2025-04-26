#!/bin/python3

# Imports
import os, shutil, tomllib, send2trash, zipfile, patoolib

# Helper functions
def string_in_list(input_string: str, input_list: list):
  present = False
  for item in input_list:
    if item == input_string:
      present = True
  return present

# Processes the given input arguments
class InputInterpreter:
  def __init__(self, app, description, commands, options):
    # Class vars
    self.app = app
    self.commands = commands
    self.options = options
    # Auto generating a help page
    offset = 2; offset_string = "".ljust(offset)
    commands_list = []
    for command in commands:
      command_desc = commands.get(command).get('description')
      commands_list.append(f"{command}")
      commands_list.append(f"- {command_desc}")
    commands_list.append("help")
    commands_list.append("- Prints this page")
    commands_string = Typewriter().list_to_columns(commands_list, 2, offset)
    options_list = []
    for option in options:
      option_desc = options.get(option).get('description')
      long = ', --'.join(options.get(option).get('long'))
      short = ', -'.join(options.get(option).get('short'))
      options_list.append(f"-{short}, --{long}")
      options_list.append(f"- {option_desc}")
    options_string = Typewriter().list_to_columns(options_list, 2, offset)
    self.help = f'''{Typewriter().bolden('Description:')}
{offset_string}{description}
{Typewriter().bolden('Synopsis:')}
{offset_string}{self.app} [OPTIONS] [COMMAND]
{Typewriter().bolden('Commands:')}
{commands_string.rstrip()}
{Typewriter().bolden('Options:')}
{options_string.rstrip()}'''
  def get_help(self):
    return self.help
  def set_help(self, help: str):
    self.help = help
  def print_help(self):
    print(self.help)

  # Interpreting input arguments
  def interpret(self, arguments):
    # Class vars
    self.command = None
    self.function = None
    self.requires_args = False
    self.command_args = ""
    # Creating option bools
    self.option_values = {}
    for option in self.options:
      name = self.options.get(option).get('option')
      self.option_values[name] = False
    # Parsing arguments
    for argument in arguments:
      # Long options
      if argument.startswith("-"):
        self.arg_found = False
        if argument.startswith("--"):
          argument = argument.removeprefix("--")
          for option in self.options:
            strings = self.options.get(option).get('long')
            if string_in_list(argument, strings) is True:
              option_dict = self.options.get(option).get('option')
              option_value = self.option_values[option_dict] = True
              self.arg_found = True
          if self.arg_found is False:
            print(f"Option '{argument}' unrecognized. Try {self.app} help")
            exit()
        # Short options
        else:
          argument = argument.removeprefix("-")
          arguments = list(argument)
          for argument in arguments:
            for option in self.options:
              strings = self.options.get(option).get('short')
              for string in strings:
                if argument == string:
                  option_dict = self.options.get(option).get('option')
                  option_value = self.option_values[option_dict] = True
                  self.command_found = True
          if self.command_found is False:
            print(f"Option '{argument}' unrecognized. Try {self.app} help")
            exit()
      # Commands
      else:
        if self.command is None:
          for command in self.commands:
            if command == argument:
              self.command = command
            elif argument == "help":
              self.print_help()
              exit()
          if self.command is None:
            print(f"Command '{argument}' unrecognized. Try {self.app} help")
            exit()
        else:
          self.requires_args = self.commands.get(command).get('requires_args')
          if self.requires_args is True:
            if self.command_args == "":
              self.command_args = argument
            else:
              print(f"Command '{self.command}' only takes one argument.")
              exit()
          elif self.requires_args is True and self.command_args == "":
            print(f"Command '{self.command}' requires an argument.")
            exit()
          else:
            print(f"Command '{self.command}' does not take arguments.")
            exit()
    # Checking if command is specified
    if self.command is None:
        print(f"No command specified. Try {self.app} help")
        exit()

  def get_option_values(self):
    return self.option_values

  def get_function(self):
    function = self.commands.get(self.command).get('function')
    if self.command_args != "":
      function = f"{function}('{self.command_args}')"
    else:
      function = f"{function}()"
    return function

# Prints stuff in a fancy way
class Typewriter:
  def __init__(self):
    self.BOLD = '\033[1m'
    self.NORMAL = '\033[0m'
    self.CLEAR = '\x1b[2K'
    self.CURSOR_UP = '\033[1A'
  def bolden(self, text: str):
    text = f'{self.BOLD}{text}{self.NORMAL}'
    return text
  def clear_lines(self, lines: int):
    if lines == 0:
      print("\r" + self.CLEAR, end='')
      return
    for line in range(lines):
      print(self.CURSOR_UP + self.CLEAR, end='')
  def print(self, text: str):
    self.clear_lines(0)
    print(text)
  def print_status(self, status: str):
    self.clear_lines(0)
    print(f" {status}", end='\r')
  # Prints a list in columns
  def list_to_columns(self, text_list: list, columns: int, offset: int):
    column_width = len(max(text_list, key=len))
    # Automatically set num of columns if not specified otherwise
    if columns is None:
      terminal_width = shutil.get_terminal_size()[0]
      columns = int(terminal_width / (column_width + offset))
    output = ""
    # Ol' reliable
    counter = 1
    for item in text_list:
      spaces = column_width - len(item)
      end = "".ljust(spaces)
      offset_string = "".ljust(offset)
      if counter % columns == 0 or counter == len(text_list):
        end = "\n"
      output += f"{offset_string}{item}{end}"
      counter += 1
    return output

  # Removes entries from input_list that are in filter_list 
  def filter_list(self, input_list: list, filter_list: list):
    result_list = []
    for item in input_list:
      if string_in_list(item, filter_list) is False:
        result_list.append(item)
    return result_list

  # Returns entries from input_list that are also in match_list
  def match_list(self, input_list: list, match_list: list):
    result_list = self.filter_list(input_list, match_list)
    result_list = self.filter_list(input_list, result_list)
    return result_list

  # Searches for string in list
  def search_in_list(self, input_string: str, input_list: list):
    result_list = []
    for item in input_list:
      if input_string.lower() in item.lower():
        result_list.append(item)
    return result_list


# Deals with files
class Drawer:
  # Filetype checks
  def is_folder(self, path: str):
    return os.path.isdir(path)
  def is_file(self, path: str):
    return os.path.isfile(path)
  def get_filetype(self, path: str):
    if self.is_folder(path):
      return "folder"
    elif self.is_file(path) is False:
      return None
    file = self.basename(path)
    filetype = os.path.splitext(file)[1]
    filetype = filetype.removeprefix('.')
    return filetype

  # Getting files/directories
  def get_all(self, directory: str):
    relative_files = os.listdir(directory)
    absolute_files = []
    for file in relative_files:
      absolute_files.append(f"{directory}/{file}")
    return absolute_files
  def get_files(self, directory: str):
    unfiltered_files = self.get_all(directory)
    files = []
    for file in unfiltered_files:
      if self.is_file:
        files.append(file)
    return files
  def get_files_recursive(self, folder: str):
    files = []
    for folder in os.walk(folder, topdown=True):
      for file in folder[2]:
        files.append(f"{folder[0]}/{file}")
    return files
  def get_folders(self, directory: str):
    folders = []
    for item in self.get_all(directory):
      if self.is_folder(item):
        folders.append(item)
    return folders
  def get_folders_recursive(self, folder: str):
    folders = []
    for folder in os.walk(folder, topdown=True):
      for item in folder[1]:
        folders.append(f"{folder[0]}/{item}")
    return folders
  def search_for_filetype(self, search_term: str, folder: str):
    search_term.removeprefix('.')
    matching_files = []
    files = self.get_files_recursive(folder)
    for file in files:
      filetype = self.get_filetype(file)
      if filetype == search_term:
        matching_files.append(file)
    return matching_files

  # Making files/directories
  def make_folder(self, path):
    os.makedirs(path)
  def make_file(self, path):
    new = open(file)
    new.close()
  def copy_file(self, source: str or list, destination: str):
    if type(source) == str:
      shutil.copy(source, destination)
    elif type(source) == list:
      for file in source:
        shutil.copy(file, destination)
  def copy_folder(self, source: str, destination: str):
    shutil.copytree(source, destination)

  # Trashing files/directories
  def trash_file(self, file: str or list):
    if type(file) == str:
      if self.is_file(file):
        send2trash.send2trash(file)
    elif type(file) == list:
      for item in file:
        if self.is_file(file):
          send2trash.send2trash(item)
  # Deleting files/directories
  def delete_file(self, file: str or list):
    if type(file) == str:
      if self.is_file(file):
        os.remove(file)
    elif type(file) == list:
      for item in file:
        if self.is_file(file):
          os.remove(item)
  def trash_folder(self, folder: str or list):
    if type(folder) == str:
      if self.is_folder(folder):
        send2trash.send2trash(folder)
    elif type(folder) == list:
      for item in folder:
        if self.is_folder(item):
          send2trash.send2trash(item)
  def delete_folder(self, folder: str or list):
    if type(folder) == str:
      if self.is_folder(folder):
        shutil.rmtree(folder)
    elif type(folder) == list:
      for item in folder:
        if self.is_folder(item):
          shutil.rmtree(item)

  # Getting parts of file or path
  def get_parent(self, path: str or list):
    if type(path) == str:
      file = self.basename(path)
      parent = path.removesuffix(file)
      return parent
    elif type(path) == list:
      result_list = []
      for file in path:
        basename = self.basename(file)
        parent = file.removesuffix(basename)
        parent = parent.removesuffix('/')
        result_list.append(parent)
      return result_list
  def get_depth(self, path: str):
    depth = path.split(sep='/')
    depth = len(depth)
    return depth
      
  def basename(self, path: str or list):
    if type(path) == str:
      if self.is_file(path):
        path = os.path.basename(path)
      elif self.is_folder(path):
        path = os.path.basename(os.path.normpath(path))
      return path
    elif type(path) == list:
      return_list = []
      for file in path:
        if self.is_file(file):
          file = os.path.basename(file)
        elif self.is_folder(file):
          file = os.path.basename(os.path.normpath(file))
        return_list.append(file)
      return return_list
  def filter_by_basename(self, files: list, filters: list):
    result_list = []
    counter = 0
    for file in files:
      basename = self.basename(file)
      if not string_in_list(basename, filters):
        result_list.append(file)
    return result_list
  # Searches for string in list of basenames
  def search_for_files(self, search_term: str, folder: list):
    result_list = []
    files = self.get_files_recursive(folder)
    for file in files:
      basename = self.basename(file)
      if search_term.lower() in basename.lower():
        result_list.append(file)
    return result_list
  def search_for_folder(self, search_term: str, folder: str or list):
    result_list = []
    if type(folder) == str:
      subfolders = self.get_folders(folder)
      for item in subfolders:
        basename = self.basename(item)
        if basename == search_term:
          result_list.append(item)
    elif type(folder) == list:
      for subfolder in folder:
        subfolders = self.get_folders(subfolder)
        for item in subfolders:
          basename = self.basename(item)
          if basename == search_term:
            result_list.append(item)
    return result_list
  def search_for_folders(self, search_term: str, folder: str or list):
    result_list = []
    def search(search_term: str, folder: str):
      folders = self.get_folders_recursive(folder)
      for folder in folders:
        basename = self.basename(folder)
        if search_term.lower() in basename.lower():
          result_list.append(folder)
    if type(folder) == str:
      search(search_term, folder)
    elif type(folder) == list:
      for subfolder in folder:
        search(search_term, subfolder)
    return result_list
  # Finds a folder with specified files
  def find_folders_with_files(self, folder: str, required_files: list):
    matches = []
    for req in required_files:
      matched_files = self.get_parent(self.search(req, folder))
      matched_files = Clipboard().deduplicate(matched_files)
      if matched_files != []:
        matches += matched_files
    return matches
  
  # Extracting archives
  archive_types = ['zip', 'rar', '7z']
  def is_archive(self, path: str):
    filetype = self.get_filetype(path)
    if string_in_list(filetype, self.archive_types):
      return True
    else:
      return False
  def extract_archive(self, archive: str, extract_location: str):
    archive_type = self.get_filetype(archive)
    archive_basename = self.basename(archive).removesuffix(f".{archive_type}")
    extract_location = f"{extract_location}/{archive_basename}"
    if archive_type == 'zip':
      with zipfile.ZipFile(archive, 'r') as file:
        file.extractall(extract_location)
      return extract_location
    elif archive_type == 'rar':
      try:
        patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
        return extract_location
      except patoolib.util.PatoolError:
        print("Please install the 'unrar' package to process RAR archives.")
        return None
    elif archive_type == '7z':
      try:
        patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
        return extract_location
      except patoolib.util.PatoolError:
        print("Please install the 'p7zip' package to process 7zip archives.")
        return None
    else:
      return None
      

# Deals with stuffs
class Clipboard:
  def deduplicate(self, input_list: list):
    result_list = list(set(input_list))
    result_list.sort()
    return result_list
  def match_string(self, input_list: list, search_term: str):
    matching = []
    for item in input_list:
      if item == search_term:
        matching.append(item)
    return matching
  def match_list(self, input_list1: list, input_list2: list):
    matching = []
    for item in input_list1:
      match = self.match_string(input_list2, item)
      if match != []:
        matching.append(item)
    return matching
  def match_substring(self, input_list: list, substring: str):
    matching = []
    for item in input_list:
      if substring in item:
        matching.append(item)
    return matching
  def match_prefix(self, input_list: list, input_prefix: str):
    result_list = []
    for item in input_list:
      item_prefix = item.removeprefix(input_prefix)
      if item != item_prefix:
        result_list.append(item)
    return result_list
  def match_suffix(self, input_list: list, input_suffix: str):
    result_list = []
    for item in input_list:
      item_suffix = item.removesuffix(input_suffix)
      if item != item_suffix:
        result_list.append(item)
    return result_list


# Deals with configs
class Notebook:
  def check_config(self, config_file: str):
    print("fr")
  # parsing a toml config
  def read_toml(self, config_file: str):
    # Parsing config
    with open(config_file, "rb") as file:
      data = tomllib.load(file)
      return data


# Asks user for inputs
class Flashcard:
  def yn_prompt(self, question: str):
    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']
    while True:
      try:
        user_input = input(f'{question} {Typewriter().bolden("[y/n]")}: ')
        answer = None
        if user_input.lower() in yes_choices:
          return True
        elif user_input.lower() in no_choices:
          return False
      except KeyboardInterrupt:
        print()
        exit()
