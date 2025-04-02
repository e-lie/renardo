import sys
import os
import json
import ttkbootstrap as tb

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

# Check for OS -> mac, linux, win
SYSTEM = 0
WINDOWS = 0
LINUX = 1
MAC_OS = 2

if sys.platform.startswith('darwin'):
    SYSTEM = MAC_OS
    # Attempted fix for some macOS users
    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except ImportError:
        pass
elif sys.platform.startswith('win'):
    SYSTEM = WINDOWS
elif sys.platform.startswith('linux'):
    SYSTEM = LINUX