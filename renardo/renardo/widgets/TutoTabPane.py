from textual.app import ComposeResult
from textual.widgets import TabPane, MarkdownViewer
from renardo.supercollider_mgt.sc_classes_files import SC_USER_CONFIG_DIR
import requests

def download_file(url, filepath):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully as '{filepath}'")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


TUTO_MD_URL = "https://raw.githubusercontent.com/e-lie/renardo-website/master/docs/intro_tuto.md"


class TutoTabPane(TabPane):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_string = ""
        file_path = SC_USER_CONFIG_DIR / 'in_app_tutorials.md'
        try:
            if not (file_path).exists():
                download_file(TUTO_MD_URL, file_path)
            with open(file_path, mode="r") as file:
                self.markdown_string = file.read()
        except:
            self.markdown_string = "Tutorials download failed ! retrying at next renardo launch"

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self.markdown_string)