# Deals with lists and such
class Clipboard:

  # Checks if there is a string in a list
  def is_string_in_list(self, input_list: list, input_string: str):
    for item in input_list:
      if item == input_string:
        return True
    return False


  # Returns items present in both given lists
  def get_duplicates(self, input_list1, input_list2):
    result_list = []
    for item in input_list1:
      if self.is_string_in_list(input_list2, item):
        result_list.append(item)
    result_list = self.deduplicate(result_list)
    return result_list

  # Removes duplicates from a given list
  def deduplicate(self, input_list: list):
    result_list = list(set(input_list))
    result_list.sort()
    return result_list


  # Returns input_list without any items from filter_list
  def filter(self, input_list, filter_list):
    result_list = []
    for item in input_list:
      if self.is_string_in_list(filter_list, item) is False:
        result_list.append(item)
    return result_list


  # Returns a list of strings which contain substring
  def match_substring(self, input_list: list, substring: str):
    matching = []
    for item in input_list:
      if substring in item:
        matching.append(item)
    return matching


  # Returns a list of strings which start with input_prefix
  def match_prefix(self, input_list: list, input_prefix: str):
    result_list = []
    for item in input_list:
      if item.startswith(input_prefix):
        result_list.append(item)
    return result_list

  def remove_prefix(self, input_list: list, input_prefix: str):
    result_list = []
    for item in input_list:
      result_list.append(item.removeprefix(input_prefix))
    return result_list

  # Returns a list of strings which ends with input_suffix
  def match_suffix(self, input_list: list, input_suffix: str):
    result_list = []
    for item in input_list:
      if item.endswith(input_suffix):
        result_list.append(item)
    return result_list

  # Returns a list of strings which ends with input_suffix
  def match_suffixes(self, input_list: list, input_suffixes: list):
    result_list = []
    for suffix in input_suffixes:
      result_list += self.match_suffix(input_list, suffix)
    return result_list


  # Returns a list with lower-case strings
  def lower(self, input_list: list):
    result_list = []
    for item in input_list:
      result_list.append(item.lower())
    return result_list

  # Returns a list with upper-case strings
  def upper(self, input_list: list):
    result_list = []
    for item in input_list:
      result_list.append(item.upper())
    return result_list


  # Returns a list of strings containing given string, ignores case
  def search(self, input_list: list, search_term: str):
    result_list = []
    search_term = search_term.lower()
    for item in input_list:
      if search_term in item.lower():
        result_list.append(item)
    return result_list

  # Find & Replace for a list
  def replace(self, input_list:list , oldstring: str, newstring: str):
    result_list = []
    for item in input_list:
      item = item.replace(oldstring, newstring)
      result_list.append(item)
    return result_list
