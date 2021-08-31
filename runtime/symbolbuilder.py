#!/usr/bin/env python3
#
#--------------------------------------------------------
# Symbol Builder for the project manager
#
#--------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# September 21, 2016
# Version 0.1
#--------------------------------------------------------

import tkinter
from tkinter import ttk

class SymbolBuilder(tkinter.Toplevel):
    """symbol builder."""

    def __init__(self, parent = None, pinlist = None, fontsize = 11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)
        self.transient(parent)
        self.parent = parent

        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')

        self.title('Symbol Builder')
        self.pframe = tkinter.Frame(self)
        self.pframe.grid(column = 0, row = 0, sticky = "news")

        self.pframe.pindisplay = tkinter.Text(self.pframe)
        self.pframe.pindisplay.pack(side = 'left', fill = 'y')
        # Add scrollbar to symbol builder window
        self.pframe.scrollbar = ttk.Scrollbar(self.pframe)
        self.pframe.scrollbar.pack(side='right', fill='y')
        # attach symbol builder window to scrollbar
        self.pframe.pindisplay.config(yscrollcommand = self.pframe.scrollbar.set)
        self.pframe.scrollbar.config(command = self.pframe.pindisplay.yview)

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 1, sticky = "news")
        self.bbar.cancel_button = ttk.Button(self.bbar, text='Cancel',
		command=self.close, style = 'normal.TButton')
        self.bbar.cancel_button.grid(column=0, row=0, padx = 5)

        self.bbar.okay_button = ttk.Button(self.bbar, text='Okay',
		command=self.okay, style = 'normal.TButton')
        self.bbar.okay_button.grid(column=1, row=0, padx = 5)

        typelist = ['input', 'output', 'inout', 'power', 'gnd']
        self.pinlist = []
        self.pvar = []
        self.result = None

        # Each pinlist entry is in the form <pin_name>:<type>
        # where <type> is one of "input", "output", "inout",
        # "power", or "gnd".

        n = 0
        for pin in pinlist:
            p = pin.split(':')
            pinname = p[0]
            pintype = p[1]

            newpvar = tkinter.StringVar(self.pframe.pindisplay)
            self.pinlist.append(pinname)
            self.pvar.append(newpvar)
            newpvar.set(pintype) 
            ttk.Label(self.pframe.pindisplay, text=pinname,
			style = 'normal.TButton').grid(row = n,
			column = 0, padx = 5, sticky = 'nsew')
            ttk.OptionMenu(self.pframe.pindisplay, newpvar,
			pintype, *typelist, style = 'blue.TMenubutton').grid(row = n,
			column = 1, padx = 5, sticky = 'nswe')
            n += 1

        self.grab_set()
        self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.initial_focus.focus_set()
        self.wait_window(self)

    def grid_configure(self, padx, pady):
        pass

    def okay(self):
        # return the new pin list.
        pinlist = []
        n = 0
        for p in self.pinlist:
            pinlist.append(p + ':' + str(self.pvar[n].get()))
            n += 1

        self.withdraw()
        self.update_idletasks()
        self.result = pinlist
        self.close()

    def close(self):
        # remove symbol builder window
        self.parent.focus_set()
        self.destroy()
