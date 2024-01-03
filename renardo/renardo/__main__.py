import argparse
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Button, Static

from renardo import launch

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


class RenardoTUI(App):
    CSS_PATH = "renardo_tui.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            VerticalScroll(
                Static("Welcome to Renardo livecoding environment !", classes="header"),
                Button("Launch sound server (SuperCollider)", variant="primary", disabled=True),
                Button("Launch Classic Editor (FoxDot Editor)", variant="primary"),
            ),
            # VerticalScroll(
            #     # Static("Disabled Buttons", classes="header"),
            # ),
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        launch(args)
        # self.exit(str(event.button))

app = RenardoTUI()
app.run()