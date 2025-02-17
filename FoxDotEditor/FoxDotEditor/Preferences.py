
from FoxDotEditor.tkimport import *
from renardo_lib.Settings import *
from .Format import *
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
try:
    import tkMessageBox
except ImportError:
    from tkinter import messagebox as tkMessageBox
import os.path


class Preferences:
    def __init__(self):
        self.w = 850
        self.h = 600
        self.stop = tb.Toplevel(topmost=True)
        self.stop.title("Preferences")
        self.stop.protocol("WM_DELETE_WINDOW", self.save_and_close)
        self.stop.minsize(400, 300)
        self.stop.resizable(True, True)
        self.stop.geometry(str(self.w)+"x"+str(self.h))
        try:
            # Use .ico file by default
            self.stop.iconbitmap(FOXDOT_ICON)
        except TclError:
            # Use .gif if necessary
            self.stop.tk.call('wm',
                              'iconphoto',
                              self.stop._w,
                              PhotoImage(file=FOXDOT_ICON_GIF))
        self.themes = ()
        self.theme_colors = {}
        # Opening JSON file
        with open(FOXDOT_EDITOR_THEMES, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            # Text area colours
            # ------------------
            theme_list = json_object["themes"]
            for item in theme_list:
                theme = list(item.keys())[0]
                self.themes = self.themes + (theme,)
                if theme == COLOR_THEME:
                    # Colors
                    # ------------------
                    self.theme_colors['primary'] = item[COLOR_THEME]["colors"]['primary']
                    self.theme_colors['secondary'] = item[COLOR_THEME]["colors"]['secondary']
                    self.theme_colors['success'] = item[COLOR_THEME]["colors"]['success']
                    self.theme_colors['info'] = item[COLOR_THEME]["colors"]['info']
                    self.theme_colors['warning'] = item[COLOR_THEME]["colors"]['warning']
                    self.theme_colors['danger'] = item[COLOR_THEME]["colors"]['danger']
                    self.theme_colors['light'] = item[COLOR_THEME]["colors"]['light']
                    self.theme_colors['dark'] = item[COLOR_THEME]["colors"]['dark']
                    self.theme_colors['bg'] = item[COLOR_THEME]["colors"]['bg']
                    self.theme_colors['fg'] = item[COLOR_THEME]["colors"]['fg']
                    self.theme_colors['border'] = item[COLOR_THEME]["colors"]['border']
                    self.theme_colors['active'] = item[COLOR_THEME]["colors"]['active']
                    # Prompt colours
                    # ------------------
                    self.theme_colors['selectfg'] = item[COLOR_THEME]["colors"]['selectfg']
                    self.theme_colors['selectbg'] = item[COLOR_THEME]["colors"]['selectbg']
                    # Console area colours
                    # ------------------
                    self.theme_colors['inputfg'] = item[COLOR_THEME]["colors"]['inputfg']
                    self.theme_colors['inputbg'] = item[COLOR_THEME]["colors"]['inputbg']
                    self.theme_colors['type'] = item[COLOR_THEME]["type"]
        self.settings = {}
        self.conf_json = FOXDOT_CONFIG_FILE
        self.tabview = tb.Notebook(self.stop)
        self.general = tb.Frame(self.tabview)
        self.colors = tb.Frame(self.tabview)
        self.advanced = tb.Frame(self.tabview)
        self.tabview.add(self.general, text="General")  # add tab at the end
        self.tabview.add(self.colors, text="Appearance")
        self.tabview.add(self.advanced, text="Advanced")
        self.tabview.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.alert_text = "MODIFYING THIS FILE WILL OVERWRITE CHANGES DONE IN 'General' AND 'Appearance'. SAVE 'Preferences' FIRST TO CONTINUE!"
        self.alert = tb.Label(self.advanced,
                              text=self.alert_text)
        self.alert.grid(row=0, column=0, columnspan=3, padx=10, pady=20, sticky='nsew')
        self.y_scroll = tb.Scrollbar(self.advanced)
        self.y_scroll.grid(row=1, column=4, sticky='nsew')
        self.textbox = Text(self.advanced,
                            yscrollcommand=self.y_scroll.set)
        self.textbox.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.y_scroll.configure(command=self.textbox.yview)
        self.exit = tb.Button(
            self.stop,
            text="Cancel",
            command=self.save_and_close)
        self.exit.grid(row=1, column=2, padx=20, sticky="ew")
        self.save = tb.Button(
            self.stop,
            text="Save Changes",
            command=self.save_and_close)
        self.save.grid(row=1, column=3, padx=20, sticky="ew")
        self.unsaved = True
        try:
            with open(self.conf_json) as f:
                self.text = f.read().rstrip()
            self.textbox.insert(INSERT, self.text)
        except FileNotFoundError:
            print("conf.json file not found")
        # Add binds?
        self.textbox.bind()
        self.theme_name = ""
        # Settings values
        self.menu_start = BooleanVar()
        self.menu_start.set(MENU_ON_STARTUP)
        self.linenumbers_start = BooleanVar()
        self.linenumbers_start.set(LINENUMBERS_ON_STARTUP)
        self.console_start = BooleanVar()
        self.console_start.set(CONSOLE_ON_STARTUP)
        self.treeview_start = BooleanVar()
        self.treeview_start.set(TREEVIEW_ON_STARTUP)
        self.midibar_start = BooleanVar()
        self.midibar_start.set(MIDIBAR_ON_STARTUP)
        self.recover_work = BooleanVar()
        self.recover_work.set(RECOVER_WORK)
        self.check_update = BooleanVar()
        self.check_update.set(CHECK_FOR_UPDATE)
        # Editor
        self.linenumber_offset = StringVar()
        self.linenumber_offset.set(LINE_NUMBER_MARKER_OFFSET)
        self.brackets_auto = BooleanVar()
        self.brackets_auto.set(AUTO_COMPLETE_BRACKETS)
        # Sample values
        self.samples_dir = StringVar()
        self.samples_dir.set(SAMPLES_DIR)
        self.sample_pack = StringVar()
        self.sample_pack.set(SAMPLES_PACK_NUMBER)
        # Connection values
        self.address = StringVar()
        self.address.set(ADDRESS)
        self.port = StringVar()
        self.port.set(PORT)
        self.port2 = StringVar()
        self.port2.set(PORT2)
        self.fwd_address = StringVar()
        self.fwd_address.set(FORWARD_ADDRESS)
        self.fwd_port = StringVar()
        self.fwd_port.set(FORWARD_PORT)
        # SuperCollider
        self.sc_start = BooleanVar()
        self.sc_start.set(BOOT_ON_STARTUP)
        self.sc_path = StringVar()
        self.sc_path.set(SUPERCOLLIDER)
        self.sc3_start = BooleanVar()
        self.sc3_start.set(SC3_PLUGINS)
        self.max_ch = StringVar()
        self.max_ch.set(MAX_CHANNELS)
        self.sc_info = BooleanVar()
        self.sc_info.set(GET_SC_INFO)
        # Performance
        self.cpu_use = StringVar()
        cpu_val = self.convert2str(CPU_USAGE)
        self.cpu_use.set(cpu_val)
        lat_val = self.convert2str(CLOCK_LATENCY)
        self.clk_lat = StringVar()
        self.clk_lat.set(lat_val)
        # Appearance
        # theme
        self.theme = StringVar()
        self.theme.set(COLOR_THEME)
        self.text_theme = StringVar()
        self.text_theme.set(COLOR_THEME)
        self.font = StringVar()
        self.font.set(FONT)
        self.use_alpha = BooleanVar()
        self.use_alpha.set(USE_ALPHA)
        self.alpha_val = StringVar()
        self.alpha_val.set(ALPHA_VALUE)
        self.alpha_start = BooleanVar()
        self.alpha_start.set(TRANSPARENT_ON_STARTUP)
        # x distance for widgets
        # ------------------
        self.padx = 10
        # Widgets in section General
        # ON START
        self.g1 = tb.Frame(self.general)
        self.g1.grid(row=0, column=0, sticky="n")
        self.g2 = tb.Frame(self.general)
        self.g2.grid(row=0, column=1, sticky="n")
        self.g3 = tb.Frame(self.general)
        self.g3.grid(row=0, column=2, sticky="n")
        self.g4 = tb.Frame(self.general)
        self.g4.grid(row=0, column=3, sticky="n")
        self.lbl_on_start = tb.Label(
            self.g1,
            text="ACTIVATED ON START")
        self.lbl_on_start.grid(column=0, row=0, padx=self.padx*2, pady=10,
                               sticky="nw")
        self.tgl_menu = tb.Checkbutton(
            self.g1, text="Menu", variable=self.menu_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_menu.grid(column=0, row=1, padx=self.padx*2, pady=10,
                           sticky="nw")
        self.tgl_console = tb.Checkbutton(
            self.g1, text="Console", variable=self.console_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_console.grid(column=0, row=2, padx=self.padx*2, pady=10,
                              sticky="nw")
        self.tgl_linenumbers = tb.Checkbutton(
            self.g1, text="Line Numbers", variable=self.linenumbers_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_linenumbers.grid(column=0, row=2, padx=self.padx*2, pady=10,
                                  sticky="nw")
        self.tgl_treeview = tb.Checkbutton(
            self.g1, text="Treeview", variable=self.treeview_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_treeview.grid(column=0, row=3, padx=self.padx*2, pady=10,
                               sticky="nw")
        self.tgl_midibar = tb.Checkbutton(
            self.g1, text="MidiBar", variable=self.midibar_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_midibar.grid(column=0, row=4, padx=self.padx*2, pady=10,
                              sticky="nw")
        self.tgl_recover = tb.Checkbutton(
            self.g1, text="Recover Work", variable=self.recover_work,
            style='Roundtoggle.Toolbutton')
        self.tgl_recover.grid(column=0, row=5, padx=self.padx*2, pady=10,
                              sticky="nw")
        self.tgl_update = tb.Checkbutton(
            self.g1, text="Check for Updates", variable=self.check_update,
            style='Roundtoggle.Toolbutton')
        self.tgl_update.grid(column=0, row=6, padx=self.padx*2, pady=10,
                             sticky="nw")
        # EDITOR
        self.lbl_on_start = tb.Label(
            self.g1, text="EDITOR")
        self.lbl_on_start.grid(column=0, row=7, padx=self.padx*2, pady=10,
                               sticky="nw")
        self.tgl_update = tb.Checkbutton(
            self.g1, text="Autocomplete Brackets", variable=self.brackets_auto,
            style='Roundtoggle.Toolbutton')
        self.tgl_update.grid(column=0, row=8, padx=self.padx*2, pady=10,
                             sticky="nw")
        self.lbl_line_offset = tb.Label(
            self.g1, text="Linenumber Marker Offset")
        self.lbl_line_offset.grid(column=0, row=9, padx=self.padx*2,
                                  sticky="sw")
        self.entry_linenum_offset = tb.Entry(
            self.g1, textvariable=self.linenumber_offset)
        self.entry_linenum_offset.grid(column=0, row=10, padx=self.padx*2,
                                       pady=5, sticky="nw")
        # CONNECTIONS
        self.lbl_connect = tb.Label(
            self.g2, text="CONNECTIONS")
        self.lbl_connect.grid(column=1, row=0, padx=self.padx, pady=10,
                              sticky="nw")
        self.lbl_address = tb.Label(
            self.g2, text="Address")
        self.lbl_address.grid(column=1, row=1, padx=self.padx, sticky="sw")
        self.entry_address = tb.Entry(
            self.g2, textvariable=self.address)
        self.entry_address.grid(column=1, row=2, padx=self.padx, sticky="nw")
        self.lbl_port = tb.Label(
            self.g2, text="Port")
        self.lbl_port.grid(column=1, row=3, padx=self.padx, sticky="sw")
        self.entry_port = tb.Entry(
            self.g2, textvariable=self.port)
        self.entry_port.grid(column=1, row=4, padx=self.padx, sticky="nw")
        self.lbl_port2 = tb.Label(
            self.g2, text="Port2")
        self.lbl_port2.grid(column=1, row=5, padx=self.padx, sticky="sw")
        self.entry_port2 = tb.Entry(
            self.g2, textvariable=self.port2)
        self.entry_port2.grid(column=1, row=6, padx=self.padx, sticky="nw")
        self.lbl_fwd_address = tb.Label(
            self.g2, text="Forward Address")
        self.lbl_fwd_address.grid(column=1, row=7, padx=self.padx, sticky="sw")
        self.entry_fwd_address = tb.Entry(
            self.g2, textvariable=self.fwd_address)
        self.entry_fwd_address.grid(column=1, row=8, padx=self.padx, pady=5,
                                    sticky="nw")
        self.lbl_fwd_port = tb.Label(
            self.g2, text="Forward Port")
        self.lbl_fwd_port.grid(column=1, row=9, padx=self.padx, sticky="sw")
        self.entry_fwd_port = tb.Entry(
            self.g2, textvariable=self.fwd_port)
        self.entry_fwd_port.grid(column=1, row=10, padx=self.padx, pady=5,
                                 sticky="nw")
        # SUPERCOLLIDER
        self.lbl_sc = tb.Label(
            self.g3, text="SUPERCOLLIDER")
        self.lbl_sc.grid(column=2, row=0, padx=self.padx, pady=10, sticky="nw")
        self.tgl_sc_start = tb.Checkbutton(
            self.g3, text="Boot SC on Start", variable=self.sc_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_sc_start.grid(column=2, row=1, padx=self.padx, pady=10,
                               sticky="sw")
        self.lbl_sc_path = tb.Label(
            self.g3, text="SuperCollider Path")
        self.lbl_sc_path.grid(column=2, row=2, padx=self.padx, sticky="sw")
        self.entry_sc_path = tb.Entry(
            self.g3, textvariable=self.sc_path)
        self.entry_sc_path.grid(column=2, row=3, padx=self.padx, pady=5,
                                sticky="nw")
        self.tgl_sc3_start = tb.Checkbutton(
            self.g3, text="Use sc3-plugins", variable=self.sc3_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_sc3_start.grid(column=2, row=4, padx=self.padx, pady=10,
                                sticky="nw")
        self.lbl_max_ch = tb.Label(
            self.g3, text="Max. Channels")
        self.lbl_max_ch.grid(column=2, row=5, padx=self.padx*2, sticky="sw")
        self.entry_max_ch = tb.Entry(
            self.g3, textvariable=self.max_ch)
        self.entry_max_ch.grid(column=2, row=6, padx=self.padx, pady=5,
                               sticky="nw")
        self.tgl_sc_info = tb.Checkbutton(
            self.g3, text="Get SC Info", variable=self.sc_info,
            style='Roundtoggle.Toolbutton')
        self.tgl_sc_info.grid(column=2, row=7, padx=self.padx, pady=10,
                              sticky="nw")
        # PERFORMANCE
        self.lbl_perf = tb.Label(
            self.g4, text="PERFORMANCE")
        self.lbl_perf.grid(column=3, row=0, padx=self.padx, pady=10,
                           sticky="nw")
        self.lbl_cpu_use = tb.Label(
            self.g4, text="CPU Usage")
        self.lbl_cpu_use.grid(column=3, row=1, padx=self.padx, sticky="sw")
        self.cpu_use_opt = tb.Combobox(
            self.g4, textvariable=self.cpu_use)
        self.cpu_use_opt["values"] = ("Low", "Medium", "High")
        self.cpu_use_opt.grid(column=3, row=2, padx=self.padx, pady=10,
                              sticky="nw")
        self.lbl_clk_lat = tb.Label(
            self.g4, text="Clock Latency")
        self.lbl_clk_lat.grid(column=3, row=3, padx=self.padx, sticky="sw")
        self.clk_lat_opt = tb.Combobox(
            self.g4, textvariable=self.clk_lat)
        self.clk_lat_opt["values"] = ("Low", "Medium", "High")
        self.clk_lat_opt.grid(column=3, row=4, padx=self.padx, pady=10,
                              sticky="nw")
        # SAMPLES
        self.lbl_samples = tb.Label(
            self.g4, text="SAMPLES")
        self.lbl_samples.grid(column=3, row=5, padx=self.padx*2, pady=10,
                              sticky="nw")
        self.lbl_smpldir = tb.Label(
            self.g4, text="Samples Directory")
        self.lbl_smpldir.grid(column=3, row=6, padx=self.padx*2, sticky="sw")
        self.entry_smpldir = tb.Entry(
            self.g4, textvariable=self.samples_dir)
        self.entry_smpldir.grid(column=3, row=7, padx=self.padx*2, pady=5,
                                sticky="nw")
        self.lbl_smplpck = tb.Label(
            self.g4, text="Samplepack #")
        self.lbl_smplpck.grid(column=3, row=8, padx=self.padx*2,
                              sticky="nw")
        self.entry_smplpck = tb.Entry(
            self.g4, textvariable=self.sample_pack)
        self.entry_smplpck.grid(column=3, row=9, padx=self.padx*2, pady=5,
                                sticky="nw")
        # APPEARENCE COLOURS
        self.a1 = tb.Frame(self.colors)
        self.a1.grid(row=0, column=0, padx=self.padx*2, sticky="nw")
        self.a2 = tb.Frame(self.colors)
        self.a2.grid(row=0, column=1, padx=self.padx*2, sticky="nw")
        self.a3 = tb.Frame(self.a2)
        self.a3.grid(row=0, column=0, sticky="nw")
        self.a4 = tb.Frame(self.a2)
        self.a4.grid(row=1, column=0, pady=self.padx, sticky="nw")
        self.a5 = tb.Frame(self.a2)
        self.a5.grid(row=1, column=1, pady=self.padx, sticky="nw")
        self.lbl_themes = tb.Label(
            self.a1, text="Theme")
        self.lbl_themes.grid(row=0, column=0, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.themes_opt = tb.Combobox(
            self.a1, textvariable=self.theme)
        self.themes_opt["values"] = self.themes
        self.themes_opt.grid(row=1, column=0, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.btn_load = tb.Button(self.a1, text="Load",
                                  command=self.load_tt)
        self.btn_load.grid(row=2, column=0, padx=self.padx,
                           pady=self.padx/2, sticky="sw")
        self.theme_name_lbl = tb.Label(
            self.a1, text="Save theme as")
        self.theme_name_lbl.grid(row=3, column=0, padx=self.padx,
                                 pady=self.padx/2, sticky="nw")
        self.theme_entry = tb.Entry(self.a1,
                                    textvariable=self.theme_name)
        self.theme_entry.grid(row=4, column=0, padx=self.padx,
                              pady=self.padx/2, sticky="nw")
        self.theme_types = ["light", "dark"]
        self.ttype = StringVar()
        if self.theme_colors['type'] == "light":
            self.ttype.set(self.theme_types[0])
        elif self.theme_colors['type'] == "dark":
            self.ttype.set(self.theme_types[1])
        self.type_l = tb.Radiobutton(self.a1,
                                     bootstyle="danger",
                                     variable=self.ttype,
                                     text="light",
                                     value=self.theme_types[0],
                                     command=self.ttype.set(self.theme_types[0]))
        self.type_l.grid(column=0, padx=self.padx, pady=self.padx, sticky="nw")
        self.type_d = tb.Radiobutton(self.a1,
                                     bootstyle="danger",
                                     variable=self.ttype,
                                     text="dark",
                                     value=self.theme_types[1],
                                     command=self.ttype.set(self.theme_types[1]))
        self.type_d.grid(column=0, padx=self.padx, pady=self.padx, sticky="nw")
        self.btn_save = tb.Button(self.a1, text="Save", command=self.save_tt)
        self.btn_save.grid(row=7, column=0, padx=self.padx,
                           pady=self.padx/2, sticky="sw")
        self.lbl_font = tb.Label(self.a1, text="Font")
        self.lbl_font.grid(row=8, column=0, padx=self.padx,
                           pady=self.padx/2, sticky="sw")
        self.entry_font = tb.Entry(
            self.a1, textvariable=self.font)
        self.entry_font.grid(row=9, column=0, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.tgl_alpha_start = tb.Checkbutton(
            self.a1, text="Transparent on Start", variable=self.alpha_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_alpha_start.grid(row=10, column=0, padx=self.padx,
                                  pady=self.padx, sticky="nw")
        # COLOR CHOICE
        self.lbl_colorlist = tb.Label(self.a3, text="Text Colors Editor")
        self.lbl_colorlist.grid(column=0, row=0,
                                padx=self.padx,
                                pady=self.padx,
                                sticky="nw")
        # background
        self.lbl_primary = tb.Label(
            self.a4, text="primary")
        self.lbl_primary.grid(column=0, row=0, padx=self.padx, sticky="nw")
        self.btn_primary = Button(self.a4, width=5,
                                  command=lambda: self.cc(self.btn_primary,
                                                          "primary"))
        self.btn_primary.config(bg=self.theme_colors["primary"])
        self.btn_primary.grid(column=1, row=0, pady=10, sticky="nw")
        # functions
        self.lbl_secondary = tb.Label(
            self.a4, text="secondary\nfunctions/numbers")
        self.lbl_secondary.grid(column=0, row=1, padx=self.padx, sticky="nw")
        self.btn_secondary = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_secondary, "secondary"))
        self.btn_secondary.config(bg=self.theme_colors["secondary"])
        self.btn_secondary.grid(column=1, row=1, pady=10, sticky="nw")
        # user_defn
        self.lbl_success = tb.Label(
            self.a4, text="success\nuser_defn/other_kws")
        self.lbl_success.grid(column=0, row=2, padx=self.padx, sticky="nw")
        self.btn_success = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_success, "success"))
        self.btn_success.config(bg=self.theme_colors["success"])
        self.btn_success.grid(column=1, row=2, pady=10, sticky="nw")
        # key_types
        self.lbl_info = tb.Label(
            self.a4, text="info\nkey_types")
        self.lbl_info.grid(column=0, row=3, padx=self.padx, sticky="nw")
        self.btn_info = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_info, "info"))
        self.btn_info.config(bg=self.theme_colors["info"])
        self.btn_info.grid(column=1, row=3, pady=10, sticky="nw")
        # players
        self.lbl_danger = tb.Label(
            self.a4, text="danger\nplayers")
        self.lbl_danger.grid(column=0, row=4, padx=self.padx, sticky="nw")
        self.btn_danger = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_danger, "danger"))
        self.btn_danger.config(bg=self.theme_colors["danger"])
        self.btn_danger.grid(column=1, row=4, pady=10, sticky="nw")
        # players
        self.lbl_warning = tb.Label(
            self.a4, text="warning\nstrings/arrow")
        self.lbl_warning.grid(column=0, row=5, padx=self.padx, sticky="nw")
        self.btn_warning = Button(self.a4, width=5,
                                  command=lambda: self.cc(self.btn_warning,
                                                          "warning"))
        self.btn_warning.config(bg=self.theme_colors["warning"])
        self.btn_warning.grid(column=1, row=5, pady=10, sticky="nw")
        # dollar
        self.lbl_light = tb.Label(
            self.a4, text="light\ncomments")
        self.lbl_light.grid(column=0, row=6, padx=self.padx, sticky="nw")
        self.btn_light = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_light, "light"))
        self.btn_light.config(bg=self.theme_colors["light"])
        self.btn_light.grid(column=1, row=6, pady=10, sticky="nw")
        # dark
        self.lbl_dark = tb.Label(self.a4, text="dark")
        self.lbl_dark.grid(column=0, row=7, padx=self.padx, sticky="nw")
        self.btn_dark = Button(self.a4, width=5,
                               command=lambda: self.cc(self.btn_dark,
                                                       "dark"))
        self.btn_dark.config(bg=self.theme_colors["dark"])
        self.btn_dark.grid(column=1, row=7, pady=10, sticky="nw")
        # bg
        self.lbl_bg = tb.Label(self.a5, text="bg\nbackground")
        self.lbl_bg.grid(column=0, row=0, padx=self.padx, sticky="nw")
        self.btn_bg = Button(self.a5, width=5,
                             command=lambda: self.cc(self.btn_bg, "bg"))
        self.btn_bg.config(bg=self.theme_colors["bg"])
        self.btn_bg.grid(column=1, row=0, pady=10, sticky="nw")
        # plaintext
        self.lbl_fg = tb.Label(
            self.a5, text="fg\nplaintext")
        self.lbl_fg.grid(column=0,
                         row=1,
                         padx=self.padx,
                         sticky="nw")
        self.btn_fg = Button(self.a5, width=5,
                             command=lambda: self.cc(self.btn_fg, "fg"))
        self.btn_fg.config(bg=self.theme_colors["fg"])
        self.btn_fg.grid(column=1, row=1, pady=10, sticky="nw")
        # prompt_fg
        self.lbl_selectfg = tb.Label(self.a5, text="selectfg\nprompt_fg")
        self.lbl_selectfg.grid(column=0,
                               row=2,
                               padx=self.padx,
                               sticky="nw")
        self.btn_selectfg = Button(self.a5, width=5,
                                   command=lambda: self.cc(self.btn_selectfg,
                                                           "selectfg"))
        self.btn_selectfg.config(bg=self.theme_colors["selectfg"])
        self.btn_selectfg.grid(column=1, row=2, pady=10, sticky="nw")
        # prompt_bg
        self.lbl_selectbg = tb.Label(
            self.a5, text="selectbg\nprompt_bg")
        self.lbl_selectbg.grid(column=0, row=3, padx=self.padx, sticky="nw")
        self.btn_selectbg = Button(self.a5, width=5,
                                   command=lambda: self.cc(self.btn_selectbg,
                                                           "selectbg"))
        self.btn_selectbg.config(bg=self.theme_colors["selectbg"])
        self.btn_selectbg.grid(column=1, row=3, pady=10, sticky="nw")
        # console_text
        self.lbl_inputfg = tb.Label(
            self.a5, text="inputfg\nconsole_text")
        self.lbl_inputfg.grid(column=0, row=4, padx=self.padx, sticky="nw")
        self.btn_inputfg = Button(self.a5, width=5,
                                  command=lambda: self.cc(self.btn_inputfg,
                                                          "inputfg"))
        self.btn_inputfg.config(bg=self.theme_colors["inputfg"])
        self.btn_inputfg.grid(column=1, row=4, pady=10, sticky="nw")
        # console_bg
        self.lbl_inputbg = tb.Label(self.a5, text="inputbg\nconsole_bg")
        self.lbl_inputbg.grid(column=0, row=5, padx=self.padx, sticky="nw")
        self.btn_inputbg = Button(self.a5, width=5,
                                  command=lambda: self.cc(self.btn_inputbg,
                                                          "inputbg"))
        self.btn_inputbg.config(bg=self.theme_colors["inputbg"])
        self.btn_inputbg.grid(column=1, row=5, pady=10, sticky="nw")
        # border
        self.lbl_border = tb.Label(self.a5, text="border")
        self.lbl_border.grid(column=0, row=6, padx=self.padx, sticky="nw")
        self.btn_border = Button(self.a5, width=5,
                                 command=lambda: self.cc(self.btn_border,
                                                         "border"))
        self.btn_border.config(bg=self.theme_colors["border"])
        self.btn_border.grid(column=1, row=6, pady=10, sticky="nw")
        # active
        self.lbl_active = tb.Label(self.a5, text="active")
        self.lbl_active.grid(column=0, row=7, padx=self.padx, sticky="nw")
        self.btn_active = Button(self.a5, width=5,
                                 command=lambda: self.cc(self.btn_active,
                                                         "active"))
        self.btn_active.config(bg=self.theme_colors["active"])
        self.btn_active.grid(column=1, row=7, pady=10, sticky="nw")

    def load_tt(self):
        self.theme_name = self.themes_opt.get()
        self.theme_entry.delete(0, END)
        self.theme_entry.insert(0, self.theme_name)
        with open(FOXDOT_EDITOR_THEMES, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            # Text area colours
            # ------------------
            for item in json_object["themes"]:
                if self.theme_name in item:
                    self.btn_primary.config(
                        bg=item[self.theme_name]["colors"]["primary"])
                    self.theme_colors["primary"] = item[self.theme_name]["colors"]["primary"]
                    self.btn_secondary.config(
                        bg=item[self.theme_name]["colors"]["secondary"])
                    self.theme_colors["secondary"] = item[self.theme_name]["colors"]["secondary"]
                    self.btn_success.config(
                        bg=item[self.theme_name]["colors"]["success"])
                    self.theme_colors["success"] = item[self.theme_name]["colors"]["success"]
                    self.btn_info.config(
                        bg=item[self.theme_name]["colors"]["info"])
                    self.theme_colors["info"] = item[self.theme_name]["colors"]["info"]
                    self.btn_warning.config(
                        bg=item[self.theme_name]["colors"]["warning"])
                    self.theme_colors["warning"] = item[self.theme_name]["colors"]["warning"]
                    self.btn_success.config(
                        bg=item[self.theme_name]["colors"]["success"])
                    self.theme_colors["success"] = item[self.theme_name]["colors"]["success"]
                    self.btn_dark.config(
                        bg=item[self.theme_name]["colors"]["dark"])
                    self.theme_colors["dark"] = item[self.theme_name]["colors"]["dark"]
                    self.btn_bg.config(
                        bg=item[self.theme_name]["colors"]["bg"])
                    self.theme_colors["bg"] = item[self.theme_name]["colors"]["bg"]
                    self.btn_fg.config(
                        bg=item[self.theme_name]["colors"]["fg"])
                    self.theme_colors["fg"] = item[self.theme_name]["colors"]["fg"]
                    # Prompt colours
                    # ------------------
                    self.btn_selectfg.config(
                        bg=item[self.theme_name]["colors"]["selectfg"])
                    self.theme_colors["selectfg"] = item[self.theme_name]["colors"]["selectfg"]
                    self.btn_selectbg.config(
                        bg=item[self.theme_name]["colors"]["selectbg"])
                    self.theme_colors["selectbg"] = item[self.theme_name]["colors"]["selectbg"]
                    # Console area colours
                    # ------------------
                    self.btn_inputfg.config(
                        bg=item[self.theme_name]["colors"]["inputfg"])
                    self.theme_colors["inputfg"] = item[self.theme_name]["colors"]["inputfg"]
                    self.btn_inputbg.config(
                        bg=item[self.theme_name]["colors"]["inputbg"])
                    self.theme_colors["inputbg"] = item[self.theme_name]["colors"]["inputbg"]
                    # ------------------
                    self.btn_border.config(
                        bg=item[self.theme_name]["colors"]["border"])
                    self.theme_colors["border"] = item[self.theme_name]["colors"]["border"]
                    self.btn_active.config(
                        bg=item[self.theme_name]["colors"]["active"])
                    self.theme_colors["active"] = item[self.theme_name]["colors"]["active"]
                    self.theme_type = item[self.theme_name]["type"]
        if self.theme_type == "light":
            self.ttype.set(self.theme_types[0])
        elif self.theme_type == "dark":
            self.ttype.set(self.theme_types[1])

    def save_tt(self):
        # Colors
        # ------------------
        self.theme_name = self.theme_entry.get()
        with open(FOXDOT_EDITOR_THEMES, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            # Text area colours
            # ------------------
            for item in json_object["themes"]:
                if self.theme_name in item:
                    item[self.theme_name]["colors"]["primary"] = self.theme_colors.get("primary")
                    item[self.theme_name]["colors"]["secondary"] = self.theme_colors.get("secondary")
                    item[self.theme_name]["colors"]["success"] = self.theme_colors.get("success")
                    item[self.theme_name]["colors"]["info"] = self.theme_colors.get("info")
                    item[self.theme_name]["colors"]["warning"] = self.theme_colors.get("warning")
                    item[self.theme_name]["colors"]["danger"] = self.theme_colors.get("danger")
                    item[self.theme_name]["colors"]["light"] = self.theme_colors.get("light")
                    item[self.theme_name]["colors"]["dark"] = self.theme_colors.get("dark")
                    item[self.theme_name]["colors"]["bg"] = self.theme_colors.get("bg")
                    item[self.theme_name]["colors"]["fg"] = self.theme_colors.get("fg")
                    item[self.theme_name]["colors"]["selectbg"] = self.theme_colors.get("selectbg")
                    item[self.theme_name]["colors"]["selectfg"] = self.theme_colors.get("selectfg")
                    item[self.theme_name]["colors"]["border"] = self.theme_colors.get("border")
                    item[self.theme_name]["colors"]["inputfg"] = self.theme_colors.get("inputfg")
                    item[self.theme_name]["colors"]["inputbg"] = self.theme_colors.get("inputbg")
                    item[self.theme_name]["colors"]["active"] = self.theme_colors.get("active")
                    item[self.theme_name]["type"] = self.ttype.get()
            if self.theme_name not in self.themes:
                new_id = len(json_object["themes"])
                json_object["themes"].append({self.theme_name: {"type": "", "colors": {}}})
                json_object["themes"][new_id][self.theme_name]["colors"]["primary"] = self.theme_colors.get("primary")
                json_object["themes"][new_id][self.theme_name]["colors"]["secondary"] = self.theme_colors.get("secondary")
                json_object["themes"][new_id][self.theme_name]["colors"]["success"] = self.theme_colors.get("success")
                json_object["themes"][new_id][self.theme_name]["colors"]["info"] = self.theme_colors.get("info")
                json_object["themes"][new_id][self.theme_name]["colors"]["warning"] = self.theme_colors.get("warning")
                json_object["themes"][new_id][self.theme_name]["colors"]["danger"] = self.theme_colors.get("danger")
                json_object["themes"][new_id][self.theme_name]["colors"]["light"] = self.theme_colors.get("light")
                json_object["themes"][new_id][self.theme_name]["colors"]["dark"] = self.theme_colors.get("dark")
                json_object["themes"][new_id][self.theme_name]["colors"]["bg"] = self.theme_colors.get("bg")
                json_object["themes"][new_id][self.theme_name]["colors"]["fg"] = self.theme_colors.get("fg")
                json_object["themes"][new_id][self.theme_name]["colors"]["selectfg"] = self.theme_colors.get("selectfg")
                json_object["themes"][new_id][self.theme_name]["colors"]["selectbg"] = self.theme_colors.get("selectbg")
                json_object["themes"][new_id][self.theme_name]["colors"]["border"] = self.theme_colors.get("border")
                json_object["themes"][new_id][self.theme_name]["colors"]["inputfg"] = self.theme_colors.get("inputfg")
                json_object["themes"][new_id][self.theme_name]["colors"]["inputbg"] = self.theme_colors.get("inputbg")
                json_object["themes"][new_id][self.theme_name]["colors"]["active"] = self.theme_colors.get("active")
                json_object["themes"][new_id][self.theme_name]["type"] = self.ttype.get()
        openfile.close()
        with open(FOXDOT_EDITOR_THEMES, 'w') as newfile:
            json.dump(json_object, newfile, indent=6)
            print("Theme saved.")
            newfile.close()

    def cc(self, button, key):
        color = self.theme_colors.get(key)
        self.cchooser = ColorChooserDialog(initialcolor=color)
        self.stop.iconify()
        self.cchooser.show()
        self.stop.deiconify()
        if not self.cchooser.result:
            pass
        else:
            colors = self.cchooser.result
            color = colors.hex
            self.theme_colors[key] = color
            button.config(bg=color)

    def convert2number(self, selection, option):
        if selection == "Low":
            if option == 0:
                self.cpu_use.set("0")
            if option == 1:
                self.clk_lat.set("0")
        elif selection == "Medium":
            if option == 0:
                self.cpu_use.set("1")
            if option == 1:
                self.clk_lat.set("1")
        elif selection == "High":
            if option == 0:
                self.cpu_use.set("2")
            if option == 1:
                self.clk_lat.set("2")

    def convert2str(self, variable):
        if variable == 0:
            return "Low"
        elif variable == 1:
            return "Medium"
        elif variable == 2:
            return "High"

    def start(self):
        self.stop.mainloop()

    def save_and_close(self, event=None):
        """ Asks the user if they want to save changes """
        answer = tkMessageBox.askyesno("Save changes",
                                       "Do you want to save your changes?",
                                       parent=self.stop)
        self.stop.lift(aboveThis=None)
        if answer:
            self.save_changes()
        else:
            pass
        self.stop.destroy()

    def save_changes(self):
        self.text_settings = self.textbox.get("1.0", "end-1c")
        if self.text_settings != self.text:
            try:
                self.settings.clear()
                self.settings = json.loads(self.text_settings)
            except Exception:
                print("Can not convert text to json file. Please check your changes in this file!")
        else:
            self.settings.clear()
            self.settings['ADDRESS'] = self.address.get()
            self.settings['PORT'] = int(self.port.get())
            self.settings['PORT2'] = int(self.port2.get())
            self.settings['FONT'] = self.font.get()
            self.settings['SUPERCOLLIDER'] = self.sc_path.get()
            self.settings['BOOT_ON_STARTUP'] = self.sc_start.get()
            self.settings['SC3_PLUGINS'] = self.sc3_start.get()
            self.settings['MAX_CHANNELS'] = int(self.max_ch.get())
            self.settings['SAMPLES_DIR'] = self.samples_dir.get()
            self.settings['SAMPLES_PACK_NUMBER'] = int(self.sample_pack.get())
            self.settings['GET_SC_INFO'] = self.sc_info.get()
            self.settings['USE_ALPHA'] = self.use_alpha.get()
            self.settings['ALPHA_VALUE'] = float(self.alpha_val.get())
            self.settings['MENU_ON_STARTUP'] = self.menu_start.get()
            self.settings['CONSOLE_ON_STARTUP'] = self.console_start.get()
            self.settings['LINENUMBERS_ON_STARTUP'] = self.linenumbers_start.get()
            self.settings['TREEVIEW_ON_STARTUP'] = self.treeview_start.get()
            self.settings['MIDIBAR_ON_STARTUP'] = self.midibar_start.get()
            self.settings['TRANSPARENT_ON_STARTUP'] = self.alpha_start.get()
            self.settings['RECOVER_WORK'] = self.recover_work.get()
            self.settings['CHECK_FOR_UPDATE'] = self.check_update.get()
            self.settings['LINE_NUMBER_MARKER_OFFSET'] = int(self.linenumber_offset.get())
            self.settings['AUTO_COMPLETE_BRACKETS'] = self.brackets_auto.get()
            self.convert2number(self.cpu_use.get(), 0)
            self.settings['CPU_USAGE'] = int(self.cpu_use.get())
            self.convert2number(self.clk_lat.get(), 1)
            self.settings['CLOCK_LATENCY'] = int(self.clk_lat.get())
            self.settings['FORWARD_ADDRESS'] = self.fwd_address.get()
            self.settings['FORWARD_PORT'] = int(self.fwd_port.get())
            self.settings['COLOR_THEME'] = self.theme.get()
        settings_file = open(self.conf_json, "w")
        json.dump(self.settings, settings_file, indent=6)
        settings_file.close()
        msg = "A restart of FoxDot is required for the changes to take effect"
        tkMessageBox.showwarning(parent=self.stop, title="Just a heads up", message=msg)
        self.stop.destroy()
        return
