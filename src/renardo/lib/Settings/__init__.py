# import os
# import sys
# import pathlib
# # Anything that needs to be updated
# from importlib import reload
# from renardo.settings_manager import get_samples_dir_path




# # Directory informations
# FOXDOT_ROOT = os.path.realpath(__file__ + "/../../")
# FOXDOT_SETTINGS = os.path.realpath(__file__ + "/../../Settings/")









# # Set Environment Variables
# try:
#     reload(conf)  # incase of a reload
# except NameError:
#     from renardo.lib.Settings import conf

# FOXDOT_CONFIG_FILE = conf.filename
# ADDRESS = conf.ADDRESS
# PORT = conf.PORT
# PORT2 = conf.PORT2
# FONT = conf.FONT
# BOOT_ON_STARTUP = conf.BOOT_ON_STARTUP
# SUPERCOLLIDER = conf.SUPERCOLLIDER
# SC3_PLUGINS = conf.SC3_PLUGINS
# MAX_CHANNELS = conf.MAX_CHANNELS
# GET_SC_INFO = conf.GET_SC_INFO
# USE_ALPHA = conf.USE_ALPHA
# ALPHA_VALUE = conf.ALPHA_VALUE
# MENU_ON_STARTUP = conf.MENU_ON_STARTUP
# CONSOLE_ON_STARTUP = conf.CONSOLE_ON_STARTUP
# LINENUMBERS_ON_STARTUP = conf.LINENUMBERS_ON_STARTUP
# TREEVIEW_ON_STARTUP = conf.TREEVIEW_ON_STARTUP
# TRANSPARENT_ON_STARTUP = conf.TRANSPARENT_ON_STARTUP
# RECOVER_WORK = conf.RECOVER_WORK
# CHECK_FOR_UPDATE = conf.CHECK_FOR_UPDATE
# LINE_NUMBER_MARKER_OFFSET = conf.LINE_NUMBER_MARKER_OFFSET
# AUTO_COMPLETE_BRACKETS = conf.AUTO_COMPLETE_BRACKETS
# CPU_USAGE = conf.CPU_USAGE
# CLOCK_LATENCY = conf.CLOCK_LATENCY
# FORWARD_ADDRESS = conf.FORWARD_ADDRESS
# FORWARD_PORT = conf.FORWARD_PORT
# SAMPLES_DIR = conf.SAMPLES_DIR
# SAMPLES_PACK_NUMBER = conf.SAMPLES_PACK_NUMBER
# COLOR_THEME = conf.COLOR_THEME
# TEXT_COLORS = conf.TEXT_COLORS

# if conf.SAMPLES_DIR is not None and conf.SAMPLES_DIR != "":
#     FOXDOT_SND = os.path.realpath(conf.SAMPLES_DIR)



