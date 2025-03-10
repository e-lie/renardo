
from FoxDotEditor.tkimport import *
from renardo_lib.Settings import *
from .Format import *
try:
    import tkMessageBox
except ImportError:
    from tkinter import messagebox as tkMessageBox
try:
    from rtmidi import *
except ImportError:
    pass
import os.path
import time


class MidiMapper:
    def __init__(self):
        self.w = 850
        self.h = 600
        self.mm_top = tb.Toplevel(topmost=True)
        self.mm_top.title("Midi Mapper")
        self.mm_top.protocol("WM_DELETE_WINDOW", self.save_and_close)
        self.mm_top.minsize(400, 300)
        self.mm_top.resizable(True, True)
        self.mm_top.geometry(str(self.w)+"x"+str(self.h))
        self.item_colors = ["#000000", "#ff1900", "#ff8800", "#057dff",
                            "#00ff2e", "#00ddff", "#9800ff",
                            "#ff00e4", "#ff008c", "#d400ff"]
        self.style = ttk.Style()
        self.tgl_edit = False
        self.tgl_conn = False
        self.msg = [0, 0, 0]
        self.midimap_name = "No Midi Map Loaded"
        try:
            # Use .ico file by default
            self.mm_top.iconbitmap(FOXDOT_ICON)
        except TclError:
            # Use .gif if necessary
            self.mm_top.tk.call('wm',
                                'iconphoto',
                                self.mm_top._w,
                                PhotoImage(file=FOXDOT_ICON_GIF))
        # Row 1
        self.mm_title = tb.Label(self.mm_top,
                                 text="MIDI MAPPER >> Map Your Midi Devices, Load and Save It. Choose your device in Menu >> Tools >> Midi Devices",
                                 style="primary.Inverse.TLabel",
                                 justify="center")
        self.mm_title.grid(row=0,
                           column=0,
                           columnspan=5,
                           padx=20,
                           pady=15,
                           sticky="WE")
        # Row 2
        self.device_lbl = tb.Label(self.mm_top,
                                   text="MIDI DEVICE",
                                   width=30)
        self.device_lbl.grid(row=1,
                             column=0,
                             columnspan=2,
                             pady=15,
                             padx=20,
                             sticky="W")
        self.device_chkbtn = tb.Button(self.mm_top,
                                       text="Check Devices",
                                       width=15,
                                       command=self.check_devices)
        self.device_chkbtn.grid(row=1,
                                column=2,
                                pady=15,
                                padx=5,
                                sticky="E")
        self.device_chkbox = tb.Combobox(self.mm_top, width=20)
        self.device_chkbox.set("No Devices Available")
        self.device_chkbox.grid(row=1,
                                column=3,
                                pady=15,
                                padx=5,
                                sticky="W")
        self.device_connbtn = tb.Button(self.mm_top,
                                        text="Connect It!",
                                        width=15,
                                        command=self.conn_device)
        self.device_connbtn.grid(row=1,
                                 column=4,
                                 pady=15,
                                 padx=5,
                                 sticky="W")
        # Row 3
        self.device_state = tb.Label(self.mm_top,
                                     text="No Device Connected",
                                     width=30)
        self.device_state.grid(row=2,
                               column=0,
                               columnspan=2,
                               padx=20,
                               sticky="W")
        self.txt_output = tb.Label(self.mm_top,
                                   text="No Midi Output Yet!")
        self.txt_output.grid(row=2,
                             column=2,
                             columnspan=3,
                             padx=20,
                             sticky="W")
        self.file_lbl = tb.Label(self.mm_top,
                                 text="MIDI MAP",
                                 width=30)
        self.file_lbl.grid(row=3,
                           column=0,
                           columnspan=2,
                           padx=20,
                           pady=15,
                           sticky="W")
        self.file_new = tb.Button(self.mm_top,
                                  text="New Midi Map",
                                  width=15,
                                  command=self.new_file)
        self.file_new.grid(row=3,
                           column=2,
                           pady=15,
                           padx=5,
                           sticky="E")
        self.file_open = tb.Button(self.mm_top,
                                   text="Load Midi Map",
                                   width=20,
                                   command=self.load_mmf)
        self.file_open.grid(row=3,
                            column=3,
                            pady=15,
                            padx=5,
                            sticky="E")
        self.file_save = tb.Button(self.mm_top,
                                   text="Save Midi Map",
                                   width=15,
                                   command=self.save_mmf)
        self.file_save.grid(row=3,
                            column=4,
                            pady=15,
                            padx=5,
                            sticky="W")
        self.file_state = tb.Label(self.mm_top,
                                   text=self.midimap_name,
                                   width=30)
        self.file_state.grid(row=4,
                             column=0,
                             columnspan=2,
                             padx=20,
                             pady=5,
                             sticky="W")
        self.valmap_info = tb.Button(self.mm_top,
                                     text="ValMap Info",
                                     width=15,
                                     command=self.info_vmf)
        self.valmap_info.grid(row=4,
                              column=3,
                              pady=5,
                              padx=5,
                              sticky="E")
        self.valmap_gen = tb.Button(self.mm_top,
                                    text="Generate ValMap",
                                    width=15,
                                    command=self.gen_vmf)
        self.valmap_gen.grid(row=4,
                             column=4,
                             pady=5,
                             padx=5,
                             sticky="W")

        self.items_frame = tb.Frame(self.mm_top)
        self.items_frame.grid(row=5,
                              column=0,
                              columnspan=5,
                              padx=20,
                              pady=10,
                              sticky="W")
        # Elements Of Item Frame
        self.name_entry = tb.Entry(self.items_frame, width=15)
        self.name_entry.insert(0, "U0:E0")
        self.name_entry.grid(row=0,
                             column=0,
                             sticky="W")
        self.types_drpdwn = tb.Combobox(self.items_frame, width=20)
        self.types_drpdwn.set("Choose Type")
        self.types_drpdwn["values"] = ("Slider",
                                       "Knob",
                                       "Pad",
                                       "Button",
                                       "Switch",
                                       "Wheel",
                                       "XY-X",
                                       "XY-Y",
                                       "XY-Off",)
        self.types_drpdwn.grid(row=0,
                               column=1,
                               sticky="W")
        # Add CC # Dropdwn menu
        self.cc_drpdwn = tb.Combobox(self.items_frame, width=20)
        cc_values = ()
        for i in range(128):
            cc_values += (str(i),)
        self.cc_drpdwn["values"] = cc_values
        self.cc_drpdwn.grid(row=0,
                            column=2,
                            sticky="W")
        self.cc_drpdwn.set("Choose CC #")
        # Add CC # Dropdwn menu
        self.val_drpdwn = tb.Combobox(self.items_frame, width=20)
        self.val_drpdwn["values"] = ("0-127",
                                     "-64-64",
                                     "Push",
                                     "Switch",
                                     "Count")
        self.val_drpdwn.grid(row=0,
                             column=3,
                             sticky="W")
        self.val_drpdwn.set("Choose Range")
        # Add Add button
        self.add_btn = tb.Button(self.items_frame,
                                 text="Add",
                                 command=self.add_list_item)
        self.add_btn.grid(row=0,
                          column=4,
                          sticky="WE")

        self.list_frame = tb.Frame(self.items_frame)
        self.list_frame.grid(row=1,
                             column=0,
                             columnspan=5,
                             pady=15,
                             sticky="WE")
        self.list_scroll = tb.Scrollbar(self.list_frame)
        self.list_scroll.grid(row=0, column=1, sticky="NSEW")
        # Add Treeview to use as Midi Controller List
        self.items_list = tb.Treeview(self.list_frame,
                                      style='primary.Treeview',
                                      yscrollcommand=self.list_scroll.set)
        self.list_scroll.config(command=self.items_list.yview)
        # Add all colums for this list
        self.items_list['columns'] = ("Name",
                                      "Type",
                                      "CC #",
                                      "Value")
        # Add columns configuration
        self.items_list.column("#0", width=0, stretch=NO)
        self.items_list.column("Name", anchor=W, width=200)
        self.items_list.column("Type", anchor=W, width=140)
        self.items_list.column("CC #", anchor=W, width=120)
        self.items_list.column("Value", anchor=W, width=220)
        # Add heading
        self.items_list.heading("#0", text="", anchor=W)
        self.items_list.heading("Name", text="Name", anchor=W)
        self.items_list.heading("Type", text="Type", anchor=W)
        self.items_list.heading("CC #", text="CC #", anchor=W)
        self.items_list.heading("Value", text="Value", anchor=W)
        # Gather data from xml file
        self.data = []
        # Add it to list
        self.count = 0
        for record in self.data:
            self.items_list.insert(parent="",
                                   index="end",
                                   iid=self.count,
                                   text="",
                                   values=(record[0],
                                           record[1],
                                           record[2],
                                           record[3]))
            self.count += 1
        # Adding list to Frame
        self.items_list.grid(row=0,
                             column=0,
                             sticky="WE")
        # Configure row colors
        self.items_list.tag_configure('Choose Type',
                                      background=self.item_colors[0])
        self.items_list.tag_configure('Slider',
                                      background=self.item_colors[1])
        self.items_list.tag_configure('Knob',
                                      background=self.item_colors[2])
        self.items_list.tag_configure('Pad',
                                      background=self.item_colors[3])
        self.items_list.tag_configure('Button',
                                      background=self.item_colors[4])
        self.items_list.tag_configure('Switch',
                                      background=self.item_colors[5])
        self.items_list.tag_configure('Wheel',
                                      background=self.item_colors[6])
        self.items_list.tag_configure('XY-X',
                                      background=self.item_colors[7])
        self.items_list.tag_configure('XY-Y',
                                      background=self.item_colors[7])
        self.items_list.tag_configure('XY-Off',
                                      background=self.item_colors[8])
        # Add buttons
        self.edit_btn = tb.Button(self.items_frame,
                                  text="Edit",
                                  command=self.edit_list_item)
        self.edit_btn.grid(row=2,
                           column=1,
                           padx=10,
                           sticky="WE")
        self.up_btn = tb.Button(self.items_frame,
                                text="Move Up",
                                command=self.move_up_item)
        self.up_btn.grid(row=2,
                         column=2,
                         padx=10,
                         sticky="WE")
        self.dwn_btn = tb.Button(self.items_frame,
                                 text="Move Dwn",
                                 command=self.move_dwn_item)
        self.dwn_btn.grid(row=2,
                          column=3,
                          padx=10,
                          sticky="WE")
        self.del_btn = tb.Button(self.items_frame,
                                 text="Delete",
                                 command=self.del_list_item)
        self.del_btn.grid(row=2,
                          column=4,
                          padx=10,
                          sticky="WE")

    def add_list_item(self):
        self.items_list.insert(parent="",
                               index="end",
                               iid=self.count,
                               text="",
                               tags=(self.types_drpdwn.get(),),
                               values=(self.name_entry.get(),
                                       self.types_drpdwn.get(),
                                       self.cc_drpdwn.get(),
                                       self.val_drpdwn.get()))
        self.count += 1

    def del_list_item(self):
        items = self.items_list.selection()
        for record in items:
            self.items_list.delete(record)

    def edit_list_item(self):
        if not self.tgl_edit:
            selected = self.items_list.focus()
            values = self.items_list.item(selected, "values")
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, values[0])
            self.types_drpdwn.set(values[1])
            self.cc_drpdwn.set(values[2])
            self.val_drpdwn.set(values[3])
            self.edit_btn.config(text="Append")
            self.add_btn.state(["disabled"])
            self.del_btn.state(["disabled"])
            self.up_btn.state(["disabled"])
            self.dwn_btn.state(["disabled"])
            self.tgl_edit = True
        else:
            selected = self.items_list.focus()
            self.items_list.item(selected,
                                 text="",
                                 tags=(self.types_drpdwn.get(),),
                                 values=(self.name_entry.get(),
                                         self.types_drpdwn.get(),
                                         self.cc_drpdwn.get(),
                                         self.val_drpdwn.get()))
            # Clear boxes
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, "U0:E0")
            self.types_drpdwn.set("Choose Type")
            self.cc_drpdwn.set("Choose CC #")
            self.val_drpdwn.set("Choose Range")
            self.edit_btn.config(text="Edit")
            self.add_btn.state(["!disabled"])
            self.del_btn.state(["!disabled"])
            self.up_btn.state(["!disabled"])
            self.dwn_btn.state(["!disabled"])
            self.tgl_edit = False

    def move_up_item(self):
        rows = self.items_list.selection()
        for row in rows:
            self.items_list.move(row,
                                 self.items_list.parent(row),
                                 self.items_list.index(row)-1)

    def move_dwn_item(self):
        rows = self.items_list.selection()
        for row in reversed(rows):
            self.items_list.move(row,
                                 self.items_list.parent(row),
                                 self.items_list.index(row)+1)

    def new_file(self):
        self.count = 0
        self.file_state.config(text=self.midimap_name)
        for record in self.items_list.get_children():
            self.items_list.delete(record)

    def check_devices(self):
        try:
            self.device = MidiIn()
        except NameError:
            raise ImportError("rtmidi not imported")

        self.available_ports = self.device.get_ports()
        devices = ()
        for port in self.available_ports:
            devices += (port,)
        self.device_chkbox["values"] = devices
        self.device_chkbox.set("Choose Device")

    def conn_device(self):
        if not self.tgl_conn:
            self.device.set_callback(self.callback)
            self.device_id = self.device_chkbox.current()
            self.device.open_port(self.device_id)
            self.device.ignore_types(timing=False)
            self.device_chkbox.state(["disabled"])
            self.device_state.config(text=self.device_chkbox.get())
            self.device_connbtn.config(text="Disconnect!")
            self.tgl_conn = True
        else:
            self.tgl_conn = False
            self.device.close_port()
            self.device_chkbox.state(["!disabled"])
            self.device_connbtn.config(text="Connect It!")
            self.device_state.config(text="No Device Connected")
            self.txt_output.config(text="No Midi Output Yet!")

    def callback(self, msg: list, timestamp: float):
        msg_update = "Status: "+str(msg[0][0])+" -- CC/Note: "+str(msg[0][1])+" -- Value/Velocity: "+str(msg[0][2])+" -- Time: "+str(round(msg[1], 3))
        self.txt_output.config(text=msg_update)

    def load_mmf(self):
        self.mm_top.iconify()
        self.new_file()
        self.filename = tkFileDialog.askopenfilename(
            title="Load Midi Map",
            filetypes=[("JSON files", ".json")],
            initialdir=os.path.join(FOXDOT_MIDI_MAPS, ""),
            defaultextension=".json")
        if self.filename:
            new_name = os.path.split(self.filename)[1]
            new_name = os.path.splitext(new_name)[0]
            self.file_state.config(text=self.filename)
            with open(self.filename, "r") as openfile:
                # Reading from json file
                json_object = json.load(openfile)
                mm_name = list(json_object.keys())[0]
                self.file_state.config(text=mm_name)
                for key, value in json_object.items():
                    mm_dict = value
                self.count = 0
                for key, val in mm_dict.items():
                    name = key
                    type = val[0]
                    cc = val[1]
                    value = val[2]
                    self.items_list.insert(parent="",
                                           index="end",
                                           iid=self.count,
                                           text="",
                                           tags=(type,),
                                           values=(name, type, cc, value))
                    self.count += 1
        self.mm_top.deiconify()

    def save_mmf(self):
        # Save it into a json file
        self.mm_top.iconify()
        self.filename = tkFileDialog.asksaveasfilename(
            title="Save Midi Map",
            filetypes=[("JSON files", ".json")],
            initialdir=os.path.join(FOXDOT_MIDI_MAPS, ""),
            defaultextension=".json")
        if self.filename:
            # Get data from treeview list
            new_name = os.path.split(self.filename)[1]
            new_name = os.path.splitext(new_name)[0]
            new_midimap = {new_name: {}}
            for line in self.items_list.get_children():
                name = self.items_list.item(line)["values"][0]
                type = self.items_list.item(line)["values"][1]
                cc = self.items_list.item(line)["values"][2]
                value = self.items_list.item(line)["values"][3]
                new_midimap[new_name][name] = [type, cc, value]
            self.file_state.config(text=new_name)
            new_file = open(self.filename, "w")
            json.dump(new_midimap, new_file, indent=6)
            new_file.close()
            print("Midi Map saved.")
        else:
            pass
        self.mm_top.deiconify()

    def gen_vmf(self):
        vmf_dict = {}
        name = self.file_state.cget("text")
        if name != self.midimap_name:
            vmf_dict[name] = {}
            tmp_list = []
            for line in self.items_list.get_children():
                vals = []
                vals.append(self.items_list.item(line)["values"][0])
                vals.append(self.items_list.item(line)["values"][3])
                tmp_list.append(vals)
            for element in tmp_list:
                vmf_dict[name][element[0]] = [element[1], {}]
            # Save it into a json file
            self.mm_top.iconify()
            self.filename = tkFileDialog.asksaveasfilename(
                title="Save Value Map",
                filetypes=[("JSON files", ".json")],
                initialdir=os.path.join(FOXDOT_ROOT, ""),
                defaultextension=".json")
            if self.filename:
                # Get data from treeview list
                new_name = os.path.split(self.filename)[1]
                new_name = os.path.splitext(new_name)[0]
                new_valmap = vmf_dict
                new_file = open(self.filename, "w")
                json.dump(new_valmap, new_file, indent=6)
                new_file.close()
                print("Value Map saved.")
            else:
                pass
            self.mm_top.deiconify()
        else:
            self.mm_top.iconify()
            alert_text = "There is no Midi Map saved or loaded.\nPlease save/load a Midi Map, and try again!"
            alert_message = Messagebox.ok(alert_text)
            self.mm_top.deiconify()

    def info_vmf(self):
        info = '''
        VALUE MAPPING DICTIONARY
        -------------------------------------------------------------------------------------------

        To be able to generate a ValMap template that is useable, a naming convention is needed
        to remember the relation to your Midi Map setup. The generated template will created
        nested dictionaries with this names.

        The default name is U0:E0 (Unit 0, Element 0), whereby Unit can be e.g. a row, a column,
        a X-shape, or a L-shape.

        An element can be an Exchangable Element (EE), e.g. knobs, slider, pads. The template
        generator will create a dictionary with the Elements' value range as key. The value will
        be another nested empty dictionary, that can be filled with synth or group attributes as
        keys later, and list value with the according attribute Minimum and Maximum.

            e.g. {
                    "0-127": {"room": [1/2, 1], "hpf": [80, 4000], "lpf": [4000, 20]},
                 }

        On the other hand, it can be a Control Element (CE), e.g. switch, button. As with EE, the
        template will contain an empty dictionary with the value as key. This might be "Push",
        "Switch", or "Count". The value of this dictionary is going to have the related EE or CE
        names go through the values of several EEs' at the same time, or to add more functionality
        to another CE.

            e.g. {
                    "Count": ["U0:E1", "U0:E2"],
                 }

        {
        "Name of Midi Device": [
                "U0:E0": {
                        "Hold": {},
                },
                "U0:E1": {
                        "0-127": {},
                },
                "U0:E2": {
                        "X: 0-127": {},
                        "Y: 0-127": {},
                },
                "U1:E0": {
                        "-64-64": {},
                },
                "U1:E1": {
                        "Push": {},
                },
            ]
        }
        '''
        self.info_box = tb.Toplevel(topmost=True)
        self.info_text = ScrolledText(self.info_box,
                                      wrap=WORD,
                                      autohide=False,
                                      bootstyle="info",
                                      hbar=True)
        self.info_text.insert(END, info)
        self.info_text.grid(row=0,
                            column=0,
                            padx=20,
                            pady=15,
                            sticky="WE")
        self.ok_btn = tb.Button(self.info_box,
                                text="Close Info",
                                command=self.close_infobox)
        self.ok_btn.grid(row=1,
                         column=0,
                         padx=20,
                         pady=15,
                         sticky="E")

    def close_infobox(self):
        self.info_box.lift(aboveThis=None)
        self.info_box.destroy()

    def save_and_close(self, event=None):
        self.mm_top.lift(aboveThis=None)
        self.mm_top.destroy()
