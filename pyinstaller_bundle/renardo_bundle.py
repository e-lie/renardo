
from renardo import launch

import argparse

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