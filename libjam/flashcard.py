# Asks user for input
class Flashcard:
  def yn_prompt(self, question: str):
    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']
    while True:
      try:
        user_input = input(f'{question} [y/n]: ')
        answer = None
        if user_input.lower() in yes_choices:
          return True
        elif user_input.lower() in no_choices:
          return False
      except KeyboardInterrupt:
        print()
        exit()
