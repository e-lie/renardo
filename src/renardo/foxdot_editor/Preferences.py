import tomli

from renardo.foxdot_editor.tkimport import *
from renardo.settings_manager import settings
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
            self.stop.iconbitmap(settings.get("foxdot_editor.ICON"))
        except TclError:
            # Use .gif if necessary
            self.stop.tk.call('wm',
                              'iconphoto',
                              self.stop._w,
                              PhotoImage(file=settings.get("foxdot_editor.ICON_GIF")))
        self.text_themes = ()
        for file_name in [file for file in os.listdir(settings.get("foxdot_editor.THEMES_PATH")) if file.endswith('.json')]:
            theme = os.path.splitext(file_name)[0]
            self.text_themes = self.text_themes + (theme,)
        self.settings = {}
        self.conf_toml = settings.get_path("PUBLIC_SETTINGS_FILE")
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
            with open(self.conf_toml) as f:
                self.text = f.read().rstrip()
            self.textbox.insert(INSERT, self.text)
        except FileNotFoundError:
            print(f"{settings.get_path('PUBLIC_SETTINGS_FILE')} file not found")
        # Add binds?
        self.textbox.bind()

        self.theme_name = ""

        # Settings values
        self.menu_start = BooleanVar()
        self.menu_start.set(settings.get("foxdot_editor.MENU_ON_STARTUP"))
        self.linenumbers_start = BooleanVar()
        self.linenumbers_start.set(settings.get("foxdot_editor.LINENUMBERS_ON_STARTUP"))
        self.console_start = BooleanVar()
        self.console_start.set(settings.get("foxdot_editor.CONSOLE_ON_STARTUP"))
        self.treeview_start = BooleanVar()
        self.treeview_start.set(settings.get("foxdot_editor.TREEVIEW_ON_STARTUP"))
        self.recover_work = BooleanVar()
        self.recover_work.set(settings.get("foxdot_editor.RECOVER_WORK"))
        self.check_update = BooleanVar()
        self.check_update.set(settings.get("foxdot_editor.CHECK_FOR_UPDATE"))

        # Editor
        self.linenumber_offset = StringVar()
        self.linenumber_offset.set(settings.get("foxdot_editor.LINE_NUMBER_MARKER_OFFSET"))
        self.brackets_auto = BooleanVar()
        self.brackets_auto.set(settings.get("foxdot_editor.AUTO_COMPLETE_BRACKETS"))

        # Sample values
        self.sample_pack = StringVar()
        self.sample_pack.set(settings.get("samples.SAMPLES_PACK_NUMBER"))

        # Connection values
        self.address = StringVar()
        self.address.set(settings.get("sc_backend.ADDRESS"))
        self.port = StringVar()
        self.port.set(settings.get("sc_backend.PORT"))
        self.port2 = StringVar()
        self.port2.set(settings.get("sc_backend.PORT2"))
        self.fwd_address = StringVar()
        self.fwd_address.set(settings.get("sc_backend.FORWARD_ADDRESS"))
        self.fwd_port = StringVar()
        self.fwd_port.set(settings.get("sc_backend.FORWARD_PORT"))

        # SuperCollider
        self.sc_start = BooleanVar()
        self.sc_start.set(settings.get("sc_backend.BOOT_SCLANG_ON_STARTUP"))
        self.sc3_start = BooleanVar()
        self.sc3_start.set(settings.get("sc_backend.SC3_PLUGINS"))
        self.max_ch = StringVar()
        self.max_ch.set(settings.get("samples.MAX_CHANNELS"))
        self.sc_info = BooleanVar()
        self.sc_info.set(settings.get("sc_backend.GET_SC_INFO"))

        # Performance
        self.cpu_use = StringVar()
        cpu_val = self.convert2str(settings.get("core.CPU_USAGE"))
        self.cpu_use.set(cpu_val)
        lat_val = self.convert2str(settings.get("core.CLOCK_LATENCY"))
        self.clk_lat = StringVar()
        self.clk_lat.set(lat_val)

        # Appearance
        # theme
        self.theme = StringVar()
        self.theme.set(settings.get("foxdot_editor.COLOR_THEME"))
        self.text_theme = StringVar()
        self.text_theme.set(settings.get("foxdot_editor.TEXT_COLORS"))
        self.font = StringVar()
        self.font.set(settings.get("foxdot_editor.FONT"))
        self.use_alpha = BooleanVar()
        self.use_alpha.set(settings.get("foxdot_editor.USE_ALPHA"))
        self.alpha_val = StringVar()
        self.alpha_val.set(settings.get("foxdot_editor.ALPHA_VALUE"))
        self.alpha_start = BooleanVar()
        self.alpha_start.set(settings.get("foxdot_editor.TRANSPARENT_ON_STARTUP"))

        # Colors
        # ------------------
        self.plaintext = colour_map['plaintext']
        self.background = colour_map['background']
        self.functions = colour_map['functions']
        self.key_types = colour_map['key_types']
        self.user_defn = colour_map['user_defn']
        self.other_kws = colour_map['other_kws']
        self.comments = colour_map['comments']
        self.numbers = colour_map['numbers']
        self.strings = colour_map['strings']
        self.dollar = colour_map['dollar']
        self.arrow = colour_map['arrow']
        self.players = colour_map['players']
        # Prompt colours
        # ------------------
        self.prompt_fg = colour_map['prompt_fg']
        self.prompt_bg = colour_map['prompt_bg']
        # Console area colours
        # ------------------
        self.console_text = colour_map['console_text']
        self.console_bg = colour_map['console_bg']
        # x distance for widgets
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
        self.tgl_recover = tb.Checkbutton(
            self.g1, text="Recover Work", variable=self.recover_work,
            style='Roundtoggle.Toolbutton')
        self.tgl_recover.grid(column=0, row=4, padx=self.padx*2, pady=10,
                              sticky="nw")
        self.tgl_update = tb.Checkbutton(
            self.g1, text="Check for Updates", variable=self.check_update,
            style='Roundtoggle.Toolbutton')
        self.tgl_update.grid(column=0, row=5, padx=self.padx*2, pady=10,
                             sticky="nw")
        # EDITOR
        self.lbl_on_start = tb.Label(
            self.g1, text="EDITOR")
        self.lbl_on_start.grid(column=0, row=6, padx=self.padx*2, pady=10,
                               sticky="nw")
        self.tgl_update = tb.Checkbutton(
            self.g1, text="Autocomplete Brackets", variable=self.brackets_auto,
            style='Roundtoggle.Toolbutton')
        self.tgl_update.grid(column=0, row=7, padx=self.padx*2, pady=10,
                             sticky="nw")
        self.lbl_line_offset = tb.Label(
            self.g1, text="Linenumber Marker Offset")
        self.lbl_line_offset.grid(column=0, row=8, padx=self.padx*2,
                                  sticky="sw")
        self.entry_linenum_offset = tb.Entry(
            self.g1, textvariable=self.linenumber_offset)
        self.entry_linenum_offset.grid(column=0, row=9, padx=self.padx*2,
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
        # settings.get("sc_backend.SUPERCOLLIDER")
        self.lbl_sc = tb.Label(
            self.g3, text="SUPERCOLLIDER")
        self.lbl_sc.grid(column=2, row=0, padx=self.padx, pady=10, sticky="nw")
        self.tgl_sc_start = tb.Checkbutton(
            self.g3, text="Boot SC on Start", variable=self.sc_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_sc_start.grid(column=2, row=1, padx=self.padx, pady=10,
                               sticky="sw")
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
        self.lbl_themes.grid(column=0, row=0, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.themes_opt = tb.Combobox(
            self.a1, textvariable=self.theme)
        self.themes_opt["values"] = ("cosmo", "flatly",
                                     "journal", "litera", "lumen", "minty",
                                     "pulse", "sandstone", "united", "yeti",
                                     "morph", "simplex", "cerulean", "solar",
                                     "superhero", "darkly", "cyborg", "vapor")
        self.themes_opt.grid(column=0, row=1, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.lbl_text_colors = tb.Label(
            self.a1, text="Text Color Theme")
        self.lbl_text_colors.grid(column=0, row=2, padx=self.padx,
                                  pady=self.padx, sticky="sw")
        self.text_colors_opt = tb.Combobox(
            self.a1, textvariable=self.text_theme)
        self.text_colors_opt["values"] = self.text_themes
        self.text_colors_opt.grid(column=0, row=3, padx=self.padx,
                                  pady=self.padx/2, sticky="nw")
        self.btn_load = tb.Button(self.a1, text="Load",
                                  command=self.load_tt)
        self.btn_load.grid(column=0, row=4, padx=self.padx*3,
                           pady=self.padx/2, sticky="sw")
        self.btn_save = tb.Button(self.a1, text="Save", command=self.save_tt)
        self.btn_save.grid(column=0, row=4, padx=self.padx*12,
                           pady=self.padx/2, sticky="sw")
        self.lbl_font = tb.Label(
            self.a1, text="Font")
        self.lbl_font.grid(column=0, row=5, padx=self.padx,
                           pady=self.padx/2, sticky="sw")
        self.entry_font = tb.Entry(
            self.a1, textvariable=self.font)
        self.entry_font.grid(column=0, row=6, padx=self.padx, pady=self.padx/2,
                             sticky="nw")
        self.tgl_use_alpha = tb.Checkbutton(
            self.a1, text="Use Alpha", variable=self.use_alpha,
            style='Roundtoggle.Toolbutton')
        self.tgl_use_alpha.grid(column=0, row=7, padx=self.padx,
                                pady=self.padx, sticky="nw")
        self.tgl_alpha_start = tb.Checkbutton(
            self.a1, text="Transparent on Start", variable=self.alpha_start,
            style='Roundtoggle.Toolbutton')
        self.tgl_alpha_start.grid(column=0, row=8, padx=self.padx,
                                  pady=self.padx, sticky="nw")
        # COLOR CHOICE
        self.lbl_colorlist = tb.Label(self.a3, text="Text Colors Editor")
        self.lbl_colorlist.grid(column=0, row=0,
                                padx=self.padx,
                                pady=self.padx,
                                sticky="nw")
        # plaintext
        self.lbl_plaintext = tb.Label(
            self.a4, text="plaintext")
        self.lbl_plaintext.grid(column=0, row=0, padx=self.padx, sticky="nw")
        self.btn_plaintext = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_plaintext, self.plaintext))
        self.btn_plaintext.config(bg=self.plaintext)
        self.btn_plaintext.grid(column=1, row=0, sticky="nw")
        # background
        self.lbl_background = tb.Label(
            self.a4, text="background")
        self.lbl_background.grid(column=0, row=2, padx=self.padx, sticky="nw")
        self.btn_background = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_background, self.background))
        self.btn_background.config(bg=self.background)
        self.btn_background.grid(column=1, row=2, sticky="nw")
        # functions
        self.lbl_functions = tb.Label(
            self.a4, text="functions")
        self.lbl_functions.grid(column=0, row=3, padx=self.padx, sticky="nw")
        self.btn_functions = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_functions, self.functions))
        self.btn_functions.config(bg=self.functions)
        self.btn_functions.grid(column=1, row=3, sticky="nw")
        # key_types
        self.lbl_key_types = tb.Label(
            self.a4, text="key_types")
        self.lbl_key_types.grid(column=0, row=4, padx=self.padx, sticky="nw")
        self.btn_key_types = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_key_types, self.key_types))
        self.btn_key_types.config(bg=self.key_types)
        self.btn_key_types.grid(column=1, row=4, sticky="nw")
        # user_defn
        self.lbl_user_defn = tb.Label(
            self.a4, text="user_defn")
        self.lbl_user_defn.grid(column=0, row=5, padx=self.padx, sticky="nw")
        self.btn_user_defn = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_user_defn, self.user_defn))
        self.btn_user_defn.config(bg=self.user_defn)
        self.btn_user_defn.grid(column=1, row=5, sticky="nw")
        # other_kws
        self.lbl_other_kws = tb.Label(
            self.a4, text="other_kws")
        self.lbl_other_kws.grid(column=0, row=6, padx=self.padx, sticky="nw")
        self.btn_other_kws = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_other_kws, self.other_kws))
        self.btn_other_kws.config(bg=self.other_kws)
        self.btn_other_kws.grid(column=1, row=6, sticky="nw")
        # comments
        self.lbl_comments = tb.Label(
            self.a4, text="comments")
        self.lbl_comments.grid(column=0, row=7, padx=self.padx, sticky="nw")
        self.btn_comments = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_comments, self.comments))
        self.btn_comments.config(bg=self.comments)
        self.btn_comments.grid(column=1, row=7, sticky="nw")
        # numbers
        self.lbl_numbers = tb.Label(
            self.a4, text="numbers")
        self.lbl_numbers.grid(column=0, row=8, padx=self.padx, sticky="nw")
        self.btn_numbers = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_numbers, self.numbers))
        self.btn_numbers.config(bg=self.numbers)
        self.btn_numbers.grid(column=1, row=8, sticky="nw")
        # strings
        self.lbl_strings = tb.Label(
            self.a4, text="strings")
        self.lbl_strings.grid(column=0, row=9, padx=self.padx, sticky="nw")
        self.btn_strings = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_strings, self.strings))
        self.btn_strings.config(bg=self.strings)
        self.btn_strings.grid(column=1, row=9, sticky="nw")
        # dollar
        self.lbl_dollar = tb.Label(
            self.a4, text="dollar")
        self.lbl_dollar.grid(column=0, row=10, padx=self.padx, sticky="nw")
        self.btn_dollar = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_dollar, self.dollar))
        self.btn_dollar.config(bg=self.dollar)
        self.btn_dollar.grid(column=1, row=10, sticky="nw")
        # arrow
        self.lbl_arrow = tb.Label(
            self.a4, text="arrow")
        self.lbl_arrow.grid(column=0, row=11, padx=self.padx, sticky="nw")
        self.btn_arrow = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_arrow, self.arrow))
        self.btn_arrow.config(bg=self.arrow)
        self.btn_arrow.grid(column=1, row=11, sticky="nw")
        # players
        self.lbl_players = tb.Label(
            self.a4, text="players")
        self.lbl_players.grid(column=0, row=12, padx=self.padx, sticky="nw")
        self.btn_players = Button(
            self.a4, width=5,
            command=lambda: self.cc(self.btn_players, self.players))
        self.btn_players.config(bg=self.players)
        self.btn_players.grid(column=1, row=12, sticky="nw")
        # prompt_fg
        self.lbl_prompt_fg = tb.Label(
            self.a5, text="prompt_fg")
        self.lbl_prompt_fg.grid(column=0, row=0, padx=self.padx, sticky="nw")
        self.btn_prompt_fg = Button(
            self.a5, width=5,
            command=lambda: self.cc(self.btn_prompt_fg, self.prompt_fg))
        self.btn_prompt_fg.config(bg=self.prompt_fg)
        self.btn_prompt_fg.grid(column=1, row=0, sticky="nw")
        # prompt_bg
        self.lbl_prompt_bg = tb.Label(
            self.a5, text="prompt_bg")
        self.lbl_prompt_bg.grid(column=0, row=1, padx=self.padx, sticky="nw")
        self.btn_prompt_bg = Button(
            self.a5, width=5,
            command=lambda: self.cc(self.btn_prompt_bg, self.prompt_bg))
        self.btn_prompt_bg.config(bg=self.prompt_bg)
        self.btn_prompt_bg.grid(column=1, row=1, sticky="nw")
        # console_text
        self.lbl_console_text = tb.Label(
            self.a5, text="console_text")
        self.lbl_console_text.grid(column=0, row=2, padx=self.padx, sticky="nw")
        self.btn_console_text = Button(
            self.a5, width=5,
            command=lambda: self.cc(self.btn_console_text, self.console_text))
        self.btn_console_text.config(bg=self.console_text)
        self.btn_console_text.grid(column=1, row=2, sticky="nw")
        # console_bg
        self.lbl_console_bg = tb.Label(
            self.a5, text="console_bg")
        self.lbl_console_bg.grid(column=0, row=3, padx=self.padx, sticky="nw")
        self.btn_console_bg = Button(
            self.a5, width=5,
            command=lambda: self.cc(self.btn_console_bg, self.console_bg))
        self.btn_console_bg.config(bg=self.console_bg)
        self.btn_console_bg.grid(column=1, row=3, sticky="nw")

    def load_tt(self):
        self.theme_name = self.text_colors_opt.get()
        try:
            file = settings.get("foxdot_editor.THEMES_PATH") + '/' + self.theme_name + '.json'
            # Opening JSON file
            with open(file, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)
                self.btn_plaintext.config(
                    bg=json_object[self.theme_name]['plaintext'])
                self.btn_background.config(
                    bg=json_object[self.theme_name]['background'])
                self.btn_functions.config(
                    bg=json_object[self.theme_name]['functions'])
                self.btn_key_types.config(
                    bg=json_object[self.theme_name]['key_types'])
                self.btn_user_defn.config(
                    bg=json_object[self.theme_name]['user_defn'])
                self.btn_other_kws.config(
                    bg=json_object[self.theme_name]['other_kws'])
                self.btn_comments.config(
                    bg=json_object[self.theme_name]['comments'])
                self.btn_numbers.config(
                    bg=json_object[self.theme_name]['numbers'])
                self.btn_strings.config(
                    bg=json_object[self.theme_name]['strings'])
                self.btn_dollar.config(
                    bg=json_object[self.theme_name]['dollar'])
                self.btn_arrow.config(
                    bg=json_object[self.theme_name]['arrow'])
                self.btn_players.config(
                    bg=json_object[self.theme_name]['players'])
                self.btn_prompt_fg.config(
                    bg=json_object[self.theme_name]['prompt_fg'])
                self.btn_prompt_bg.config(
                    bg=json_object[self.theme_name]['prompt_bg'])
                self.btn_console_text.config(
                    bg=json_object[self.theme_name]['console_text'])
                self.btn_console_bg.config(
                    bg=json_object[self.theme_name]['console_bg'])
        except FileNotFoundError:
            pass

    def save_tt(self):
        # Colors
        # ------------------
        new_theme = {self.theme_name: {}}
        new_theme[self.theme_name]['plaintext'] = self.plaintext
        new_theme[self.theme_name]['background'] = self.background
        new_theme[self.theme_name]['functions'] = self.functions
        new_theme[self.theme_name]['key_types'] = self.key_types
        new_theme[self.theme_name]['user_defn'] = self.user_defn
        new_theme[self.theme_name]['other_kws'] = self.other_kws
        new_theme[self.theme_name]['comments'] = self.comments
        new_theme[self.theme_name]['numbers'] = self.numbers
        new_theme[self.theme_name]['strings'] = self.strings
        new_theme[self.theme_name]['dollar'] = self.dollar
        new_theme[self.theme_name]['arrow'] = self.arrow
        new_theme[self.theme_name]['players'] = self.players
        # Prompt colours
        # ------------------
        new_theme[self.theme_name]['prompt_fg'] = self.prompt_fg
        new_theme[self.theme_name]['prompt_bg'] = self.prompt_bg
        # Console area colours
        # ------------------
        new_theme[self.theme_name]['console_text'] = self.console_text
        new_theme[self.theme_name]['console_bg'] = self.console_bg
        self.stop.iconify()
        self.filename = tkFileDialog.asksaveasfilename(
            filetypes=[("JSON files", ".json")],
            initialdir=settings.get("foxdot_editor.THEMES_PATH") + '/',
            defaultextension=".json")
        if self.filename:
            new_file = open(self.filename, "w")
            json.dump(new_theme, new_file, indent=6)
            new_file.close()
            print("Theme saved.")
        else:
            pass
        self.stop.deiconify()

    def cc(self, button, color):
        self.cchooser = ColorChooserDialog(initialcolor=color)
        self.stop.iconify()
        self.cchooser.show()
        self.stop.deiconify()
        if not self.cchooser.result:
            pass
        else:
            colors = self.cchooser.result
            color = colors.hex
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
            # TODO reimplement save changes using the new central settings manager
            return self.save_changes()
        else:
            pass
        return self.stop.destroy()
        pass

    def save_changes(self):
        self.text_settings = self.textbox.get("1.0", "end-1c")
        if self.text_settings != self.text:
            #try:
                toml_bytes = self.text_settings.encode("utf-8")
                config_dict = tomli.loads(self.text_settings)
                settings.set_from_dict(config_dict)
                settings.save_to_file()
            #except Exception:
            #    print("Can not convert text to TOML file. Please check your changes in this file!")
        else:
            settings.set("sc_backend.ADDRESS", self.address.get())
            settings.set("sc_backend.PORT", int(self.port.get()))
            settings.set("sc_backend.PORT2", int(self.port2.get()))
            settings.set("foxdot_editor.FONT", self.font.get())
            settings.set("core.BOOT_SCLANG_ON_STARTUP", self.sc_start.get())
            settings.set("sc_backend.SC3_PLUGINS", self.sc3_start.get())
            settings.set("samples.MAX_CHANNELS", int(self.max_ch.get()))
            settings.set("samples.SAMPLES_PACK_NUMBER", int(self.sample_pack.get()))
            settings.set("sc_backend.GET_SC_INFO", self.sc_info.get())
            settings.set("foxdot_editor.USE_ALPHA", self.use_alpha.get())
            settings.set("foxdot_editor.ALPHA_VALUE", float(self.alpha_val.get()))
            settings.set("foxdot_editor.MENU_ON_STARTUP", self.menu_start.get())
            settings.set("foxdot_editor.CONSOLE_ON_STARTUP", self.console_start.get())
            settings.set("foxdot_editor.LINENUMBERS_ON_STARTUP", self.linenumbers_start.get())
            settings.set("foxdot_editor.TREEVIEW_ON_STARTUP", self.treeview_start.get())
            settings.set("foxdot_editor.TRANSPARENT_ON_STARTUP", self.alpha_start.get())
            settings.set("foxdot_editor.RECOVER_WORK", self.recover_work.get())
            settings.set("foxdot_editor.CHECK_FOR_UPDATE", self.check_update.get())
            settings.set("foxdot_editor.LINE_NUMBER_MARKER_OFFSET", int(self.linenumber_offset.get()))
            settings.set("foxdot_editor.AUTO_COMPLETE_BRACKETS", self.brackets_auto.get())
            self.convert2number(self.cpu_use.get(), 0)
            settings.set("core.CPU_USAGE", int(self.cpu_use.get()))
            self.convert2number(self.clk_lat.get(), 1)
            settings.set("core.CLOCK_LATENCY", int(self.clk_lat.get()))
            settings.set("sc_backend.FORWARD_ADDRESS", self.fwd_address.get())
            settings.set("sc_backend.FORWARD_PORT", int(self.fwd_port.get()))
            settings.set("foxdot_editor.COLOR_THEME", self.theme.get())
            settings.set("foxdot_editor.TEXT_COLORS", self.text_theme.get())
        #settings_file = open(self.conf_json, "w")
        #json.dump(self.settings, settings_file, indent=6)
        #settings_file.close()
        settings.save_to_file()
        msg = "A restart of Renardo is required for the changes to take effect"
        tkMessageBox.showwarning(parent=self.stop, title="Just a heads up", message=msg)
        self.stop.destroy()
        return
