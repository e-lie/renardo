#!/usr/bin/env python
from __future__ import absolute_import

import multiprocessing
from playsound import playsound
from .tkimport import *
from .Format import *
from renardo_lib.Settings import *
from renardo_lib import spack_manager
from renardo_gatherer.samples_download import nonalpha
from renardo_gatherer import SAMPLES_DIR_PATH

class SampleChart:

    def __init__(self):
        # Basic TKinter function
        self.root = Tk()

        self.width = 800
        self.height = 600
        self.wheel_count = 0
        self.root.geometry(str(self.width) + "x" + str(self.height))
        self.root.title("FoxDot >> Samples Database Chart")
        self.root.resizable(True, True)

        #self.root.iconbitmap('img/foxdot.ico')

        # Call init methods
        self.db_view()
        self.create_dics(spack_num=0)
        self.smpl_view(self.width, self.height)
        self.root.mainloop()

    def create_dics(self, spack_num=0):
        """Iterating through subfolders and writing all file names into dictionary lists"""
        self.spack_num_str = str(spack_num)
        self.ext = ('.wav', 'aif')
        self.dict_letters = {}
        self.dict_specials = {}
        self.dict_loops = []
        # First go through all letters and get file paths in upper and lower
        # Fill dictionary with letters as key and file names of audio as values
        self.db_path_l = str(spack_manager.get_spack(int(self.spack_num_str)).path) + "/"
        self.dir_list_l = []

        for filename in os.listdir(self.db_path_l):
            if os.path.isdir(os.path.join(self.db_path_l, filename)):
                self.dir_list_l.append(filename)

        self.dir_list_l.sort()

        for i in self.dir_list_l:
            if i != "_" and i != "_loop_":
                self.new_path = self.db_path_l + str(i) + "/lower/"
                #self.smpl_list = os.path.isdir(self.new_path)
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
                self.new_path = self.db_path_l + str(i) + "/upper/"
                self.smpl_list = [
                    f for f in os.listdir(self.new_path)
                    if os.path.isfile(os.path.join(self.new_path, f))
                ]
                self.smpl_list.sort()
                for n in self.smpl_list:
                    if not n.endswith(self.ext):
                        self.smpl_list.remove(n)
                self.dict_letters[i.upper()] = self.smpl_list

        # Fill dictionary with specials as key and file names of audio as values
        self.db_path_s = str(spack_manager.get_spack(int(self.spack_num_str)).path) + "/_/"
        self.dir_list_s = []
        for filename in os.listdir(self.db_path_s):
            if os.path.isdir(os.path.join(self.db_path_s, filename)):
                self.dir_list_s.append(filename)
        self.dir_list_s.sort()
        for j in self.dir_list_s:
            self.new_path = self.db_path_s + str(j) + "/"
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
        self.db_path_loops = str(spack_manager.get_spack(int(self.spack_num_str)).path) + "/" + FOXDOT_LOOP
        self.smpl_list = [
            f for f in os.listdir(self.db_path_loops)
            if os.path.isfile(os.path.join(self.db_path_loops, f))
        ]
        self.smpl_list.sort()
        for n in self.smpl_list:
            if not n.endswith(self.ext):
                self.smpl_list.remove(n)
        self.dict_loops = self.smpl_list

    def db_view(self):
        """Generate a button for each sample database by spack folder"""
        # Set DB_SAMPLES Frame
        self.db_count = len([name for name in os.listdir(str(SAMPLES_DIR_PATH))])
        self.db_frame = LabelFrame(
            self.root, text="SAMPLES_DB", padx=20, pady=20)
        self.db_frame.grid(row=0, column=0)

        # Add Buttons
        for count in range(self.db_count):
            lbl = str(count)
            btn_db = Button(self.db_frame, text=lbl,
                            command=lambda db=lbl: self.change_db(db))
            btn_db.grid(row=0, column=count, sticky="ns")

        self.db_frame.grid_rowconfigure(1, weight=1)
        self.db_frame.grid_columnconfigure(1, weight=1)
        self.txt_frame = LabelFrame(self.db_frame, text="Code Example", height=1)
        self.txt_frame.grid(columnspan=self.db_count, row=1, column=0, sticky='w')
        self.txt = Text(self.txt_frame, width=80, height=1)
        self.txt.pack()
        self.lbl_file = Label(self.db_frame, text="Filename: ", anchor="w")
        self.lbl_file.grid(columnspan=self.db_count, row=2, column=0, pady=5, sticky="w")

    def smpl_view(self, w, h):
        """Generate a button for each sample arranged by character folder"""
        self.w = self.width
        self.h = self.height
        self.processes = []
        # Create basic frame that will contain all
        self.frame = LabelFrame(self.root, text="SAMPLES")
        self.frame.grid(row=1, column=0, sticky='news')
        self.frame.grid_columnconfigure(0, weight=1)
        # Add a canvas in that frame
        self.canvas = Canvas(self.frame, bg=colour_map['background'])
        self.canvas.grid(row=0, column=0, sticky='news')
        # Link a scrollbar to the canvas
        self.xsb = Scrollbar(self.frame, orient="horizontal",
                             command=self.canvas.xview)
        self.ysb = Scrollbar(self.frame, orient="vertical",
                             command=self.canvas.yview)
        self.xsb.grid(row=1, column=0, sticky='we')
        self.ysb.grid(row=0, column=1, sticky='ns')
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
        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
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
        #self.root.bind("<space>", self.space_play)
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
        counter = 0
        for k in self.dict_letters.keys():
            self.btn = Button(self.btn_frame, text=k, width=10,
                              fg='white', bg=colour_map['background'])
            self.btn.grid(row=counter, column=0)
            counter += 1
        for n in self.dict_specials.keys():
            self.special = list(nonalpha.keys())[
                                list(nonalpha.values()).index(n)]
            self.btn = Button(self.btn_frame, text=self.special,
                              width=10, fg='white', bg=colour_map['background'])
            self.btn.grid(row=counter, column=0)
            counter += 1
        self.btn = Button(self.btn_frame, text="loop", width=10,
                          fg='white', bg=colour_map['background'])
        self.btn.grid(row=counter, column=0)
        # Create buttons for each sample in the letters dictionary
        dcounter = 0
        for m in self.dict_letters:
            fcounter = 0
            for v in self.dict_letters[m]:
                self.word = v.lower()
                if "_" in self.word or "-" in self.word:
                    self.word = self.word.replace('.', '_')
                    self.word = self.word.replace('-', '_')
                    self.word = self.word.split('_')
                self.color = ""
                self.btn = Button(self.btn_frame, text=fcounter,  width=1, command=lambda r=m, c=fcounter,
                                  p=v, d=dcounter, f=fcounter+self.col_space: self.play_audio(r, c, p, d, f))
                for c in self.colors:
                    if c in self.word:
                        self.color = c
                        self.btn.configure(bg=colour_map[self.color])
                    elif self.color == "":
                        self.btn.configure(bg=colour_map["default"])
                self.btn.grid(row=dcounter, column=fcounter + self.col_space)
                fcounter += 1
            dcounter += 1
        # Create buttons for each sample in the specials dictionary
        for n in self.dict_specials:
            fcounter = 0
            for w in self.dict_specials[n]:
                self.word = w.lower()
                if "_" in self.word or "-" in self.word:
                    self.word = self.word.replace('.', '_')
                    self.word = self.word.replace('-', '_')
                    self.word = self.word.split('_')
                self.color = ""
                self.btn = Button(self.btn_frame, text=fcounter,  width=1, command=lambda r=n, c=fcounter,
                                  p=w, d=dcounter, f=fcounter+self.col_space: self.play_audio(r, c, p, d, f))
                for c in self.colors:
                    if c in self.word:
                        self.color = c
                        self.btn.configure(bg=colour_map[self.color])
                    elif self.color == "":
                        self.btn.configure(bg=colour_map["default"])
                self.btn.grid(row=dcounter, column=fcounter + self.col_space)
                fcounter += 1
            dcounter += 1
        fcounter = 0
        for path in self.dict_loops:
            self.btn = Button(self.btn_frame, text=fcounter, width=1, fg="white",
                              bg=colour_map["loops"], command=lambda r="loops", c=fcounter, p=path, d=dcounter, f=fcounter+self.col_space: self.play_audio(r, c, p, d, f))
            #self.btn_frame.bind('<Return>', lambda event=None: button.invoke())
            self.btn.grid(row=dcounter, column=fcounter + self.col_space)
            fcounter += 1

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
                self.path = self.db_path_l + self.char.lower() + "/upper/" + path
            elif self.char.islower():
                self.path = self.db_path_l + self.char + "/lower/" + path
            self.cmd = "play"
        elif self.char == "loops":
            self.path = self.db_path_l + FOXDOT_LOOP + "/" + path
            self.cmd = "loop"
            self.char = os.path.splitext(path)[0]
        else:
            self.char = list(nonalpha.keys())[list(
                nonalpha.values()).index(self.char)]
            self.path = self.db_path_s + char + "/" + path
            self.cmd = "play"
        self.p = multiprocessing.Process(target=playsound, args=(self.path,))
        self.code = f'{self.cmd}("{self.char}", spack={self.spack_num_str}, sample={sample})'
        self.txt.insert(END, self.code)
        self.change_fname(path)
        self.p.start()
        self.processes.append(self.p)

    def press_space(self, event):
        #self.play_audio(char, sample, path, row, col)
        pass

    def change_db(self, spack_num):
        """Deletes buttons and regenerate dictionaries and buttons with set database number"""
        self.spack_num_str = spack_num
        self.create_dics(self.spack_num_str)
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
        self.height = self.root.winfo_height() - self.db_frame.winfo_reqheight() - 30
        # resize the canvas
        self.canvas.config(width=self.width - self.ysb.winfo_width(),
                           height=self.height - self.xsb.winfo_height())

    # #windows zoom
    # def zoomer(self,event):
    #     if (event.delta > 0):
    #         self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
    #     elif (event.delta < 0):
    #         self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
    #     self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    #
    # #linux zoom
    # def zoomerP(self,event):
    #     self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
    #     self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    # def zoomerM(self,event):
    #     self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
    #     self.canvas.configure(scrollregion = self.canvas.bbox("all"))
