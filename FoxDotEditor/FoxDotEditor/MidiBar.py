from FoxDotEditor.tkimport import *
import time
from threading import Thread
from renardo_lib.Utils import midi_cmd


class MidiBar:
    def __init__(self, parent):
        self.root = parent.root
        self.parent = parent
        self.f_height = 100
        self.fontH1 = tkFont.Font(size=14)
        self.fontH2 = tkFont.Font(size=12)
        self.midi_cmd = midi_cmd()
        self.midi_msg = self.midi_cmd.get_msg()
        self.mb_frame = tb.Frame(
            self.root, height=self.f_height)
        self.mb_frame.grid(row=0, column=2, columnspan=4, sticky='sew')
        self.hide()
        self.slots = 16
        self.var_list = []
        self.lbl_list = []
        for i in range(self.slots):
            self.var_list.append(tb.StringVar())
            self.var_list[i].set("")
            self.lbl_list.append(tb.Label(self.mb_frame,
                                          textvariable=self.var_list[i],
                                          font=self.fontH2,
                                          width=18))
            if i < self.slots/2:
                self.lbl_list[i].grid(row=0, column=i, padx=2, sticky="ew")
            else:
                num = i - self.slots/2
                self.lbl_list[i].grid(row=1, column=int(num), padx=2, sticky="ew")
        self.setText_thread = Thread(target=self.set_text)
        self.is_running = True
        self.setText_thread.setDaemon(True)
        self.setText_thread.start()

    def set_text(self):
        cur_attr = ""
        while self.is_running:
            msg = self.midi_cmd.get_msg()
            if cur_attr != msg[1].split("=")[0]:
                for i in reversed(range(self.slots)):
                    txt = self.var_list[i-1].get()
                    self.var_list[i].set(txt)
                self.var_list[0].set(msg[1])
                cur_attr = msg[1].split("=")[0]
            else:
                self.var_list[0].set(msg[1])
            time.sleep(0.01)

    def close(self):
        self.midi_cmd.is_running = False
        self.is_running = False
        self.setText_thread.join()

    def hide(self):
        """ Removes searchbar from interface """
        self.mb_frame.grid_remove()
        return

    def show(self):
        self.mb_frame.grid()
        return
