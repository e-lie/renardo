from renardo.settings_manager import settings
from renardo.RenardoApp import RenardoApp

from renardo.webserver import run_webserver

def main() -> None:
   RenardoApp()

# main is to call the module with python -m but we want to make a pypi package application with entry_point
# More here : https://setuptools.pypa.io/en/latest/userguide/entry_point.html # we don't use setuptools anymore but hatch

