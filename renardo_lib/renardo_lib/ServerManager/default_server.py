from renardo_lib.Settings import ADDRESS, PORT, PORT2, FORWARD_PORT, FORWARD_ADDRESS
from renardo_lib.ServerManager import ServerManager

# DefaultServer = SCLangServerManager(ADDRESS, PORT, PORT2)
Server = ServerManager(ADDRESS, PORT, PORT2)
Server.init_connection()

if FORWARD_PORT and FORWARD_ADDRESS:
    Server.add_forward(FORWARD_ADDRESS, FORWARD_PORT)