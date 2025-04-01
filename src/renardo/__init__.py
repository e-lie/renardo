from renardo.settings_manager import settings_manager
from renardo.lib import *
from renardo.RenardoApp import RenardoApp

def main() -> None:
   RenardoApp()

RenardoApp()

# from .RenardoApp import RenardoApp

# main is to call the module with python -m but we want to make a pypi package application with entry_point
# More here : https://setuptools.pypa.io/en/latest/userguide/entry_point.html # we don't use setuptools anymore but hatch

# RenardoApp()
