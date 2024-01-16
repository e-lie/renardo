import argparse
from renardo import launch, parse_args

# main is to call the module with python -m but we want to make a pypi package application with entry_point
# More here : https://setuptools.pypa.io/en/latest/userguide/entry_point.html

launch(parse_args())