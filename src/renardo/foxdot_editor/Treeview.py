"""
    Simple File System Explorer with Tk
"""
from renardo.foxdot_editor.tkimport import *
from pathlib import Path
from renardo.settings_manager import settings
import os


class TreeView:

    def __init__(self, parent):
        self.app = parent
        self.root = parent.root
        self.tv_pane = tb.Frame(
            self.root,
            width=220,
            height=400)
        self.tv_pane.grid(row=0, column=0, sticky='nsew', rowspan=4)
        # Make sure the treeview widget follows the window
        # when resizing.
        self.tv_pane.rowconfigure(0, weight=1)
        self.tv_pane.columnconfigure(0, weight=1)
        self.hide()
        self.y_scroll = tb.Scrollbar(self.tv_pane)
        self.y_scroll.grid(row=0, column=1, sticky='ns')
        self.scrollable = False
        self.drag = tb.Frame(
            self.tv_pane,
            cursor="sb_h_double_arrow",
            width=5
        )
        # show="tree" removes the column header, since we
        # are not using the table feature.
        self.treeview = tb.Treeview(self.tv_pane, show="tree")
        self.treeview.grid(row=0, column=0, sticky="nsew", rowspan=3)
        # Call the item_opened() method each item an item
        # is expanded.
        self.treeview.tag_bind(
            "fstag", "<<TreeviewOpen>>", self.item_opened)
        # This dictionary maps the treeview items IDs with the
        # path of the file or folder.
        self.fsobjects: dict[str, Path] = {}
        self.file_image = PhotoImage(file=str(settings.get_path("FOXDOT_EDITOR_ROOT"))+"/img/file.png")
        self.folder_image = PhotoImage(file=str(settings.get_path("FOXDOT_EDITOR_ROOT"))+"/img/folder.png")
        # Load the user directory.
        self.home_path = str(Path.home())
        self.load_tree(Path(os.path.expanduser(self.home_path)))
        self.mouse_down = False
        self.drag.bind("<Button-1>",
                       self.drag_mouseclick)
        self.drag.bind("<ButtonRelease-1>",
                       self.drag_mouserelease)
        self.drag.bind("<B1-Motion>",
                       self.drag_mousedrag)
        self.drag.grid(row=0, column=2, stick="ns")
        self.treeview.bind("<Double-Button-1>", self.doubleclick)
        self.treeview.bind("<ButtonRelease-1>", self.drag_mouserelease)
        self.treeview.grid(row=0, column=0, stick="ns")

    def doubleclick(self, event):
        self.mouse_down = True
        item = self.treeview.selection()
        parent_iid = self.treeview.parent(item)
        node = []
        # go backward until reaching root
        while parent_iid != '':
            node.insert(0, self.treeview.item(parent_iid)['text'])
            parent_iid = self.treeview.parent(parent_iid)
        i = self.treeview.item(item, "text")
        path = self.home_path + os.path.sep + os.path.join(*node, i)
        if path.endswith(".py"):
            self.app.opentvfile(path)
        return

    def drag_mouseclick(self, event):
        """ Allows the user to resize the treeview width """
        self.mouse_down = True
        self.root.grid_propagate(False)
        return

    def drag_mouserelease(self, event):
        self.mouse_down = False
        return

    def drag_mousedrag(self, event):
        if self.mouse_down:
            self.root_v = self.tv_pane.winfo_width()
            widget_x = self.tv_pane.winfo_rootx()
            new_width = (self.tv_pane.winfo_width() + (widget_x - event.x_root))
            self.width, old_width = new_width, self.tv_pane.winfo_width()
            self.tv_pane.configure(width=max(self.width, 200))
            # return "break"

    def safe_iterdir(self, path: Path) -> tuple[Path, ...] | tuple[()]:
        """
        Like `Path.iterdir()`, but do not raise on permission errors.
        """
        try:
            return tuple(path.iterdir())
        except PermissionError:
            print("You don't have permission to read", path)
            return ()

    def get_icon(self, path: Path):
        """
        Return a folder icon if `path` is a directory and
        a file icon otherwise.
        """
        return self.folder_image if path.is_dir() else self.file_image

    def insert_item(self, name: str, path: Path, parent: str = "") -> str:
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.treeview.insert(
            parent, END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid

    def load_tree(self, path: Path, parent: str = ""):
        """
        Load the contents of `path` into the treeview.
        """
        for fsobj in self.safe_iterdir(path):
            fullpath = path / fsobj
            child = self.insert_item(fsobj.name, fullpath, parent)
            # Preload the content of each directory within `path`.
            # This is necessary to make the folder item expandable.
            if fullpath.is_dir():
                for sub_fsobj in self.safe_iterdir(fullpath):
                    self.insert_item(sub_fsobj.name, fullpath/sub_fsobj, child)

    def load_subitems(self, iid: str):
        """
        Load the content of each folder inside the specified item
        into the treeview.
        """
        for child_iid in self.treeview.get_children(iid):
            if self.fsobjects[child_iid].is_dir():
                self.load_tree(self.fsobjects[child_iid],
                               parent=child_iid)

    def item_opened(self, _event: Event):
        """
        Handler invoked when a folder item is expanded.
        """
        # Get the expanded item.
        iid = self.treeview.selection()
        # If it is a folder, loads its content.
        self.load_subitems(iid)

    def hide(self):
        """ Removes treeview from interface """
        self.tv_pane.grid_remove()
        return

    def show(self):
        self.tv_pane.grid()
        return
