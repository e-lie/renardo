import sys
import os
import json
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox

if sys.version_info[0] >= 3:
    from tkinter import *
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
else:
    from Tkinter import *
    import ttk
    import tkFont
    import tkFileDialog
    import tkMessageBox
