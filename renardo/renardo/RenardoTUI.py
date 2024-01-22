from .SCFilesHandling import is_renardo_scfiles_installed, write_sc_renardo_files_in_user_config
from textual import work
from textual.worker import get_current_worker
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import (
    RadioButton,
    RadioSet,
    Header,
    Label,
    Button,
    TabbedContent,
    TabPane,
    Log,
)


class StartRenardoBlock(Widget):
    """Buttons to start renardo in different modes"""

    DEFAULT_CSS = """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_renardo_pipe_btn = Button("Start renardo pipe mode", id="start-renardo-pipe")
        self._start_renardo_foxdot_editor_btn = Button("Start renardo (with FoxDot editor)", id="start-renardo-foxdot-editor")

    def compose(self) -> ComposeResult:
        yield self._start_renardo_pipe_btn
        yield self._start_renardo_foxdot_editor_btn

    def on_mount(self) -> None:
        self._start_renardo_foxdot_editor_btn.focus()



class RenardoTUI(App[None]):
    CSS_PATH = "RenardoTUI.tcss"

    #BINDINGS = [
    #    ("d", "toggle_dark", "Toggle dark mode"),
    #    ("a", "add_stopwatch", "Add"),
    #    ("r", "remove_stopwatch", "Remove"),
    #]
    def __init__(self, renardo_app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renardo_app = renardo_app
        default_spack_ready = reactive(self.renardo_app.spack_manager.is_default_spack_initialized())
        renardo_sc_installed = reactive(is_renardo_scfiles_installed())


    def compose(self) -> ComposeResult:
        yield Header()
        #yield Footer()
        with TabbedContent(initial="start-tab"):
            with TabPane("Start", id="start-tab"):
                with Horizontal():
                    with Vertical():
                        if self.renardo_app.spack_manager.is_default_spack_initialized() and is_renardo_scfiles_installed():
                            yield Label("Default samples pack downloaded and Renardo SuperCollider files installed")
                            yield Button("Start renardo (with FoxDot editor)", id="start-renardo-foxdot-editor")
                            yield Button("Start renardo pipe mode", id="start-renardo-pipe")
                        else:
                            if not self.renardo_app.spack_manager.is_default_spack_initialized():
                                yield Label("Default samples pack needs to be downloaded")
                                yield Button("Download renardo default samples pack", id="dl-renardo-samples")
                            if not is_renardo_scfiles_installed():
                                yield Label("Renardo SuperCollider files need to be installed")
                                yield Button("Create renardo SC Class files and startup code", id="init-renardo-scfiles")
                        yield Button("Quit", id="quit-btn")
                    with Vertical():
                        yield Log(id="log-output")
            with TabPane("Config", id="config-tab"):
                with RadioSet():
                    yield Label("Boot SuperCollider audio backend at startup ?")
                    yield RadioButton("Yes (Still buggy but doesn't hurt to try)")
                    yield RadioButton("No (You should manually open SuperCollider and execute Renardo.start;)", value=True)
                yield Label(id="index")

    @work(exclusive=True, thread=True)
    def dl_samples_background(self) -> None:
        log_output_widget = self.query_one("#log-output", Log)
        worker = get_current_worker()
        self.renardo_app.spack_manager.set_logger(log_output_widget)
        self.renardo_app.spack_manager.init_default_spack()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.renardo_app.args.boot = True if event.radio_set.pressed_index == 1 else False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id

        if button_id == "quit-btn":
            self.exit()

        if button_id == "dl-renardo-samples":
            self.dl_samples_background()

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
