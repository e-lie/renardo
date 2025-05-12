"""
    FoxDot __main__.py
    ------------------

    Use FoxDot's interface by running this as a Python script, e.g.
    python __main__.py or python -m FoxDot if you have FoxDot correctly
    installed and Python on your path.

"""
from renardo.runtime import FoxDotCode, handle_stdin
from renardo.foxdot_editor.Editor import workspace
import argparse

parser = argparse.ArgumentParser(
    prog="Renardo",
    description="Live coding with Python and SuperCollider",
    epilog="More information: https://renardo.org/")

parser.add_argument('-d', '--dir',
                    action='store',
                    help="Use an alternate directory for looking up samples")
parser.add_argument('-s', '--startup',
                    action='store',
                    help="Use an alternate startup file")
parser.add_argument('-S', '--simple',
                    action='store_true',
                    help="Run Renardo in simple (accessible) mode")
parser.add_argument('-n', '--no-startup',
                    action='store_true',
                    help="Does not load startup.py on boot")
parser.add_argument('-b', '--boot',
                    action='store_true',
                    help="Boot SuperCollider from the command line")

args = parser.parse_args()

if args.dir:
    try:
        # Use given directory
        FoxDotCode.use_sample_directory(args.dir)
    except OSError as Exception:
        # Exit with last error
        import sys
        import traceback
        sys.exit(traceback.print_exc(limit=1))

if args.startup:
    try:
        FoxDotCode.use_startup_file(args.startup)
    except OSError as Exception:
        import sys
        import traceback
        sys.exit(traceback.print_exc(limit=1))

if args.no_startup:
    FoxDotCode.no_startup()

if args.boot:
    FoxDotCode.boot_supercollider()

# Open the GUI
FoxDot = workspace(FoxDotCode).run()
