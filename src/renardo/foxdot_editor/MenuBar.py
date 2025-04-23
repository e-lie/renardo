from renardo.foxdot_editor.tkimport import Menu, BooleanVar, IntVar, DISABLED
from renardo.foxdot_editor.tkimport import *
import os.path
from functools import partial
from renardo.settings_manager import settings, get_tutorial_files
from renardo.foxdot_editor.tkimport import SYSTEM, MAC_OS
from renardo.lib.Code import FoxDotCode

# Code menu
ctrl = "Command" if SYSTEM == MAC_OS else "Ctrl"


class MenuBar(Menu):
    def __init__(self, master, visible=True):
        self.root = master
        self.menu_fontsize = ("", 11)
        Menu.__init__(self, master.root)
        # "ticked" menu options
        self.sc3_plugins = BooleanVar()
        self.sc3_plugins.set(settings.get("sc_backend.SC3_PLUGINS"))
        self.cpu_usage = IntVar()
        self.cpu_usage.set(settings.get("core.CPU_USAGE"))
        self.latency = IntVar()
        self.latency.set(settings.get("core.CLOCK_LATENCY"))
        # File menu
        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label="New Document",
                                  command=self.root.newfile,
                                  accelerator="Ctrl+N",
                                  font=self.menu_fontsize)
        self.filemenu.add_command(label="Open",
                                  command=self.root.openfile,
                                  accelerator="Ctrl+O",
                                  font=self.menu_fontsize)
        self.filemenu.add_command(label="Save",
                                  command=self.root.save,
                                  accelerator="Ctrl+S",
                                  font=self.menu_fontsize)
        self.filemenu.add_command(label="Save As...",
                                  command=self.root.saveAs,
                                  font=self.menu_fontsize)
        self.add_cascade(label="File",
                         menu=self.filemenu,
                         font=self.menu_fontsize)
        # Edit menu
        self.editmenu = Menu(self, tearoff=0)
        self.editmenu.add_command(label="Undo",
                                  command=self.root.undo,
                                  accelerator="Ctrl+Z",
                                  font=self.menu_fontsize)
        self.editmenu.add_command(label="Redo",
                                  command=self.root.redo,
                                  accelerator="Ctrl+Y",
                                  font=self.menu_fontsize)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut",
                                  command=self.root.edit_cut,
                                  accelerator="Ctrl+X",
                                  font=self.menu_fontsize)
        self.editmenu.add_command(label="Copy",
                                  command=self.root.edit_copy,
                                  accelerator="Ctrl+C",
                                  font=self.menu_fontsize)
        self.editmenu.add_command(label="Paste",
                                  command=self.root.edit_paste,
                                  accelerator="Ctrl+V",
                                  font=self.menu_fontsize)
        self.editmenu.add_command(label="Select All",
                                  command=self.root.select_all,
                                  accelerator="Ctrl+A",
                                  font=self.menu_fontsize)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Increase Font Size",
                                  command=self.root.zoom_in,
                                  accelerator="Ctrl+=",
                                  font=self.menu_fontsize)
        self.editmenu.add_command(label="Decrease Font Size",
                                  command=self.root.zoom_out,
                                  accelerator="Ctrl+-",
                                  font=self.menu_fontsize)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Preferences",
                                  accelerator="Ctrl+P",
                                  command=self.root.open_preferences,
                                  font=self.menu_fontsize)
        self.add_cascade(label="Edit",
                         menu=self.editmenu,
                         font=self.menu_fontsize)
        # Toolbars
        self.viewmenu = Menu(self, tearoff=0)
        if self.root.menu_toggled.get() is True:
            lbl_menu = "Hide Menu"
        else:
            lbl_menu = "Show Menu"
        self.viewmenu.add_command(label=lbl_menu,
                                  command=self.root.toggle_menu,
                                  accelerator="Ctrl+M",
                                  font=self.menu_fontsize)
        if self.root.linenumbers_toggled.get() is True:
            lbl_linenumbers = "Hide Line Numbers"
        else:
            lbl_linenumbers = "Show Line Numbers"
        self.viewmenu.add_command(label=lbl_linenumbers,
                                  command=self.root.toggle_linenumbers,
                                  accelerator="Ctrl+0",
                                  font=self.menu_fontsize)
        if self.root.treeview_toggled.get() is True:
            lbl_treeview = "Hide Treeview"
        else:
            lbl_treeview = "Show Treeview"
        self.viewmenu.add_command(label=lbl_treeview,
                                  command=self.root.toggle_treeview,
                                  accelerator="Ctrl+U",
                                  font=self.menu_fontsize)
        if self.root.searchbar_toggled.get() is True:
            lbl_searchbar = "Hide Searchbar"
        else:
            lbl_searchbar = "Show Searchbar"
        self.viewmenu.add_command(label=lbl_searchbar,
                                  command=self.root.toggle_searchbar,
                                  accelerator="Ctrl+F",
                                  font=self.menu_fontsize)
        self.viewmenu.add_separator()
        if self.root.console_toggled.get() is True:
            lbl_console = "Hide Console"
        else:
            lbl_console = "Show Console"
        self.viewmenu.add_command(label=lbl_console,
                                  command=self.root.toggle_console,
                                  font=self.menu_fontsize)
        self.viewmenu.add_command(label="Clear Console",
                                  command=self.root.clear_console,
                                  font=self.menu_fontsize)
        self.viewmenu.add_command(label="Export Console Log",
                                  command=self.root.export_console,
                                  font=self.menu_fontsize)
        self.viewmenu.add_separator()
        self.viewmenu.add_checkbutton(label="Toggle Fullscreen",
                                      command=(lambda: self.root.toggle_fullscreen(zoom=True)),
                                      variable=self.root.fullscreen_toggled,
                                      font=self.menu_fontsize)
        self.viewmenu.add_checkbutton(label="Toggle Window Transparency",
                                      command=self.root.toggle_transparency,
                                      variable=self.root.transparent,
                                      font=self.menu_fontsize)
        self.viewmenu.add_checkbutton(label="Toggle Beat Counter",
                                      command=self.root.toggle_counter,
                                      variable=self.root.show_counter,
                                      font=self.menu_fontsize)
        self.add_cascade(label="View",
                         menu=self.viewmenu,
                         font=self.menu_fontsize)
        self.codemenu = Menu(self, tearoff=0)
        self.codemenu.add_command(label="Evaluate Block",
                                  command=self.root.exec_block,
                                  accelerator="{}+Return".format(ctrl),
                                  font=self.menu_fontsize)
        self.codemenu.add_command(label="Evaluate Line",
                                  command=self.root.exec_line,
                                  accelerator="Alt+Return",
                                  font=self.menu_fontsize)
        self.codemenu.add_command(label="Clear Scheduling Clock",
                                  command=self.root.killall,
                                  accelerator="{}+.".format(ctrl),
                                  font=self.menu_fontsize)
        self.codemenu.add_separator()
        self.codemenu.add_checkbutton(label="Listen for connections",
                                      command=self.root.allow_connections,
                                      variable=self.root.listening_for_connections,
                                      font=self.menu_fontsize)
        self.add_cascade(label="Language",
                         menu=self.codemenu,
                         font=self.menu_fontsize)
        # Help
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Display help message",
                                  command=self.root.help,
                                  accelerator="{}+{}".format(ctrl, self.root.help_key),
                                  font=self.menu_fontsize)
        self.helpmenu.add_command(label="Visit Renardo Homepage",
                                  command=self.root.openhomepage,
                                  font=self.menu_fontsize)
        self.helpmenu.add_command(label="Documentation",
                                  command=self.root.opendocumentation,
                                  font=self.menu_fontsize)
        # Tutorials
        self.tutomenu = Menu(self, tearoff=0)
        for tutorial in get_tutorial_files():
            filename = os.path.basename(tutorial)
            if filename.endswith(".py"):
                filename = filename.replace(".py", "")
                data = filename.split("_")
                num = data[0]
                name = " ".join(data[1:]).title()
                self.tutomenu.add_command(label="Load Tutorial {}: {}".format(num, name),
                                          command=partial(self.root.loadfile, tutorial))
        self.helpmenu.add_cascade(label="Tutorials",
                                  menu=self.tutomenu,
                                  font=self.menu_fontsize)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Open Samples Folder",
                                  command=self.root.open_samples_folder,
                                  font=self.menu_fontsize)
        self.helpmenu.add_command(label="Open Samples Chart App",
                                  command=self.root.open_samples_chart_app,
                                  font=self.menu_fontsize)
        self.add_cascade(label="Help",
                         menu=self.helpmenu,
                         font=self.menu_fontsize)
        # Add to root
        self.visible = visible
        if self.visible:
            master.root.config(menu=self)

    def toggle(self):
        """ Hides/shows this menu """
        self.root.root.config(menu=self if not self.visible else 0)
        self.visible = not self.visible
        return

    def allow_connections(self, **kwargs):
        """
        Starts a new instance of ServerManager.TempoServer and connects it
        with the clock
        """
        if self.listening_for_connections.get() is True:
            Clock = self.root.namespace["Clock"]
            Clock.start_tempo_server(TempoServer, **kwargs)
            print("Listening for connections on {}".format(Clock.tempo_server))
        else:
            Clock = self.root.namespace["Clock"]
            Clock.kill_tempo_server()
            print("Closed connections")
        return

    def start_listening(self, **kwargs):
        """ Manual starting of Renardo tempo server """
        # ToDo - take this method out of the menu
        self.listening_for_connections.set(not self.listening_for_connections.get())
        self.allow_connections(**kwargs)
        return

    def set_latency(self, *args):
        """ Updates the cpu usage option """
        self.root.namespace["Clock"].set_latency(self.latency.get())
        return


class PopupMenu(Menu):
    def __init__(self, master, **kwargs):
        self.root = master
        Menu.__init__(self, master.root, tearoff=0)
        self.add_command(label="Undo",
                         command=self.root.undo,
                         accelerator="{}+Z".format(ctrl))
        self.add_command(label="Redo",
                         command=self.root.redo,
                         accelerator="{}+Y".format(ctrl))
        self.add_separator()
        self.add_command(label="Copy",
                         command=self.root.edit_copy,
                         accelerator="{}+C".format(ctrl))
        self.add_command(label="Cut",
                         command=self.root.edit_cut,
                         accelerator="{}+X".format(ctrl))
        self.add_command(label="Paste",
                         command=self.root.edit_paste,
                         accelerator="{}+V".format(ctrl))
        self.add_separator()
        self.add_command(label="Select All",
                         command=self.root.select_all,
                         accelerator="{}+A".format(ctrl))
        self.bind("<FocusOut>", self.hide)  # hide when clicked off

    def show(self, event):
        """ Displays the popup menu """
        try:
            self.post(event.x_root, event.y_root)
        finally:
            self.grab_release()

    def hide(self, event):
        """ Removes menu from sight """
        self.unpost()


class ConsolePopupMenu(Menu):
    def __init__(self, master, **kwargs):
        self.root = master
        Menu.__init__(self, master.root, tearoff=0)
        self.add_command(label="Undo",
                         state=DISABLED,
                         accelerator="{}+Z".format(ctrl))
        self.add_command(label="Redo",
                         state=DISABLED,
                         accelerator="{}+Y".format(ctrl))
        self.add_separator()
        self.add_command(label="Copy",
                         command=self.root.edit_copy,
                         accelerator="{}+C".format(ctrl))
        self.add_command(label="Cut",
                         state=DISABLED,
                         accelerator="{}+X".format(ctrl))
        self.add_command(label="Paste",
                         state=DISABLED,
                         accelerator="{}+V".format(ctrl))
        self.add_separator()
        self.add_command(label="Select All",
                         command=self.root.select_all,
                         accelerator="{}+A".format(ctrl))
        self.bind("<FocusOut>", self.hide)  # hide when clicked off

    def show(self, event):
        """ Displays the popup menu """
        try:
            self.post(event.x_root, event.y_root)
        finally:
            self.grab_release()

    def hide(self, event):
        """ Removes menu from sight """
        self.unpost()
