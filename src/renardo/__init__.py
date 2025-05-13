

def main() -> None:
   """Entry point for the Renardo application"""
   from renardo.settings_manager import settings
   from renardo.renardo_app.renardo_app import RenardoApp
   app = RenardoApp.get_instance()
   app.launch()

# main is to call the module with python -m but we want to make a pypi package application with entry_point
# More here : https://setuptools.pypa.io/en/latest/userguide/entry_point.html # we don't use setuptools anymore but hatch