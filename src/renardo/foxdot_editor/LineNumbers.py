from renardo.foxdot_editor.tkimport import *
from renardo.settings_manager import settings
from renardo.lib.Code import execute


class LineNumbers(tb.Canvas):
    def __init__(self, master, *args, **kwargs):
        tb.Canvas.__init__(self, *args, **kwargs)
        self.root = master
        self.textwidget = master.text

    def redraw(self, *args):
        '''redraw line numbers'''
        # Update player line numbers
        # execute.update_line_numbers(self.textwidget)
        # Clear
        self.delete("all")
        # Draw a line
        w = self.winfo_width() - 1
        h = self.winfo_height()
        self.create_line(w, 0, w, h, fill="gray")
        i = self.textwidget.index("@0,0")

        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            h = dline[3]
            linenum = int(str(i).split(".")[0])
            curr_row = int(self.textwidget.index(INSERT).split(".")[0])

            if linenum == curr_row:
                x1, y1 = 0, y + settings.get("foxdot_editor.LINE_NUMBER_MARKER_OFFSET")
                x2, y2 = w - 2, y + h
                self.create_rectangle(x1,
                                      y1,
                                      x2,
                                      y2,
                                      fill="gray30",
                                      outline="gray30")

            self.create_text(w - 4, y, anchor="ne",
                             justify=RIGHT,
                             text=linenum,
                             font=self.root.codefont,
                             fill="#c9c9c9")

            i = self.textwidget.index("{}+1line".format(i))

        # Update console beat counter here too
        self.root.console.counter.redraw()
        self.after(30, self.redraw)

    def hide(self):
        """ Removes treeview from interface """
        self.grid_remove()
        return

    def show(self):
        self.grid()
        return
