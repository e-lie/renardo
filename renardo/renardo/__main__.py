import argparse
from renardo import launch




# TODO remove this main ? 
# main is to call the module with python -m but we want to make a pypi package application with entry_point
# More here : https://setuptools.pypa.io/en/latest/userguide/entry_point.html



parser = argparse.ArgumentParser(
    prog="renardo", 
    description="Live coding with Python and SuperCollider", 
    epilog="More information: https://renardo.org/")

parser.add_argument('-p', '--pipe', action='store_true', help="run FoxDot from the command line interface")
parser.add_argument('-d', '--dir', action='store', help="use an alternate directory for looking up samples")
parser.add_argument('-s', '--startup', action='store', help="use an alternate startup file")
parser.add_argument('-n', '--no-startup', action='store_true', help="does not load startup.py on boot")
parser.add_argument('-b', '--boot', action='store_true', help="Boot SuperCollider from the command line")

args = parser.parse_args()

launch(args)