#!/usr/bin/env python3
#
#-----------------------------------------------------------
# Simulation hints management for the
# characterization tool
#-----------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# March 21, 2017
# Version 0.1
#--------------------------------------------------------

import re
import tkinter
from tkinter import ttk

class SimHints(tkinter.Toplevel):
    """Characterization tool simulation hints management."""

    def __init__(self, parent=None, fontsize = 11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)

        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.parent = parent
        self.withdraw()
        self.title('Simulation hints management')
        self.sframe = tkinter.Frame(self)
        self.sframe.grid(column = 0, row = 0, sticky = "news")

        self.sframe.stitle = ttk.Label(self.sframe,
		style='title.TLabel', text = 'Hints')
        self.sframe.stitle.pack(side = 'top', fill = 'x', expand = 'true')
        self.sframe.sbar = ttk.Separator(self.sframe, orient='horizontal')
        self.sframe.sbar.pack(side = 'top', fill = 'x', expand = 'true')

        self.sframe.curparam = ttk.Label(self.sframe,
		style='title.TLabel', text = 'None')
        self.sframe.curparam.pack(side = 'top', fill = 'x', expand = 'true')
        self.sframe.sbar2 = ttk.Separator(self.sframe, orient='horizontal')
        self.sframe.sbar2.pack(side = 'top', fill = 'x', expand = 'true')

        # Keep current parameter
        self.param = None

        #--------------------------------------------------------
        # reltol option
        #--------------------------------------------------------

        self.sframe.do_reltol = tkinter.Frame(self.sframe)
        self.sframe.do_reltol.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_reltol = tkinter.IntVar(self.sframe)
        self.do_reltol.set(0)
        self.sframe.do_reltol.enable = ttk.Checkbutton(self.sframe.do_reltol,
		text='Set reltol', variable = self.do_reltol,
		command=self.apply_reltol)
        self.sframe.do_reltol.value = ttk.Entry(self.sframe.do_reltol)
        self.sframe.do_reltol.value.delete(0, 'end')
        self.sframe.do_reltol.value.insert(0, '1.0E-3')
        # Return or leave window applies hint, if enabled
        self.sframe.do_reltol.value.bind('<Return>', self.apply_reltol)
        self.sframe.do_reltol.value.bind('<Leave>', self.apply_reltol)
        self.sframe.do_reltol.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_reltol.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------
        # rshunt option
        #--------------------------------------------------------

        self.sframe.do_rshunt = tkinter.Frame(self.sframe)
        self.sframe.do_rshunt.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_rshunt = tkinter.IntVar(self.sframe)
        self.do_rshunt.set(0)
        self.sframe.do_rshunt.enable = ttk.Checkbutton(self.sframe.do_rshunt,
		text='Use shunt resistance', variable = self.do_rshunt,
		command=self.apply_rshunt)
        self.sframe.do_rshunt.value = ttk.Entry(self.sframe.do_rshunt)
        self.sframe.do_rshunt.value.delete(0, 'end')
        self.sframe.do_rshunt.value.insert(0, '1.0E20')
        # Return or leave window applies hint, if enabled
        self.sframe.do_rshunt.value.bind('<Return>', self.apply_rshunt)
        self.sframe.do_rshunt.value.bind('<Leave>', self.apply_rshunt)
        self.sframe.do_rshunt.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_rshunt.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------
        # nodeset option
        #--------------------------------------------------------

        self.sframe.do_nodeset = tkinter.Frame(self.sframe)
        self.sframe.do_nodeset.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_nodeset = tkinter.IntVar(self.sframe)
        self.do_nodeset.set(0)
        self.sframe.do_nodeset.enable = ttk.Checkbutton(self.sframe.do_nodeset,
		text='Use nodeset', variable = self.do_nodeset,
		command=self.apply_nodeset)
        self.sframe.do_nodeset.value = ttk.Entry(self.sframe.do_nodeset)
        self.sframe.do_nodeset.value.delete(0, 'end')
        # Return or leave window applies hint, if enabled
        self.sframe.do_nodeset.value.bind('<Return>', self.apply_nodeset)
        self.sframe.do_nodeset.value.bind('<Leave>', self.apply_nodeset)
        self.sframe.do_nodeset.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_nodeset.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------
        # itl1 option
        #--------------------------------------------------------

        self.sframe.do_itl1 = tkinter.Frame(self.sframe)
        self.sframe.do_itl1.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_itl1 = tkinter.IntVar(self.sframe)
        self.do_itl1.set(0)
        self.sframe.do_itl1.enable = ttk.Checkbutton(self.sframe.do_itl1,
		text='Set gmin iterations', variable = self.do_itl1,
		command=self.apply_itl1)
        self.sframe.do_itl1.value = ttk.Entry(self.sframe.do_itl1)
        self.sframe.do_itl1.value.delete(0, 'end')
        self.sframe.do_itl1.value.insert(0, '100')
        # Return or leave window applies hint, if enabled
        self.sframe.do_itl1.value.bind('<Return>', self.apply_itl1)
        self.sframe.do_itl1.value.bind('<Leave>', self.apply_itl1)
        self.sframe.do_itl1.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_itl1.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------
        # include option
        # Disabled for now.  This needs to limit the selection of
        # files to include to a drop-down selection list.
        #--------------------------------------------------------
        self.sframe.do_include = tkinter.Frame(self.sframe)
        # self.sframe.do_include.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_include = tkinter.IntVar(self.sframe)
        self.do_include.set(0)
        self.sframe.do_include.enable = ttk.Checkbutton(self.sframe.do_include,
		text='Include netlist', variable = self.do_include,
		command=self.apply_include)
        self.sframe.do_include.value = ttk.Entry(self.sframe.do_include)
        self.sframe.do_include.value.delete(0, 'end')
        # Return or leave window applies hint, if enabled
        self.sframe.do_include.value.bind('<Return>', self.apply_include)
        self.sframe.do_include.value.bind('<Leave>', self.apply_include)
        self.sframe.do_include.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_include.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------
        # alternative method option
        #--------------------------------------------------------

        self.sframe.do_method = tkinter.Frame(self.sframe)
        self.sframe.do_method.pack(side = 'top', anchor = 'w', fill = 'x', expand = 'true')

        self.do_method = tkinter.IntVar(self.sframe)
        self.do_method.set(0)
        self.sframe.do_method.enable = ttk.Checkbutton(self.sframe.do_method,
		text='Use alternate method', variable = self.do_method,
		command=self.apply_method)
        self.sframe.do_method.value = ttk.Entry(self.sframe.do_method)
        self.sframe.do_method.value.delete(0, 'end')
        self.sframe.do_method.value.insert(0, '0')
        # Return or leave window applies hint, if enabled
        self.sframe.do_method.value.bind('<Return>', self.apply_method)
        self.sframe.do_method.value.bind('<Leave>', self.apply_method)
        self.sframe.do_method.enable.pack(side = 'left', anchor = 'w')
        self.sframe.do_method.value.pack(side = 'left', anchor = 'w', fill='x', expand='true')

        #--------------------------------------------------------

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 1, sticky = "news")

        self.bbar.apply_button = ttk.Button(self.bbar, text='Apply',
		command=self.apply_hints, style = 'normal.TButton')
        self.bbar.apply_button.grid(column=0, row=0, padx = 5)

        self.bbar.close_button = ttk.Button(self.bbar, text='Close',
		command=self.close, style = 'normal.TButton')
        self.bbar.close_button.grid(column=1, row=0, padx = 5)

    def apply_reltol(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_reltol = self.do_reltol.get()
        if have_reltol:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['reltol'] = self.sframe.do_reltol.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('reltol', None)
            
    def apply_rshunt(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_rshunt = self.do_rshunt.get()
        if have_rshunt:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['rshunt'] = self.sframe.do_rshunt.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('rshunt', None)
            
    def apply_itl1(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_itl1 = self.do_itl1.get()
        if have_itl1:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['itl1'] = self.sframe.do_itl1.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('itl1', None)
            

    def apply_nodeset(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_nodeset = self.do_nodeset.get()
        if have_nodeset:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['nodeset'] = self.sframe.do_nodeset.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('nodeset', None)
            
    def apply_include(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_include = self.do_include.get()
        if have_include:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['include'] = self.sframe.do_include.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('include', None)
            
    def apply_method(self, value = ''):
        # "value" is passed from binding callback but is not used
        have_method = self.do_method.get()
        if have_method:
            if not 'hints' in self.param:
                phints = {}
            else:
                phints = self.param['hints']
            phints['method'] = self.sframe.do_method.value.get()
            self.param['hints'] = phints
        else:
            if 'hints' in self.param:
                self.param['hints'].pop('method', None)

    def apply_hints(self, value = ''):
        self.apply_reltol(value)
        self.apply_rshunt(value)
        self.apply_itl1(value)
        self.apply_nodeset(value)
        self.apply_include(value)
        self.apply_method(value)

        # Update 'Simulate' button in characterization tool with a mark
        # indicating hints are present.  Also remove the hints record
        # from the parameter dictionary if it is empty.
        if 'method' in self.param:
            if 'hints' in self.param:
                if self.param['hints'] == {}:
                    self.param.pop('hints', None)
                    simtext = 'Simulate'
                else:
                    simtext = '\u2022Simulate'
            else:
                simtext = 'Simulate'
            self.simbutton.config(text=simtext)

    def grid_configure(self, padx, pady):
        pass

    def redisplay(self):
        pass

    def populate(self, param, simbutton = False):
        if 'display' in param:
            self.sframe.curparam.config(text=param['display'])
        else:
            self.sframe.curparam.config(text=param['method'])

        # Set the current parameter
        self.param = param

        # Remember the simulate button so we can mark or unmark hints
        self.simbutton = simbutton

        # Regenerate view and update for the indicated param.
        if 'hints' in param:
            phints = param['hints']
            if 'reltol' in phints:
                # (1) Reltol adjustment
                self.do_reltol.set(1)
                self.sframe.do_reltol.value.delete(0, 'end')
                self.sframe.do_reltol.value.insert(0, phints['reltol'])
            else:
                self.do_reltol.set(0)
            if 'rshunt' in phints:
                # (2) Gshunt option
                self.do_rshunt.set(1)
                self.sframe.do_rshunt.value.delete(0, 'end')
                self.sframe.do_rshunt.value.insert(0, phints['rshunt'])
            else:
                self.do_rshunt.set(0)
            if 'nodeset' in phints:
                # (3) Nodeset
                self.do_nodeset.set(1)
                self.sframe.do_nodeset.value.delete(0, 'end')
                self.sframe.do_nodeset.value.insert(0, phints['nodeset'])
            else:
                self.do_nodeset.set(0)
            if 'itl1' in phints:
                # (4) Gmin iterations (ITL1)
                self.do_itl1.set(1)
                self.sframe.do_itl1.value.delete(0, 'end')
                self.sframe.do_itl1.value.insert(0, phints['itl1'])
            else:
                self.do_itl1.set(0)
            if 'include' in phints:
                # (5) Include library (from dropdown list)
                self.do_include.set(1)
                self.sframe.do_include.value.delete(0, 'end')
                self.sframe.do_include.value.insert(0, phints['include'])
            else:
                self.do_include.set(0)
            if 'method' in phints:
                # (6) Alternative method (where indicated)
                self.do_method.set(1)
                self.sframe.do_method.value.delete(0, 'end')
                self.sframe.do_method.value.insert(0, phints['method'])
            else:
                self.do_method.set(0)
        else:
            # No hints, so set everything to unchecked
            self.do_reltol.set(0)
            self.do_rshunt.set(0)
            self.do_nodeset.set(0)
            self.do_itl1.set(0)
            self.do_include.set(0)
            self.do_method.set(0)

    def close(self):
        # pop down settings window
        self.withdraw()

    def open(self):
        # pop up settings window
        self.deiconify()
        self.lift()
