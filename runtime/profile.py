#!/usr/bin/env python3
#
#------------------------------------------------------------
# Profile settings window for the project manager
#
#------------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# July 21, 2017
# Version 0.1
#--------------------------------------------------------

import os
import re
import json
import tkinter
import subprocess
from tkinter import ttk

class Profile(tkinter.Toplevel):
    """Project manager profile settings management."""

    def __init__(self, parent=None, fontsize = 11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)

        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.parent = parent
        self.withdraw()
        self.title('Project Manager Profile Settings')
        self.sframe = tkinter.Frame(self)
        self.sframe.grid(column = 0, row = 0, sticky = "news")

        self.sframe.stitle = ttk.Label(self.sframe,
		style='title.TLabel', text = 'Profile')
        self.sframe.stitle.grid(column = 0, row = 0, sticky = 'news', padx = 5, pady = 5, columnspan = 2)
        self.sframe.sbar = ttk.Separator(self.sframe, orient='horizontal')
        self.sframe.sbar.grid(column = 0, row = 1, sticky = 'news', padx = 5, pady = 5, columnspan = 2)

        # Read profile JSON file
        self.prefsfile = os.path.expanduser('~/.open_pdks/prefs.json')

        if os.path.exists(self.prefsfile):
            with open(self.prefsfile, 'r') as f:
                prefs = json.load(f)
        else:
            prefs = {}

        # Default font size preference

        self.fontsize = tkinter.IntVar(self.sframe)
        self.sframe.lfsize = ttk.Label(self.sframe, text='Font size', style='blue.TLabel', anchor='e')
        self.sframe.fsize = ttk.Entry(self.sframe, textvariable=self.fontsize)
        self.sframe.lfsize.grid(column = 0, row = 2, sticky = 'news', padx = 5, pady = 5)
        self.sframe.fsize.grid(column = 1, row = 2, sticky = 'news', padx = 5, pady = 5)

        if 'fontsize' in prefs:
            self.fontsize.set(int(prefs['fontsize']))
        else:
            self.fontsize.set(11)

        # User name as written at the top of the project manager and characterization tools

        self.username = tkinter.StringVar(self.sframe)
        self.sframe.luser = ttk.Label(self.sframe, text='User name', style='blue.TLabel', anchor='e')
        self.sframe.user = ttk.Entry(self.sframe, textvariable=self.username)
        self.sframe.luser.grid(column = 0, row = 3, sticky = 'news', padx = 5, pady = 5)
        self.sframe.user.grid(column = 1, row = 3, sticky = 'news', padx = 5, pady = 5)

        if 'username' in prefs:
            self.username.set(prefs['username'])
        else:
            self.username.set(os.environ['USER'])

        # Graphics format for magic
        magicgraphics = ['X11', 'CAIRO', 'OPENGL']

        self.maggraph = tkinter.StringVar(self.sframe)
        self.maggraph.set(0)
        self.sframe.lmaggraph = ttk.Label(self.sframe, text='Layout editor graphics format', style='blue.TLabel', anchor='e')
        self.sframe.maggraph = ttk.OptionMenu(self.sframe, self.maggraph,
		self.maggraph.get(), *magicgraphics)

        self.sframe.lmaggraph.grid(column = 0, row = 4, sticky = 'news', padx = 5, pady = 5)
        self.sframe.maggraph.grid(column = 1, row = 4, sticky = 'news', padx = 5, pady = 5)

        if 'magic-graphics' in prefs:
            self.maggraph.set(prefs['magic-graphics'])
        else:
            self.maggraph.set('X11')

        # Choice of layout editor
        layouteditors = ['magic', 'klayout', 'electric']

        self.layouteditor = tkinter.StringVar(self.sframe)
        self.layouteditor.set(0)
        self.sframe.llayouteditor = ttk.Label(self.sframe, text='Layout editor', style='blue.TLabel', anchor='e')
        self.sframe.layouteditor = ttk.OptionMenu(self.sframe, self.layouteditor,
		self.layouteditor.get(), *layouteditors)

        self.sframe.llayouteditor.grid(column = 0, row = 5, sticky = 'news', padx = 5, pady = 5)
        self.sframe.layouteditor.grid(column = 1, row = 5, sticky = 'news', padx = 5, pady = 5)

        if 'layout-editor' in prefs:
            self.layouteditor.set(prefs['layout-editor'])
        else:
            self.layouteditor.set('magic')

        # Choice of schematic editor
        schemeditors = ['electric', 'xschem', 'xcircuit']

        self.schemeditor = tkinter.StringVar(self.sframe)
        self.schemeditor.set(0)
        self.sframe.lschemeditor = ttk.Label(self.sframe, text='Schematic editor', style='blue.TLabel', anchor='e')
        self.sframe.schemeditor = ttk.OptionMenu(self.sframe, self.schemeditor,
		self.schemeditor.get(), *schemeditors)

        self.sframe.lschemeditor.grid(column = 0, row = 6, sticky = 'news', padx = 5, pady = 5)
        self.sframe.schemeditor.grid(column = 1, row = 6, sticky = 'news', padx = 5, pady = 5)

        
        if 'schemeditor' in prefs:
            self.schemeditor.set(prefs['schemeditor'])
        else:
            self.schemeditor.set('electric')

        # Allow the project manager to list development PDKs and create projects
        # using them.

        self.development = tkinter.IntVar(self.sframe)
        self.sframe.ldev = ttk.Label(self.sframe, text='Create projects with development PDKs', style='blue.TLabel', anchor='e')
        self.sframe.dev = ttk.Checkbutton(self.sframe, variable=self.development)
        self.sframe.ldev.grid(column = 0, row = 7, sticky = 'news', padx = 5, pady = 5)
        self.sframe.dev.grid(column = 1, row = 7, sticky = 'news', padx = 5, pady = 5)

        if 'development' in prefs:
            self.development.set(True)
        else:
            self.development.set(False)

        # Allow the synthesis tool to list PDK development standard cell sets

        self.devstdcells = tkinter.IntVar(self.sframe)
        self.sframe.ldev = ttk.Label(self.sframe, text='Use development libraries for digital synthesis', style='blue.TLabel', anchor='e')
        self.sframe.dev = ttk.Checkbutton(self.sframe, variable=self.devstdcells)
        self.sframe.ldev.grid(column = 0, row = 8, sticky = 'news', padx = 5, pady = 5)
        self.sframe.dev.grid(column = 1, row = 8, sticky = 'news', padx = 5, pady = 5)

        if 'devstdcells' in prefs:
            self.devstdcells.set(True)
        else:
            self.devstdcells.set(False)

        # Button bar

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 1, sticky = "news")

        self.bbar.save_button = ttk.Button(self.bbar, text='Save',
		command=self.save, style = 'normal.TButton')
        self.bbar.save_button.grid(column=0, row=0, padx = 5)

        self.bbar.close_button = ttk.Button(self.bbar, text='Close',
		command=self.close, style = 'normal.TButton')
        self.bbar.close_button.grid(column=1, row=0, padx = 5)

    def save(self):
        # Create JSON record of options and write them to prefs.json
        with open(self.prefsfile, 'w') as f:
            prefs = {}
            prefs['fontsize'] = self.get_fontsize()
            prefs['username'] = self.get_username()
            prefs['schemeditor'] = self.get_schemeditor()
            prefs['magic-graphics'] = self.get_magic_graphics()
            prefs['development'] = self.get_development()
            prefs['devstdcells'] = self.get_devstdcells()
            json.dump(prefs, f, indent = 4)
        # Live-updates where easy. Due read_prefs, a magic-graphics takes effect immediately.
        self.parent.read_prefs()
        self.parent.refreshToolTips()

    def grid_configure(self, padx, pady):
        pass

    def redisplay(self):
        pass

    def get_fontsize(self):
        # return the fontsize value
        return self.fontsize.get()

    def get_username(self):
        # return the username
        return self.username.get()

    def get_schemeditor(self):
        # return the state of the "keep simulation files" checkbox
        return self.schemeditor.get()

    def get_magic_graphics(self):
        # return the format of graphics to use in Magic
        return self.maggraph.get()

    def get_development(self):
        # return the T/F value for creating projects with development PDKs
        return self.development.get()

    def get_devstdcells(self):
        # return the T/F value for synthesizing projects with development standard cells
        return self.devstdcells.get()

    def refresh(self):
        self.prefsfile = os.path.expanduser('~/.open_pdks/prefs.json')

        if os.path.exists(self.prefsfile):
            with open(self.prefsfile, 'r') as f:
                prefs = json.load(f)
        else:
            prefs = {}
        if 'fontsize' in prefs:
            self.fontsize.set(int(prefs['fontsize']))
        else:
            self.fontsize.set(11)
        if 'username' in prefs:
            self.username.set(prefs['username'])
        else:
            userid = os.environ['USER']
        if 'magic-graphics' in prefs:
            self.maggraph.set(prefs['magic-graphics'])
        else:
            self.maggraph.set('X11')
        if 'layout-editor' in prefs:
            self.layouteditor.set(prefs['layout-editor'])
        else:
            self.layouteditor.set('magic')
        if 'schemeditor' in prefs:
            self.schemeditor.set(prefs['schemeditor'])
        else:
            self.schemeditor.set('electric')
        if 'development' in prefs:
            self.development.set(True)
        else:
            self.development.set(False)
        if 'devstdcells' in prefs:
            self.devstdcells.set(True)
        else:
            self.devstdcells.set(False)
    
    def close(self):
        # pop down profile settings window
        self.withdraw()

    def open(self):
        # pop up profile settings window
        self.refresh()
        self.deiconify()
        self.lift()
