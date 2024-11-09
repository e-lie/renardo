FOXDOT_EDITOR_ROOT = os.path.realpath(__file__ + "/../..")
FOXDOT_ICON = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/icon.ico")
FOXDOT_ICON_GIF = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/icon.gif")
FOXDOT_HELLO = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/hello.txt")
FOXDOT_STARTUP_PATH = os.path.realpath(FOXDOT_ROOT + "/Custom/startup.py")
FOXDOT_EDITOR_THEMES = os.path.realpath(FOXDOT_EDITOR_ROOT + "/themes")
FOXDOT_TEMP_FILE = os.path.realpath(FOXDOT_EDITOR_ROOT + "/tmp/tempfile.txt")


# If the tempfile doesn't exist, create it
if not os.path.isfile(FOXDOT_TEMP_FILE):
    try:
        with open(FOXDOT_TEMP_FILE, "w") as f:
            pass
    except FileNotFoundError:
        pass