from renardo.settings_manager import settings
from renardo.sc_backend.server_manager import ServerManager

# DefaultServer = SCLangServerManager(settings.get("sc_backend.ADDRESS"), PORT, settings.get("sc_backend.PORT2"))
Server = ServerManager(settings.get("sc_backend.ADDRESS"), settings.get("sc_backend.PORT"), settings.get("sc_backend.PORT2"))
Server.init_connection()

if settings.get("sc_backend.FORWARD_PORT") and settings.get("sc_backend.FORWARD_ADDRESS"):
    Server.add_forward(settings.get("sc_backend.FORWARD_ADDRESS"), settings.get("sc_backend.FORWARD_PORT"))