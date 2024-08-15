from renardo.supercollider_mgt.sc_classes_files import write_sc_renardo_files_in_user_config
from renardo.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
from .pulsar_mgt import PulsarInstance
from .RenardoTUI import RenardoTUI
from renardo_gatherer.samples_download import SPackManager

import argparse
import time

class RenardoApp:

    def __init__(self):
        self.sc_instance = None
        self.spack_manager = SPackManager()
        self.args = RenardoApp.parse_args()
        self.sc_instance = SupercolliderInstance()
        self.pulsar_instance = PulsarInstance()
        self.launch()

    def launch(self):

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

        if self.args.create_scfiles:
            write_sc_renardo_files_in_user_config()

        if not (self.args.no_tui or self.args.pipe or self.args.foxdot_editor):
            RenardoTUI(renardo_app=self).run()

        if self.args.boot:
            print("Launching Renardo SC module with SynthDefManagement...")
            self.sc_instance.start_sclang_subprocess()
            output_line = self.sc_instance.read_stdout_line()
            while "Welcome to" not in output_line:
                print(output_line[:-1]) # remove \n at the end to avoid double newline
                output_line = self.sc_instance.read_stdout_line()
            self.sc_instance.evaluate_sclang_code("Renardo.start;")
            time.sleep(3)

        if self.args.pipe:
            from renardo_lib.runtime import handle_stdin, FoxDotCode
            # Just take commands from the CLI
            handle_stdin()
        elif self.args.foxdot_editor:
            from renardo_lib.runtime import FoxDotCode
            # Open the GUI
            from FoxDotEditor.Editor import workspace
            FoxDot = workspace(FoxDotCode).run()
        elif self.args.no_tui:
            print("You need to choose a launching mode : TUI, --pipe or --foxdot-editor...")
        print("Quitting...")
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(
            prog="renardo",
            description="Live coding with Python and SuperCollider",
            epilog="More information: https://renardo.org/"
        )
        parser.add_argument('-N', '--no-tui', action='store_true', help="does start renardo TUI")
        parser.add_argument('-p', '--pipe', action='store_true', help="run Renardo from the command line interface")
        parser.add_argument('-f', '--foxdot-editor', action='store_true', help="run Renardo with the classic FoxDot code editor")
        # parser.add_argument('-d', '--dir', action='store', help="use an alternate directory for looking up samples")
        # parser.add_argument('-s', '--startup', action='store', help="use an alternate startup file")
        # parser.add_argument('-n', '--no-startup', action='store_true', help="does not load startup.py on boot")
        # store_false => boot default value = True WTF
        parser.add_argument('-b', '--boot', action='store_true', help="Boot SuperCollider Renardo instance automatically")
        parser.add_argument('-c', '--create-scfiles', action='store_true', help="Create Renardo class file and startup file in SuperCollider user conf dir.")

        return parser.parse_args()

