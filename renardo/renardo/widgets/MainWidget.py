from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual import work
from textual.widget import Widget
from textual.widgets import (
    Button,
    Label,
    TabbedContent,
    TabPane,
    Log,
    RadioButton,
    RadioSet,
    TextArea,
    MarkdownViewer
)
from textual.containers import Horizontal, Vertical
from renardo.SCFilesHandling import is_renardo_scfiles_installed, write_sc_renardo_files_in_user_config
from renardo.widgets.Widgets import LeftPane
from renardo.widgets.ConfigPane import ConfigPane


class MainWidget(Widget):
    
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
        with TabbedContent():
            with TabPane("Welcome", id="welcome-tab"):
                yield Label("Welcome to renardo terminal user interface (TUI) !!")
                yield Label("Here you can configure (WIP), learn (WIP) renardo and start it's different modules")
            with TabPane("Autostart", id="start-tab"):
                with Horizontal():
                    with Vertical():
                        yield LeftPane(initial=self.calculate_left_pane_mode())
                    with Vertical():
                        yield Log(id="log-output")
#             with TabPane("Documentation", id="doc-tab"):
#                 EXAMPLE_MARKDOWN = """\
# # Markdown Viewer

# This is an example of Textual's `MarkdownViewer` widget.

# ## Features

# Markdown syntax and extensions are supported.

# - Typography *emphasis*, **strong**, `inline code` etc.
# - Headers
# - Lists (bullet and ordered)
# - Syntax highlighted code blocks
# - Tables!
#                 """
#                 yield MarkdownViewer(EXAMPLE_MARKDOWN)

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
            self.query_one("#log-output", Log).write_line("SuperCollider backend already started (sclang backend externally managed)\nIf you want to handle the backend manually you should ensure... \n...you executed Renardo.start; correctly in SuperCollider IDE")
            self.query_one("#start-renardo-foxdot-editor-btn", Button).disabled = False
            if self.renardo_app.pulsar_instance.pulsar_ready:
                self.query_one("#start-pulsar-btn", Button).disabled = False

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


