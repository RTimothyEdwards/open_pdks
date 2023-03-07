#!/usr/bin/env python3
#
#--------------------------------------------------------
# Text Report Window for the Open Galaxy characterization
# tool (simple text window with contents read from file)
#
#--------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# June 27, 2017
# Version 0.1
#--------------------------------------------------------

import os
import re
import tkinter
from tkinter import ttk

class TextReport(tkinter.Toplevel):
    """Open Galaxy text report window."""

    def __init__(self, parent=None, fontsize = 11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)

        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.withdraw()
        self.title('Open Galaxy Text Report')

        self.texttitle = ttk.Label(self, style='title.TLabel', text = '(no text)')
        self.texttitle.grid(column = 0, row = 0, sticky = "news")
        self.textbar = ttk.Separator(self, orient='horizontal')
        self.textbar.grid(column = 0, row = 1, sticky = "news")

        self.hframe = tkinter.Frame(self)
        self.hframe.grid(column = 0, row = 2, sticky = "news")
        self.hframe.textdisplay = ttk.Frame(self.hframe)
        self.hframe.textdisplay.pack(side = 'left', fill = 'both', expand = 'true')
        self.hframe.textdisplay.page = tkinter.Text(self.hframe.textdisplay, wrap = 'word')
        self.hframe.textdisplay.page.pack(side = 'top', fill = 'both', expand = 'true')
        # Add scrollbar to text window
        self.hframe.scrollbar = ttk.Scrollbar(self.hframe)
        self.hframe.scrollbar.pack(side='right', fill='y')
        # attach text window to scrollbar
        self.hframe.textdisplay.page.config(yscrollcommand = self.hframe.scrollbar.set)
        self.hframe.scrollbar.config(command = self.hframe.textdisplay.page.yview)

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 3, sticky = "news")
        self.bbar.close_button = ttk.Button(self.bbar, text='Close',
		command=self.close, style = 'normal.TButton')
        self.bbar.close_button.grid(column = 0, row = 0, padx = 5)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
        self.columnconfigure(0, weight=1)

        # Initialize with empty page
        self.text = []
        self.title = '(No file to display)'
        self.timestamp = 0

    def grid_configure(self, padx, pady):
        pass

    def display(self, filename=''):
        # Read from file if text is empty
        if filename != '':
            if filename == self.title:
                statbuf = os.stat(filename)
                if self.text == [] or self.timestamp < statbuf.st_mtime:
                    self.add_text_from_file(filename)
                    self.timestamp = statbuf.st_mtime
            else:
                 self.add_text_from_file(filename)

        # Remove and replace contents
        self.hframe.textdisplay.page.delete('1.0', 'end')
        self.hframe.textdisplay.page.insert('end', self.text)
        self.textttitle.configure(text = self.title)
        self.open()

    # Fill the text report from a file.

    def add_text_from_file(self, filename):
        print('Loading text from file ' + filename)
        with open(filename, 'r') as f:
            self.text = f.read()
        self.title = filename
        self.display()

    def close(self):
        # pop down text window
        self.withdraw()

    def open(self):
        # pop up text window
        self.deiconify()
        self.lift()
