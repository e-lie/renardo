from textual.app import ComposeResult
from textual.widgets import Static, Button, Label, ContentSwitcher


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


