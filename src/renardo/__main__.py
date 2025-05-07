from renardo.settings_manager import settings
from renardo.renardo_app.renardo_app import RenardoApp

app = RenardoApp.get_instance()
app.launch()