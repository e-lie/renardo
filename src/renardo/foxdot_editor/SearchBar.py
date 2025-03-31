from renardo.foxdot_editor.tkimport import *
from renardo.foxdot_editor.tkimport import Text, SEL, END, SEL_FIRST, SEL_LAST, INSERT
from renardo.foxdot_editor.Format import *


class SearchBar:

    def __init__(self, parent):
        self.root = parent.root
        self.parent = parent
        self.f_height = 50
        self.sb_frame = tb.Frame(
            self.root, height=self.f_height)
        self.sb_frame.grid(row=1, column=2, sticky='ew')
        self.hide()
        self.search_list = list()
        self.search = ""
        self.idx = ""
        self.sb_label = tb.Label(
            self.sb_frame, text="Enter search")
        self.sb_label.grid(row=0, column=0, padx=10)
        self.search_entry = tb.Entry(
            self.sb_frame, width=40, justify="left")
        self.search_entry.grid(row=0, column=1, padx=10)
        self.search_btn = tb.Button(
            self.sb_frame, text="Search", command=self.search_task)
        self.search_btn.grid(row=0, column=2, padx=10, pady=5, sticky="e")

    def reset_list(self):
        if self.search != self.search_entry.get():
            self.search_list.clear()
            self.parent.text.tag_remove(SEL, "1.0", "end-1c")

    def search_task(self):
        self.reset_list()
        self.parent.text.focus_set()
        self.search = self.search_entry.get()

        if self.search:
            if self.search_list == []:
                self.idx = "1.0"
            else:
                self.idx = self.search_list[-1]
            self.idx = self.parent.text.search(self.search, self.idx, nocase=1,
                                               stopindex=END)
            self.lastidx = '%s+%dc' % (self.idx, len(self.search))
            try:
                self.parent.text.tag_remove(SEL, "1.0", self.lastidx)
            except Exception:
                pass
            try:
                self.parent.text.tag_add(SEL, self.idx, self.lastidx)
                self.counter_list = []
                self.counter_list = str(self.idx).split('.')
                self.parent.text.mark_set("insert", "%d.%d" % (float(int(self.counter_list[0])), float(int(self.counter_list[1]))))
                self.parent.text.see(float(int(self.counter_list[0])))
                self.search_list.append(self.lastidx)
            except Exception:
                tkMessageBox.showinfo("Search complete", "No further matches")
                self.search_list.clear()
                self.parent.text.tag_remove(SEL, "1.0", "end-1c")

    def hide(self):
        """ Removes searchbar from interface """
        self.sb_frame.grid_remove()
        return

    def show(self):
        self.sb_frame.grid()
        return
