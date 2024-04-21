from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual import work
from textual.widgets import (
    Static,
    Button,
    Label,
    ContentSwitcher,
    TabbedContent,
    TabPane,
    Log,
    RadioButton,
    RadioSet
)
from textual.containers import Horizontal, Vertical
from .SCFilesHandling import is_renardo_scfiles_installed, write_sc_renardo_files_in_user_config

class MainWidget(TabbedContent):
    
    def __init__(self, renardo_app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renardo_app = renardo_app
        self.left_pane_mode = self.calculate_left_pane_mode()

    def calculate_left_pane_mode(self):
        if not self.renardo_app.sc_instance.supercollider_ready:
            return "sc-not-ready"
        if not is_renardo_scfiles_installed():
            return "init-renardo-scfiles"
        if not self.renardo_app.spack_manager.is_default_spack_initialized():
            return "dl-renardo-samples"
        return "start-renardo"
    
    def compose(self) -> ComposeResult:
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
        #with TabPane("SuperCollider Boot", id="sc-boot"):
        #    with Horizontal():
        #        with Vertical():
        #            yield Button("Start SC instance", id="start-sc-btn")
        #        with Vertical():
        #            yield Log(id="sc-log-output")

    @work(exclusive=True, thread=True)
    def dl_samples_background(self) -> None:
        log_output_widget = self.query_one("#log-output", Log)
        self.renardo_app.spack_manager.set_logger(log_output_widget)
        self.renardo_app.spack_manager.init_default_spack()
        self.left_pane_mode = self.calculate_left_pane_mode()

    @work(exclusive=True, thread=True)
    def init_scfile_background(self) -> None:
        write_sc_renardo_files_in_user_config()
        self.query_one("#log-output", Log).write_line("Renardo SC files created in user config")
        self.left_pane_mode = self.calculate_left_pane_mode()

    @work(exclusive=True, thread=True)
    def start_sc_background(self) -> None:
        if self.renardo_app.sc_instance.start_sclang_subprocess():
            self.query_one("#log-output", Log).write_line("Launching Renardo SC module with SCLang...")
            output_line = self.renardo_app.sc_instance.read_stdout_line()
            while "Welcome to" not in output_line:
                self.query_one("#log-output", Log).write_line(output_line)
                output_line = self.renardo_app.sc_instance.read_stdout_line()
            self.renardo_app.sc_instance.evaluate_sclang_code("Renardo.start;")
            self.renardo_app.sc_instance.evaluate_sclang_code("Renardo.midi;")
            self.query_one("#start-renardo-foxdot-editor-btn", Button).disabled = False
            if self.renardo_app.pulsar_instance.pulsar_ready:
                self.query_one("#start-pulsar-btn", Button).disabled = False
            else:
                self.query_one("#start-pulsar-btn", Button).label = "Pulsar not ready"

            while True:
                self.query_one("#log-output", Log).write_line(self.renardo_app.sc_instance.read_stdout_line())
        else:
            self.query_one("#log-output", Log).write_line("Already started")

    @work(exclusive=True, thread=True)
    def start_pulsar_background(self) -> None:
        self.query_one("#log-output", Log).write_line("Launching Renardo SC module with SCLang...")
        self.renardo_app.pulsar_instance.start_pulsar_subprocess()
        while True:
            self.query_one("#log-output", Log).write_line(self.renardo_app.pulsar_instance.read_stdout_line())

    @work(exclusive=True, thread=True)
    def start_foxdoteditor_background(self) -> None:
        from renardo_lib import FoxDotCode
        # Open the GUI
        from FoxDotEditor.Editor import workspace
        FoxDot = workspace(FoxDotCode).run()
        self.app.exit(0) # Exit renardo when editor is closed because there is a bug when relaunching editor

    def watch_left_pane_mode(self):
        """watch function textual reactive param"""
        try:
            self.query_one(LeftPane).current = self.left_pane_mode
        except NoMatches:
            pass

    # def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
    #     self.renardo_app.args.boot = True if event.radio_set.pressed_index == 1 else False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "quit-btn":
            #self.renardo_app.sc_instance.sclang_process.kill()
            self.app.exit()
        if button_id == "dl-renardo-samples-btn":
            self.dl_samples_background()
        if button_id == "init-renardo-scfiles-btn":
            self.init_scfile_background()
        #if button_id == "start-renardo-pipe-btn":
        #    self.renardo_app.args.pipe = True
        #    self.exit()
        if button_id == "start-pulsar-btn":
            self.start_pulsar_background()
        if button_id == "start-sc-btn":
            self.start_sc_background()
        if button_id == "start-renardo-foxdot-editor-btn":
            self.start_foxdoteditor_background()

    def on_mount(self) -> None:
        self.title = "Renardo"
        #self.query_one(RadioSet).focus()

class StartRenardoBlock(Static):
    def compose(self) -> ComposeResult:
        #yield Label("Default samples pack downloaded and Renardo SuperCollider files installed")
        yield Button("Start SuperCollider Backend", id="start-sc-btn")
        yield Button("Start renardo Pulsar", id="start-pulsar-btn", disabled=True)
        yield Button("Start renardo FoxDot editor", id="start-renardo-foxdot-editor-btn", disabled=True)
        #yield Button("Start renardo pipe mode", id="start-renardo-pipe-btn", disabled=True)


class SCNotReadyBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("SuperCollider seems not ready. Please install it in default location (see doc)")


class DownloadRenardoSamplesBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("Default samples pack needs to be downloaded")
        yield Button("Download renardo default samples pack", id="dl-renardo-samples-btn")


class InitRenardoSCFilesBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("Renardo SuperCollider files need to be installed")
        yield Button("Create renardo SC Class files and startup code", id="init-renardo-scfiles-btn")


class LeftPane(ContentSwitcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield StartRenardoBlock(id="start-renardo")
        yield SCNotReadyBlock(id="sc-not-ready")
        yield InitRenardoSCFilesBlock(id="init-renardo-scfiles")
        yield DownloadRenardoSamplesBlock(id="dl-renardo-samples")
