from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.binding import Binding
from renardo.widgets.MainWidget import MainWidget

from textual.widgets import (
    Header,
    Footer,
)


class RenardoTUI(App[None]):
    CSS_PATH = "RenardoTUI.tcss"
    left_pane_mode = reactive("start-renardo")
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
    ]

    def __init__(self, renardo_app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renardo_app = renardo_app

    def compose(self) -> ComposeResult:
        yield Header()
        yield MainWidget(self.renardo_app)
        yield Footer()

    def quit(self):
        # self.renardo_app.sc_instance.sclang_process.kill()
        self.exit()
