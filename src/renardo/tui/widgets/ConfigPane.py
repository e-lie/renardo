from textual.app import ComposeResult
from textual.widgets import TabPane, RadioSet, Label, RadioButton


class OpenAutostartDirectly(RadioSet):
    def compose(self) -> ComposeResult:
        yield Label("Directly open Autostart tab at startup")
        yield RadioButton("Yes ")
        yield RadioButton("No", value=True)

class SCOutputNum(RadioSet):
    def compose(self) -> ComposeResult:
        yield Label("Number of SuperCollider audio outputs")


class ConfigPane(TabPane):
    def compose(self) -> ComposeResult:
        yield OpenAutostartDirectly()
