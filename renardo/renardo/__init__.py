from .SCFilesHandling import write_sc_renardo_files_in_user_config
from .SuperColliderInstance import RenardoSupercolliderInstance
import argparse
import time


def launch(args):

    # if args.cli:
    # if args.dir:
    #     try:
    #         # Use given directory
    #         FoxDotCode.use_sample_directory(args.dir)
    #     except OSError as e:
    #         # Exit with last error
    #         import sys, traceback
    #         sys.exit(traceback.print_exc(limit=1))

    # if args.startup:
    #     try:
    #         FoxDotCode.use_startup_file(args.startup)
    #     except OSError as e:
    #         import sys, traceback
    #         sys.exit(traceback.print_exc(limit=1))

    # if args.no_startup:
    #     FoxDotCode.no_startup()

    renardo_sc_instance = None

    if args.create_scfiles:
        write_sc_renardo_files_in_user_config()

    if args.boot:
        renardo_sc_instance = RenardoSupercolliderInstance()
        time.sleep(3)

    if args.pipe:
        from renardo_lib import FoxDotCode, handle_stdin
        # Just take commands from the CLI
        handle_stdin()
    else:
        from renardo_lib import FoxDotCode
        # Open the GUI
        from FoxDotEditor.Editor import workspace
        FoxDot = workspace(FoxDotCode).run()

def parse_args():
    parser = argparse.ArgumentParser(
        prog="renardo",
        description="Live coding with Python and SuperCollider",
        epilog="More information: https://renardo.org/"
    )

    parser.add_argument('-p', '--pipe', action='store_true', help="run FoxDot from the command line interface")
    parser.add_argument('-d', '--dir', action='store', help="use an alternate directory for looking up samples")
    parser.add_argument('-s', '--startup', action='store', help="use an alternate startup file")

    parser.add_argument('-n', '--no-startup', action='store_true', help="does not load startup.py on boot")
    # store_false => boot default value = True WTF
    parser.add_argument('-b', '--boot', action='store_false', help="Boot SuperCollider Renardo instance automatically")
    parser.add_argument('-c', '--create-scfiles', action='store_false', help="Create Renardo class file and startup file in SuperCollider user conf dir.")

    return parser.parse_args()


def entrypoint():
    launch(parse_args())
