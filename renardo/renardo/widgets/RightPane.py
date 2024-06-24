from textual.app import ComposeResult
from textual.widgets import Static, Button, Label, ContentSwitcher, Log

class RightPane(ContentSwitcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield ResourcesRightPane(id="music-resources-1")
        yield SCBackendRightPane(id="supercollider-backend-2")
        #yield RenardoLibRightPane(id="renardo-lib-3")
        yield LivecodingEditorRightPane(id="livecoding-editor-3")

class ResourcesRightPane(Static):
    def compose(self) -> ComposeResult:
        if not self.app.renardo_sc_class_initialized:
            yield Label("Renardo SuperCollider files need to be installed")
            yield Button("Create renardo SC Class files and startup code", id="init-renardo-scfiles-btn")
        else:
            yield Label("Renardo SuperCollider classes are installed")
        if not self.app.base_sample_pack_downloaded:
            yield Label("Default samples pack needs to be downloaded")
            yield Button("Download renardo default samples pack", id="dl-renardo-samples-btn")
            yield Log(id="spack-dl-log-output")
        else:
            yield Label("The default sample pack is downloaded")

class SCBackendRightPane(Static):
    def compose(self) -> ComposeResult:
        if self.app.sc_backend_started:
            yield Label(f"SuperCollider backend already started ! (manually/externally)")
        elif not self.app.supercollider_found:
            yield Label("Renardo can't find Supercollider")
            yield Label("Please install it in default location and ensure `sclang` is in PATH")
            yield Label("Alternatively you can start the backend manually (see doc)")
        else:
            yield Button("Start SuperCollider Backend", id="start-sc-btn")
            yield Log(id="sclang-log-output")

class RenardoLibRightPane(Static):
    def compose(self) -> ComposeResult:
        yield Label("SuperCollider seems not ready. Please install it in default location (see doc)")
        yield Button("Start SuperCollider Backend", id="start-sc-btn")

class LivecodingEditorRightPane(Static):
    def compose(self) -> ComposeResult:
        #yield Label("Default samples pack downloaded and Renardo SuperCollider files installed")
        if self.app.pulsar_found:
            yield Button("Start Pulsar", id="start-pulsar-btn", disabled=False)
        else:
            yield Label("Renardo can't find Pulsar automatically ! (you can still launch it manually)")
        yield Button("Start FoxDot editor", id="start-renardo-foxdot-editor-btn", disabled=False)
        #yield Button("Start renardo pipe mode", id="start-renardo-pipe-btn", disabled=True)


