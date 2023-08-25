from renardo.boot_supercollider import boot_supercollider
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

    if args.boot:
        boot_supercollider()
        time.sleep(5)

    from renardo_lib.lib import FoxDotCode, handle_stdin
    if args.pipe:
        # Just take commands from the CLI
        handle_stdin()
    else:
        # Open the GUI
        from FoxDotEditor.Editor import workspace
        FoxDot = workspace(FoxDotCode).run()
