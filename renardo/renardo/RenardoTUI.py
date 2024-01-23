import random
import time

from textual.css.query import NoMatches

from .SCFilesHandling import is_renardo_scfiles_installed, write_sc_renardo_files_in_user_config
from textual import work
from textual.worker import get_current_worker
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical

from textual.widgets import (
    RadioButton,
    RadioSet,
    Header,
    Label,
    Button,
    TabbedContent,
    TabPane,
    Log,
    Static,
    ContentSwitcher,
)

class StartRenardoBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("Default samples pack downloaded and Renardo SuperCollider files installed")
        yield Button("Start renardo (with FoxDot editor)", id="start-renardo-foxdot-editor")
        yield Button("Start renardo pipe mode", id="start-renardo-pipe")

class DownloadRenardoSamplesBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("Default samples pack needs to be downloaded")
        yield Button("Download renardo default samples pack", id="dl-renardo-samples")

class InitRenardoSCFilesBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("Renardo SuperCollider files need to be installed")
        yield Button("Create renardo SC Class files and startup code", id="init-renardo-scfiles")

class InitRenardoBothBlock(Static):
    def compose(self) -> ComposeResult:
        yield InitRenardoSCFilesBlock()
        yield DownloadRenardoSamplesBlock()

class LeftPane(ContentSwitcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield StartRenardoBlock(id="start-renardo")
        yield InitRenardoBothBlock(
            id="init-renardo-both",
        )
        yield InitRenardoSCFilesBlock(id="init-renardo-scfiles")
        yield DownloadRenardoSamplesBlock(id="dl-renardo-samples")


class RenardoTUI(App[None]):
    CSS_PATH = "RenardoTUI.tcss"

    left_pane_mode = reactive("start-renardo")

    #BINDINGS = [
    #    ("d", "toggle_dark", "Toggle dark mode"),
    #    ("a", "add_stopwatch", "Add"),
    #    ("r", "remove_stopwatch", "Remove"),
    #]
    def __init__(self, renardo_app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renardo_app = renardo_app
        self.left_pane_mode = self.calculate_left_pane_mode()

    def calculate_left_pane_mode(self):
        default_spack_ready = self.renardo_app.spack_manager.is_default_spack_initialized()
        renardo_sc_installed = is_renardo_scfiles_installed()
        if default_spack_ready and renardo_sc_installed:
            return "start-renardo"
        elif default_spack_ready and not renardo_sc_installed:
            return "init-renardo-scfiles"
        elif not default_spack_ready and renardo_sc_installed:
            return "dl-renardo-samples"
        else:
            return "init-renardo-both"


    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="start-tab"):
            with TabPane("Start", id="start-tab"):
                with Horizontal():
                    with Vertical():
                        yield LeftPane(initial=self.calculate_left_pane_mode())
                        yield Button("Quit", id="quit-btn")
                    with Vertical():
                        yield Log(id="log-output")
            with TabPane("Config", id="config-tab"):
                with RadioSet():
                    yield Label("Boot SuperCollider audio backend at startup ?")
                    yield RadioButton("Yes (Still buggy but doesn't hurt to try)")
                    yield RadioButton("No (You should manually open SuperCollider and execute Renardo.start)", value=True)

    @work(exclusive=True, thread=True)
    def dl_samples_background(self) -> None:
        log_output_widget = self.query_one("#log-output", Log)
        worker = get_current_worker()
        self.renardo_app.spack_manager.set_logger(log_output_widget)
        self.renardo_app.spack_manager.init_default_spack()
        self.left_pane_mode = self.calculate_left_pane_mode()

    @work(exclusive=True, thread=True)
    def init_scfile_background(self) -> None:
        write_sc_renardo_files_in_user_config()
        self.query_one("#log-output", Log).write_line("Renardo SC files created in user config")
        self.left_pane_mode = self.calculate_left_pane_mode()

    def watch_left_pane_mode(self):
        try:
            self.query_one(LeftPane).current = self.left_pane_mode
            #for debug
            #self.query_one("#log-output", Log).write_line(f"Left pane mode changed to {self.left_pane_mode}")
        except NoMatches:
            pass

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.renardo_app.args.boot = True if event.radio_set.pressed_index == 1 else False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id

        if button_id == "quit-btn":
            #self.query_one("StartRenardoBlock").styles.visibility = "hidden"
            self.exit()

        if button_id == "pick-btn":
           content_id = ["start-renardo", "init-renardo-scfiles", "dl-renardo-samples", "init-renardo-both"]
           self.query_one(LeftPane).current = random.choice(content_id)


        if button_id == "dl-renardo-samples":
            self.dl_samples_background()

        if button_id == "init-renardo-scfiles":
            self.init_scfile_background()

        if button_id == "start-renardo-pipe":
            self.renardo_app.args.pipe = True
            self.exit()
            #from renardo_lib import FoxDotCode, handle_stdin
            # Just take commands from the CLI
            #handle_stdin()

        if button_id == "start-renardo-foxdot-editor":
            self.renardo_app.args.foxdot_editor = True
            self.exit()


    def on_mount(self) -> None:
        self.title = "Renardo"
        self.query_one(RadioSet).focus()
