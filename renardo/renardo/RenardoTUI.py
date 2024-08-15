from textual.app import App, ComposeResult
from textual.reactive import reactive
from renardo_lib.ServerManager import ServerManager
from renardo_lib.Settings import ADDRESS, PORT, PORT2
from textual import work
from textual.binding import Binding
from textual.css.query import NoMatches
from renardo.supercollider_mgt.sc_classes_files import is_renardo_sc_classes_initialized, write_sc_renardo_files_in_user_config
from textual.containers import Horizontal, Vertical, Center, Grid
from textual.widgets import (
    Header,
    Footer,
    Button,
    Log,
    TabbedContent,
    TabPane
)

from renardo.widgets.TutoTabPane import TutoTabPane
from renardo.widgets.RightPane import RightPane, ResourcesRightPane

class RenardoTUI(App[None]):
    CSS_PATH = "RenardoTUI.tcss"
    right_pane_mode = reactive(None)
    base_sample_pack_downloaded = reactive(None, recompose=True)
    sc_backend_started = reactive(None)
    renardo_sc_class_initialized = reactive(None, recompose=True)

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
    ]

    def __init__(self, renardo_app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app.dark = False
        self.renardo_app = renardo_app

        # State variables
        self.right_pane_mode = self.get_right_pane_mode()
        self.right_pane_maximized = None # maximization feature TODO ?
        self.renardo_sc_class_initialized = is_renardo_sc_classes_initialized()
        self.base_sample_pack_downloaded = self.renardo_app.spack_manager.is_default_spack_initialized()
        self.sc_backend_started = self.test_sclang_connection()
        self.supercollider_found = self.renardo_app.sc_instance.supercollider_ready
        self.pulsar_found = self.renardo_app.pulsar_instance.pulsar_ready


    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Start", id="start-tab"):
                with Horizontal():
                    with Center(classes="main-center"):
                        with Grid(classes="main-grid"):
                            yield Button("1 - Music Resources", id="music-resources-1-btn", classes="home-button")
                            yield Button("2 - SuperCollider Backend", id="supercollider-backend-2-btn", classes="home-button")
                            #yield Button("3 - Renardo Instance", id="renardo-instance-3-btn", classes="home-button")
                            yield Button("3 - Livecoding Editor", id="livecoding-editor-3-btn", classes="home-button")
                    with Vertical(classes="right-pane"):
                        yield RightPane(initial=self.right_pane_mode)
            #with TabPane("Logs", id="log-tab"):
            #    yield Log(id="renardo-log")
            #yield TutoTabPane(title="Tutorials", id="tuto-tab")

        # yield Footer()

    ################ App state methods

    def update_app_state(self):
        self.renardo_sc_class_initialized = is_renardo_sc_classes_initialized()
        self.base_sample_pack_downloaded = self.renardo_app.spack_manager.is_default_spack_initialized()
        self.sc_backend_started = self.test_sclang_connection()
        self.supercollider_found = self.renardo_app.sc_instance.supercollider_ready
        self.pulsar_found = self.renardo_app.pulsar_instance.pulsar_ready

    def get_right_pane_mode(self):
        return "music-resources-1"

    def test_sclang_connection(self):
        TestServer = ServerManager(ADDRESS, PORT, PORT2)
        TestServer.sclang._printed_error = True
        return TestServer.test_connection()

    ################# Reactiveness for state variables (magic textual watch methods)

    def watch_right_pane_mode(self):
        # This is a special method from textual that is not easy to move from the app
        try:
            self.query_one(RightPane).current = self.right_pane_mode
        except NoMatches:
            pass


    ################ Event Handlers

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id

        # Right pane mode switch
        if button_id in ["music-resources-1-btn", "supercollider-backend-2-btn",
            "renardo-instance-3-btn", "livecoding-editor-3-btn"]:
            self.right_pane_mode = button_id[:-4]
            pass

        if button_id == "dl-renardo-samples-btn":
            self.dl_samples_background()
        if button_id == "init-renardo-scfiles-btn":
            self.init_renardo_sc_classes()
        #if button_id == "start-renardo-pipe-btn":
        #    self.renardo_app.args.pipe = True
        #    self.exit()
        if button_id == "start-pulsar-btn":
            self.start_pulsar_background()
        if button_id == "start-sc-btn":
            self.start_sc_backend()
        if button_id == "start-renardo-foxdot-editor-btn":
            self.start_foxdoteditor_background()

    def on_mount(self) -> None:
        self.title = "Renardo"
        #self.query_one(RadioSet).focus()

    def quit(self):
        # self.renardo_app.sc_instance.sclang_process.kill()
        self.exit()

    # def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
    #     self.renardo_app.args.boot = True if event.radio_set.pressed_index == 1 else False





    ################ Background Jobs

    @work(exclusive=True, thread=True)
    def dl_samples_background(self) -> None:
        log_output_widget = self.query_one("#spack-dl-log-output", Log)
        self.renardo_app.spack_manager.set_logger(log_output_widget)
        self.renardo_app.spack_manager.init_default_spack()
        self.update_app_state()

    @work(exclusive=True, thread=True)
    def init_renardo_sc_classes(self) -> None:
        write_sc_renardo_files_in_user_config()
        self.query_one("#sclang-log-output", Log).write_line("Renardo SC files created in user config")
        self.update_app_state()

    @work(exclusive=True, thread=True)
    def start_sc_backend(self) -> None:
        if self.renardo_app.sc_instance.start_sclang_subprocess():
            self.query_one("#sclang-log-output", Log).write_line("Launching Renardo SC module with SynthDefManagement...")
            output_line = self.renardo_app.sc_instance.read_stdout_line()
            while "Welcome to" not in output_line:
                self.query_one("#sclang-log-output", Log).write_line(output_line)
                output_line = self.renardo_app.sc_instance.read_stdout_line()
            self.renardo_app.sc_instance.evaluate_sclang_code("Renardo.start;")
            self.renardo_app.sc_instance.evaluate_sclang_code("Renardo.midi;")
            while True:
                self.query_one("#sclang-log-output", Log).write_line(self.renardo_app.sc_instance.read_stdout_line())
        else:
            self.query_one("#sclang-log-output", Log).write_line("SuperCollider backend already started (sclang backend externally managed)\nIf you want to handle the backend manually you should ensure... \n...you executed Renardo.start; correctly in SuperCollider IDE")
            self.query_one("#start-renardo-foxdot-editor-btn", Button).disabled = False
            if self.renardo_app.pulsar_instance.pulsar_ready:
                self.query_one("#start-pulsar-btn", Button).disabled = False

    @work(exclusive=True, thread=True)
    def start_pulsar_background(self) -> None:
        self.query_one("#sclang-log-output", Log).write_line("Launching Renardo SC module with SynthDefManagement...")
        self.renardo_app.pulsar_instance.start_pulsar_subprocess()
        while True:
            self.query_one("#sclang-log-output", Log).write_line(self.renardo_app.pulsar_instance.read_stdout_line())

    @work(exclusive=True, thread=True)
    def start_foxdoteditor_background(self) -> None:
        from renardo_lib.runtime import FoxDotCode
        # Open the GUI
        from FoxDotEditor.Editor import workspace
        FoxDot = workspace(FoxDotCode).run()
        self.app.exit(0) # Exit renardo when editor is closed because there is a bug when relaunching editor

