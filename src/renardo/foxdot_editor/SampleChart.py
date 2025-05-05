#!/usr/bin/env python
from __future__ import absolute_import

import multiprocessing
import os
from .tkimport import *
from .Format import *
from renardo.settings_manager import *
from renardo.settings_manager import settings



try:
    from playsound import playsound
except Exception:
    print("playsound library not installed...")


class SampleChart:

    def __init__(self):
        # Basic TKinter function
        self.root = Tk()
        self.width = 800
        self.height = 600
        self.wheel_count = 0
        self.root.minsize(self.width, self.height)
        self.root.title("FoxDot >> Samples Database Chart")
        self.root.resizable(True, True)
        self.root.grid_rowconfigure(0, weight=1)  # configure grid system
        self.root.grid_columnconfigure(0, weight=1)
        # self.root.iconbitmap('img/foxdot.ico')
        # Call init methods
        self.sp_count = len([name for name in os.listdir(str(settings.get_path("SAMPLES_DIR")))])
        self.sp_names = os.listdir(str(settings.get_path("SAMPLES_DIR")))
        self.sp_names.sort()
        self.sp_view()
        self.create_dics(spack_id="0_foxdot_default")
        self.smpl_view(self.width, self.height)
        self.root.mainloop()

    def sp_view(self):
        """Generate a button for each sample database by spack folder"""
        # Set SoundPack_SAMPLES Frame
        self.sp_frame = Frame(self.root)
        self.sp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        # Label for SoundPack List
        self.sp_label = Label(
            self.sp_frame,
            text="SAMPLES_PACK",
            compound="left")
        self.sp_label.grid(row=0, column=0, padx=10, sticky="w")
        # Add Buttons
        for count in range(self.sp_count):
            lbl = self.sp_names[count]
            btn_sp = Button(
                self.sp_frame,
                text=lbl,
                command=lambda sp=lbl: self.change_sp(sp))
            btn_sp.grid(row=1, column=count, padx=10, pady=10, sticky="w")
        self.txt_frame = Frame(self.sp_frame)
        self.txt_frame.grid(columnspan=self.sp_count,
                            row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.lbl_file = Label(
            self.txt_frame,
            text="Filename: ",
            anchor="w")
        self.lbl_file.grid(columnspan=self.sp_count,
                           row=0,
                           column=0,
                           padx=20,
                           pady=5,
                           sticky="w")
        self.txt = Text(self.txt_frame, width=80, height=1)
        self.txt.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def create_dics(self, spack_id="0_foxdot_default"):
        """
        Iterating through subfolders and writing all file names into dictionary
        lists
        """
        self.spack_id_str = str(spack_id)
        self.ext = ('.wav', 'aif')
        self.dict_letters = {}
        self.dict_letters.clear()
        self.dict_specials = {}
        self.dict_specials.clear()
        self.dict_loops = []
        # First go through all letters and get file paths in upper and lower
        # Fill dictionary with letters as key and file names of audio as values
        self.sp_path_l = str(settings.get_path("SAMPLES_DIR")) + "/" + spack_id + "/"
        self.dir_list_l = []

        for filename in os.listdir(self.sp_path_l):
            if os.path.isdir(os.path.join(self.sp_path_l, filename)):
                self.dir_list_l.append(filename)

        self.dir_list_l.sort()

        for i in self.dir_list_l:
            if i != "_" and i != "_loop_":
                self.new_path = self.sp_path_l + str(i) + "/lower/"
                # self.smpl_list = os.path.isdir(self.new_path)
                self.smpl_list = [
                    f for f in os.listdir(self.new_path)
                    if os.path.isfile(os.path.join(self.new_path, f))
                ]
                self.smpl_list.sort()
                for n in self.smpl_list:
                    if not n.endswith(self.ext):
                        self.smpl_list.remove(n)
                self.dict_letters[i.upper()] = self.smpl_list
                self.dict_letters[i] = self.smpl_list
                self.new_path = self.sp_path_l + str(i) + "/upper/"
                self.smpl_list = [
                    f for f in os.listdir(self.new_path)
                    if os.path.isfile(os.path.join(self.new_path, f))
                ]
                self.smpl_list.sort()
                for n in self.smpl_list:
                    if not n.endswith(self.ext):
                        self.smpl_list.remove(n)
                self.dict_letters[i.upper()] = self.smpl_list

        # Fill dictionary with specials as key and file names of
        # audio as values
        self.sp_path_s = self.sp_path_s = str(settings.get_path("SAMPLES_DIR"))+"/"+spack_id+"/_/"
        self.dir_list_s = []
        for filename in os.listdir(self.sp_path_s):
            if os.path.isdir(os.path.join(self.sp_path_s, filename)):
                self.dir_list_s.append(filename)
        self.dir_list_s.sort()
        for j in self.dir_list_s:
            self.new_path = self.sp_path_s + str(j) + "/"
            self.smpl_list = [
                f for f in os.listdir(self.new_path)
                if os.path.isfile(os.path.join(self.new_path, f))
            ]
            self.smpl_list.sort()
            for n in self.smpl_list:
                if not n.endswith(self.ext):
                    self.smpl_list.remove(n)
            self.dict_specials[j] = self.smpl_list
        # Fill dictionary with loops as value
        self.sp_path_loops = str(settings.get_path("SAMPLES_DIR"))+"/"+spack_id+"/"+settings.get("samples.LOOP_DIR_NAME")
        self.smpl_list = [
            f for f in os.listdir(self.sp_path_loops)
            if os.path.isfile(os.path.join(self.sp_path_loops, f))
        ]
        self.smpl_list.sort()
        for n in self.smpl_list:
            if not n.endswith(self.ext):
                self.smpl_list.remove(n)
        self.dict_loops = self.smpl_list

    def smpl_view(self, w, h):
        """Generate a button for each sample arranged by character folder"""
        self.w = self.width
        self.h = self.height
        self.processes = []
        # Create basic frame that will contain all
        self.frame = Frame(self.root)
        self.frame.grid(row=2, column=0, sticky='news')
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame_label = Label(self.frame,
                                 text="SAMPLES",
                                 compound="left")
        self.frame_label.grid(row=0, column=0, padx=20, sticky="w")
        # Add a canvas in that frame
        self.canvas = Canvas(self.frame, bg=colour_map['background'])
        self.canvas.grid(row=1, column=0, sticky='news')
        # Link a scrollbar to the canvas
        self.xsb = Scrollbar(self.frame, orient="horizontal",
                             command=self.canvas.xview)
        self.ysb = Scrollbar(self.frame, orient="vertical",
                             command=self.canvas.yview)
        self.xsb.grid(row=2, column=0, sticky='we')
        self.ysb.grid(row=1, column=1, sticky='ns')
        self.canvas.configure(xscrollcommand=self.xsb.set,
                              yscrollcommand=self.ysb.set)
        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_rowconfigure(1, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(1, weight=1)
        # Create a frame to contain Buttons
        self.btn_frame = Frame(self.canvas, bg=colour_map['background'])
        self.canvas.create_window((0, 0), window=self.btn_frame, anchor='nw')
        # Generate sample buttons
        self.smpl_btns()
        # Update buttons frames idle tasks to let tkinter calculate
        # buttons sizes
        self.btn_frame.update_idletasks()
        self.canvas['xscrollcommand'] = self.xsb.set
        # Resize the canvas frame
        self.canvas.config(width=self.w - self.ysb.winfo_width(),
                           height=self.h - self.xsb.winfo_height())
        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.grid_propagate(True)
        # This is what enables using the mouse:
        self.btn_frame.bind("<ButtonPress-1>", self.move_start)
        self.btn_frame.bind("<B1-Motion>", self.move_move)
        # linux scroll
        self.btn_frame.bind("<Button-4>", self.on_mousewheel)
        self.btn_frame.bind("<Button-5>", self.on_mousewheel)
        self.btn_frame.bind("<Prior>", self.on_mousewheel)  # Bind to PageUp
        self.btn_frame.bind("<Next>", self.on_mousewheel)  # Bind to PageDown
        # play audio
        # self.root.bind("<space>", self.space_play)
        # windows scroll
        self.btn_frame.bind("<MouseWheel>", self.on_mousewheel)
        self.btn_frame.bind("<space>", self.press_space)
        # Update canvas when changing window size
        self.root.bind("<Configure>", self.on_resize)

    def smpl_btns(self):
        """Generate audio sample buttons"""
        self.colors = list(colour_map.keys())
        self.col_space = 12
        # First delete all in btn_frame
        for widgets in self.btn_frame.winfo_children():
            widgets.destroy()
        # Add category buttons
        self.counter = 0
        for k in self.dict_letters.keys():
            self.btn = Button(self.btn_frame, text=k, width=10,
                              fg='white', bg=colour_map['background'])
            self.btn.grid(row=self.counter, column=0)
            self.counter += 1
        for n in self.dict_specials.keys():
            self.special = list(settings.get("samples.NON_ALPHA").keys())[list(settings.get("samples.NON_ALPHA").values()).index(n)]
            self.btn = Button(self.btn_frame, text=self.special,
                              width=10, fg='white',
                              bg=colour_map['background'])
            self.btn.grid(row=self.counter, column=0)
            self.counter += 1
        self.btn = Button(self.btn_frame, text="loop", width=10,
                          fg='white', bg=colour_map['background'])
        self.btn.grid(row=self.counter, column=0)
        # Create buttons for each sample in the letters dictionary
        self.dcounter = 0
        for m in self.dict_letters:
            self.fcounter = 0
            for v in self.dict_letters[m]:
                self.word = v.lower()
                if "_" in self.word or "-" in self.word:
                    self.word = self.word.replace('.', '_')
                    self.word = self.word.replace('-', '_')
                    self.word = self.word.split('_')
                self.color = ""
                self.btn = Button(self.btn_frame,
                                  text=self.fcounter,
                                  width=1,
                                  command=lambda r=m,
                                  c=self.fcounter,
                                  p=v,
                                  d=self.dcounter,
                                  f=self.fcounter+self.col_space: self.play_audio(r, c, p, d, f))
                for c in self.colors:
                    if c in self.word:
                        self.color = c
                        self.btn.configure(bg=colour_map[self.color])
                    elif self.color == "":
                        self.btn.configure(bg=colour_map["default"])
                self.btn.grid(row=self.dcounter, column=self.fcounter + self.col_space)
                self.fcounter += 1
            self.dcounter += 1
        # Create buttons for each sample in the specials dictionary
        for n in self.dict_specials:
            self.fcounter = 0
            for w in self.dict_specials[n]:
                self.word = w.lower()
                if "_" in self.word or "-" in self.word:
                    self.word = self.word.replace('.', '_')
                    self.word = self.word.replace('-', '_')
                    self.word = self.word.split('_')
                self.color = ""
                self.btn = Button(self.btn_frame,
                                  text=self.fcounter,
                                  width=1,
                                  command=lambda r=n,
                                  c=self.fcounter,
                                  p=w,
                                  d=self.dcounter,
                                  f=self.fcounter+self.col_space: self.play_audio(r, c, p, d, f))
                for c in self.colors:
                    if c in self.word:
                        self.color = c
                        self.btn.configure(bg=colour_map[self.color])
                    elif self.color == "":
                        self.btn.configure(bg=colour_map["default"])
                self.btn.grid(row=self.dcounter, column=self.fcounter + self.col_space)
                self.fcounter += 1
            self.dcounter += 1
        self.fcounter = 0
        for path in self.dict_loops:
            self.btn = Button(self.btn_frame,
                              text=self.fcounter,
                              width=1,
                              fg="white",
                              bg=colour_map["loops"],
                              command=lambda r="loops",
                              c=self.fcounter,
                              p=path,
                              d=self.dcounter,
                              f=self.fcounter+self.col_space: self.play_audio(r, c, p, d, f))
            # self.btn_frame.bind('<Return>', lambda event=None: button.invoke())
            self.btn.grid(row=self.dcounter, column=self.fcounter + self.col_space)
            self.fcounter += 1

    def play_audio(self, char, sample, path, row, col):
        """Displays sample code to copy and plays audio"""
        if len(self.processes) > 0:
            for p in self.processes:
                p.terminate()
        self.info = [row, col]
        self.txt.delete('1.0', END)
        self.char = char
        self.cmd = ""

        if len(self.char) == 1 and self.char.isalpha():
            if self.char.isupper():
                self.path = self.sp_path_l + self.char.lower() + "/upper/" + path
            elif self.char.islower():
                self.path = self.sp_path_l + self.char + "/lower/" + path
            self.cmd = "play"
        elif self.char == "loops":
            self.path = self.sp_path_l + settings.get("samples.LOOP_DIR_NAME") + "/" + path
            self.cmd = "loop"
            self.char = os.path.splitext(path)[0]
        else:
            self.char = list(settings.get("samples.NON_ALPHA").keys())[list(
                settings.get("samples.NON_ALPHA").values()).index(self.char)]
            self.path = self.sp_path_s + char + "/" + path
            self.cmd = "play"
        try:
            self.p = multiprocessing.Process(target=playsound, args=(self.path,))
        except Exception:
            print("playsound library not installed...")
        if self.spack_id_str == "0_foxdot_default":
            spack = "0"
        else:
            spack = self.spack_id_str
        self.code = f'{self.cmd}("{self.char}", spack={spack}, sample={sample})'
        self.txt.insert(END, self.code)
        self.change_fname(path)
        self.p.start()
        self.processes.append(self.p)

    def press_space(self, event):
        # self.play_audio(char, sample, path, row, col)
        pass

    def change_sp(self, spack_id):
        """Deletes buttons and regenerate dictionaries and buttons with set database number"""
        self.sp_id = spack_id
        self.create_dics(self.sp_id)
        self.smpl_btns()
        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self.btn_frame.update_idletasks()
        # Resize the canvas frame
        self.canvas.config(width=self.w - self.ysb.winfo_width(),
                           height=self.h - self.xsb.winfo_height())
        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.grid_propagate(True)

    def change_fname(self, path):
        self.lbl_file["text"] = "Filename: " + path

    def on_mousewheel(self, event):
        """respond to Linux or Windows wheel event"""
        if event.num == 5 or event.delta == -120:
            self.wheel_count -= 1
        if event.num == 4 or event.delta == 120:
            self.wheel_count += 1

    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_resize(self, event):
        self.width = self.root.winfo_width() - 10
        self.height = self.root.winfo_height() - self.sp_frame.winfo_reqheight() - 30
        # resize the canvas
        self.canvas.config(width=self.width - self.ysb.winfo_width(),
                           height=self.height - self.xsb.winfo_height())
