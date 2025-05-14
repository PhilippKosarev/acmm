# Imports
import os, shutil, tomllib, send2trash, zipfile, patoolib
from .typewriter import Typewriter
from .clipboard import Clipboard
typewriter = Typewriter()
clipboard = Clipboard()

# Processes given input arguments
class Captain:
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
    commands_string = typewriter.list_to_columns(commands_list, 2, offset)
    options_list = []
    for option in options:
      option_desc = options.get(option).get('description')
      long = ', --'.join(options.get(option).get('long'))
      short = ', -'.join(options.get(option).get('short'))
      options_list.append(f"-{short}, --{long}")
      options_list.append(f"- {option_desc}")
    options_string = typewriter.list_to_columns(options_list, 2, offset)
    self.help = f'''{typewriter.bolden('Description:')}
{offset_string}{description}
{typewriter.bolden('Synopsis:')}
{offset_string}{self.app} [OPTIONS] [COMMAND]
{typewriter.bolden('Commands:')}
{commands_string.rstrip()}
{typewriter.bolden('Options:')}
{options_string.rstrip()}'''

  # Returns the stored `help` string
  def get_help(self):
    return self.help

  # Sets the `help` string
  def set_help(self, help: str):
    self.help = help

  # Prints the `help` string
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
      if argument.startswith("-"):
        self.arg_found = False
        # Long options
        if argument.startswith("--"):
          argument = argument.removeprefix("--")
          for option in self.options:
            strings = self.options.get(option).get('long')
            if clipboard.is_string_in_list(strings, argument):
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
            command_found = False
            for option in self.options:
              strings = self.options.get(option).get('short')
              if clipboard.is_string_in_list(strings, argument):
                option_dict = self.options.get(option).get('option')
                option_value = self.option_values[option_dict] = True
                command_found = True
          if command_found is False:
            print(f"Option '{argument}' unrecognized. Try {self.app} help")
            exit()
      # Commands
      else:
        if self.command is None:
          for command in self.commands:
            if command == argument:
              self.command = command
              self.requires_args = self.commands.get(command).get('requires_args')
            elif argument == "help":
              self.print_help()
              exit()
          if self.command is None:
            print(f"Command '{argument}' unrecognized. Try {self.app} help")
            exit()
        else:
          if self.requires_args is True:
            if self.command_args == "":
              self.command_args = argument
            else:
              print(f"Command '{self.command}' only takes one argument.")
              exit()
          else:
            print(f"Command '{self.command}' does not take arguments.")
            exit()
    if self.requires_args is True and self.command_args == "":
      print(f"Command '{self.command}' requires an argument.")
      exit()
    # Checking if command is specified
    if self.command is None:
        print(f"No command specified. Try {self.app} help")
        exit()


  # Returns the `option_values` dict
  def get_option_values(self):
    return self.option_values


  # Returns the `function` string
  def get_function(self):
    function = self.commands.get(self.command).get('function')
    if self.command_args != "":
      function = f"{function}('{self.command_args}')"
    else:
      function = f"{function}()"
    return function
