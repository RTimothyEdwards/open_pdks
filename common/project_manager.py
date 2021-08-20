#!/usr/bin/env python3 -B
#
#--------------------------------------------------------
# Open Galaxy Project Manager GUI.
#
# This is a Python tkinter script that handles local
# project management.  It is meant as a replacement for
# appsel_zenity.sh
#
#--------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# September 9, 2016
# Modifications 2017, 2018
# Version 1.0
#--------------------------------------------------------

import sys
# Require python 3.5.x (and not python 3.6.x). Without this trap here, in several
# instances of VMs where /usr/bin/python3 symlinked to 3.6.x by mistake, it manifests
# as (misleading) errors like: ImportError: No module named 'yaml'
#
# '%x' % sys.hexversion  ->  '30502f0'

import tkinter
from tkinter import ttk, StringVar, Listbox, END
from tkinter import filedialog

# globals
theProg = sys.argv[0]
root = tkinter.Tk()      # WARNING: must be exactly one instance of Tk; don't call again elsewhere

# 4 configurations based on booleans: splash,defer
# n,n:  no splash, show only form when completed: LEGACY MODE, user confused by visual lag.
# n,y:  no splash but defer projLoad: show an empty form ASAP
# y,n:  yes splash, and wait for projLoad before showing completed form
# y,y:  yes splash, but also defer projLoad: show empty form ASAP

# deferLoad = False        # LEGACY: no splash, and wait for completed form
# doSplash = False

deferLoad = True         # True: display GUI before (slow) loading of projects, so no splash:
doSplash = not deferLoad # splash IFF GUI-construction includes slow loading of projects

# deferLoad = False        # load projects before showing form, so need splash:
# doSplash = not deferLoad # splash IFF GUI-construction includes slow loading of projects

# deferLoad = True         # here keep splash also, despite also deferred-loading
# doSplash = True

#------------------------------------------------------
# Splash screen: display ASAP: BEFORE bulk of imports.
#------------------------------------------------------

class SplashScreen(tkinter.Toplevel):
    """Project Management Splash Screen"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        parent.withdraw()
        #EFABLESS PLATFORM
        #image = tkinter.PhotoImage(file="/ef/efabless/opengalaxy/og_splashscreen50.gif")
        label = ttk.Label(self, image=image)
        label.pack()

        # required to make window show before the program gets to the mainloop
        self.update_idletasks()

import faulthandler
import signal

# SplashScreen here. fyi: there's a 2nd/later __main__ section for main app
splash = None     # a global
if __name__ == '__main__':
    faulthandler.register(signal.SIGUSR2)
    if doSplash:
        splash = SplashScreen(root)

import io
import os
import re
import json
import yaml
import shutil
import tarfile
import datetime
import subprocess
import contextlib
import tempfile
import glob

import tksimpledialog
import tooltip
from rename_project import rename_project_all
#from fix_libdirs import fix_libdirs
from consoletext import ConsoleText
from helpwindow import HelpWindow
from treeviewchoice import TreeViewChoice
from symbolbuilder import SymbolBuilder
from make_icon_from_soft import create_symbol
from profile import Profile

import config

# Global name for design directory
designdir = 'design'
# Global name for import directory
importdir = 'import'
# Global name for cloudv directory
cloudvdir = 'cloudv'
# Global name for archived imports project sub-directory
archiveimportdir = 'imported'
# Global name for current design file
#EFABLESS PLATFORM
currdesign = '~/.open_pdks/currdesign'
prefsfile = '~/.open_pdks/prefs.json'


#---------------------------------------------------------------
# Watch a directory for modified time change.  Repeat every two
# seconds.  Call routine callback() if a change occurs
#---------------------------------------------------------------

class WatchClock(object):
    def __init__(self, parent, path, callback, interval=2000, interval0=None):
        self.parent = parent
        self.callback = callback
        self.path = path
        self.interval = interval
        if interval0 != None:
            self.interval0 = interval0
            self.restart(first=True)
        else:
            self.interval0 = interval
            self.restart()

    def query(self):
        for entry in self.path:
            statbuf = os.stat(entry)
            if statbuf.st_mtime > self.reftime:
                self.callback()
                self.restart()
                return
        self.timer = self.parent.after(self.interval, self.query)

    def stop(self):
        self.parent.after_cancel(self.timer)

    # if first: optionally use different (typically shorter) interval, AND DON'T
    # pre-record watched-dir mtime-s (which forces the callback on first timer fire)
    def restart(self, first=False):
        self.reftime = 0
        if not first:
            for entry in self.path:
                statbuf = os.stat(entry)
                if statbuf.st_mtime > self.reftime:
                    self.reftime = statbuf.st_mtime
        self.timer = self.parent.after(self.interval0 if first and self.interval0 != None else self.interval, self.query)

#------------------------------------------------------
# Dialog for generating a new layout
#------------------------------------------------------

class NewLayoutDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed=''):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')

        self.l1prefs = tkinter.IntVar(master)
        self.l1prefs.set(1)
        ttk.Checkbutton(master, text='Populate new layout from netlist',
			variable = self.l1prefs).grid(row = 2, columnspan = 2, sticky = 'enws')

        return self

    def apply(self):
        return self.l1prefs.get

#------------------------------------------------------
# Simple dialog for entering project names
#------------------------------------------------------

class ProjectNameDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed=''):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        ttk.Label(master, text='Enter new project name:').grid(row = 1, column = 0, sticky = 'wns')
        self.nentry = ttk.Entry(master)
        self.nentry.grid(row = 1, column = 1, sticky = 'ewns')
        self.nentry.insert(0, seed)
        return self.nentry # initial focus

    def apply(self):
        return self.nentry.get()

class PadFrameCellNameDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed=''):
        description='PadFrame'       # TODO: make this an extra optional parameter of a generic CellNameDialog?
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        if description:
            description = description + " "
        else:
            description = ""
        ttk.Label(master, text=("Enter %scell name:" %(description))).grid(row = 1, column = 0, sticky = 'wns')
        self.nentry = ttk.Entry(master)
        self.nentry.grid(row = 1, column = 1, sticky = 'ewns')
        self.nentry.insert(0, seed)
        return self.nentry # initial focus

    def apply(self):
        return self.nentry.get()

#------------------------------------------------------
# Dialog for copying projects.  Includes checkbox
# entries for preferences.
#------------------------------------------------------

class CopyProjectDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed=''):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        ttk.Label(master, text="Enter new project name:").grid(row = 1, column = 0, sticky = 'wns')
        self.nentry = ttk.Entry(master)
        self.nentry.grid(row = 1, column = 1, sticky = 'ewns')
        self.nentry.insert(0, seed)
        self.elprefs = tkinter.IntVar(master)
        self.elprefs.set(0)
        ttk.Checkbutton(master, text='Copy electric preferences (not recommended)',
			variable = self.elprefs).grid(row = 2, columnspan = 2, sticky = 'enws')
        self.spprefs = tkinter.IntVar(master)
        self.spprefs.set(0)
        ttk.Checkbutton(master, text='Copy ngspice folder (not recommended)',
			variable = self.spprefs).grid(row = 3, columnspan = 2, sticky = 'enws')
        return self.nentry # initial focus

    def apply(self):
        # Return a list containing the entry text and the checkbox states.
        elprefs = True if self.elprefs.get() == 1 else False
        spprefs = True if self.spprefs.get() == 1 else False
        return [self.nentry.get(), elprefs, spprefs]

#-------------------------------------------------------
# Not-Quite-So-Simple dialog for entering a new project.
# Select a project name and a PDK from a drop-down list.
#-------------------------------------------------------

class NewProjectDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed='', importnode=None, development=False, parent_pdk=''):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        ttk.Label(master, text="Enter new project name:").grid(row = 1, column = 0)
        self.nentry = ttk.Entry(master)
        self.nentry.grid(row = 1, column = 1, sticky = 'ewns')
        self.nentry.insert(0, seed or '')      # may be None
        self.pvar = tkinter.StringVar(master)
        if not importnode:
            # Add PDKs as found by searching /ef/tech for 'libs.tech' directories
            ttk.Label(master, text="Select foundry/node:").grid(row = 2, column = 0)
        else:
            ttk.Label(master, text="Foundry/node:").grid(row = 2, column = 0)
        self.infolabel = ttk.Label(master, text="", style = 'brown.TLabel', wraplength=250)
        self.infolabel.grid(row = 3, column = 0, columnspan = 2, sticky = 'news')
        self.pdkmap = {}
        self.pdkdesc = {}
        self.pdkstat = {}
        pdk_def = None

        node_def = importnode
        if not node_def:
            node_def = "EFXH035B"

        # use glob instead of os.walk. Don't need to recurse large PDK hier.
        # TODO: stop hardwired default EFXH035B: get from an overall flow /ef/tech/.ef-config/plist.json
        # (or get it from the currently selected project)
        #EFABLESS PLATFORM
        #TODO: Replace with PREFIX
        for pdkdir_lr in glob.glob('/usr/share/pdk/*/libs.tech/'):
            pdkdir = os.path.split( os.path.split( pdkdir_lr )[0])[0]    # discard final .../libs.tech/
            (foundry, foundry_name, node, desc, status) = ProjectManager.pdkdir2fnd( pdkdir )
            if not foundry or not node:
                continue
            key = foundry + '/' + node
            self.pdkmap[key] = pdkdir
            self.pdkdesc[key] = desc
            self.pdkstat[key] = status
            if node == node_def and not pdk_def:
                pdk_def = key
            
        # Quick hack:  sorting puts EFXH035A before EFXH035LEGACY.  However, some
        # ranking is needed.
        pdklist = sorted( self.pdkmap.keys())
        if not pdklist:
            raise ValueError( "assertion failed, no available PDKs found")
        pdk_def = (pdk_def or pdklist[0])

        if parent_pdk != '':
            pdk_def = parent_pdk
            
        self.pvar.set(pdk_def)

        # Restrict list to single entry if importnode was non-NULL and
        # is in the PDK list (OptionMenu is replaced by a simple label)
        # Otherwise, restrict the list to entries having an "status"
        # entry equal to "active".  This allows some legacy PDKs to be
	# disabled for creating new projects (but available for projects
        # that already have them).
        
        if importnode or parent_pdk != '':
            self.pdkselect = ttk.Label(master, text = pdk_def, style='blue.TLabel')
        else:
            pdkactive = list(item for item in pdklist if self.pdkstat[item] == 'active')
            if development:
                pdkactive.extend(list(item for item in pdklist if self.pdkstat[item] == 'development'))
            self.pdkselect = ttk.OptionMenu(master, self.pvar, pdk_def, *pdkactive,
    			style='blue.TMenubutton', command=self.show_info)
        self.pdkselect.grid(row = 2, column = 1)
        self.show_info(0)

        return self.nentry # initial focus

    def show_info(self, args):
        key = str(self.pvar.get())
        desc = self.pdkdesc[key]
        if desc == '':
            self.infolabel.config(text='(no description available)')
        else:
            self.infolabel.config(text=desc)

    def apply(self):
        return self.nentry.get(), self.pdkmap[ str(self.pvar.get()) ]  # Note converts StringVar to string

#----------------------------------------------------------------
# Not-Quite-So-Simple dialog for selecting an existing project.
# Select a project name from a drop-down list.  This could be
# replaced by simply using the selected (current) project.
#----------------------------------------------------------------

class ExistingProjectDialog(tksimpledialog.Dialog):
    def body(self, master, plist, seed, warning='Enter name of existing project to import into:'):
        ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')

        # Alphebetize list
        plist.sort()
        # Add projects
        self.pvar = tkinter.StringVar(master)
        self.pvar.set(plist[0])

        ttk.Label(master, text='Select project:').grid(row = 1, column = 0)

        self.projectselect = ttk.OptionMenu(master, self.pvar, plist[0], *plist, style='blue.TMenubutton')
        self.projectselect.grid(row = 1, column = 1, sticky = 'ewns')
        # pack version (below) hangs. Don't know why, changed to grid (like ProjectNameDialog)
        # self.projectselect.pack(side = 'top', fill = 'both', expand = 'true')
        return self.projectselect # initial focus

    def apply(self):
        return self.pvar.get()  # Note converts StringVar to string

#----------------------------------------------------------------
# Not-Quite-So-Simple dialog for selecting an existing ElecLib of existing project.
# Select an elecLib name from a drop-down list.
#----------------------------------------------------------------

class ExistingElecLibDialog(tksimpledialog.Dialog):
    def body(self, master, plist, seed):
        warning = "Enter name of existing Electric library to import into:"
        ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')

        # Alphebetize list
        plist.sort()
        # Add electric libraries
        self.pvar = tkinter.StringVar(master)
        self.pvar.set(plist[0])

        ttk.Label(master, text="Select library:").grid(row = 1, column = 0)

        self.libselect = ttk.OptionMenu(master, self.pvar, plist[0], *plist, style='blue.TMenubutton')
        self.libselect.grid(row = 1, column = 1)
        return self.libselect # initial focus

    def apply(self):
        return self.pvar.get()  # Note converts StringVar to string

#----------------------------------------------------------------
# Dialog for layout, in case of multiple layout names, none of
# which matches the project name (ip-name).  Method: Select a
# layout name from a drop-down list.  If there is no project.json
# file, add a checkbox for creating one and seeding the ip-name
# with the name of the selected layout.  Include entry for
# new layout, and for new layouts add a checkbox to import the
# layout from schematic or verilog, if a valid candidate exists.
#----------------------------------------------------------------

class EditLayoutDialog(tksimpledialog.Dialog):
    def body(self, master, plist, seed='', ppath='', pname='', warning='', hasnet=False):
        ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        self.ppath = ppath
        self.pname = pname

        # Checkbox variable
        self.confirm = tkinter.IntVar(master)
        self.confirm.set(0)

        # To-Do:  Add checkbox for netlist import

        # Alphebetize list
        plist.sort()
        # Add additional item for new layout
        plist.append('(New layout)')

        # Add layouts to list
        self.pvar = tkinter.StringVar(master)
        self.pvar.set(plist[0])

        ttk.Label(master, text='Selected layout to edit:').grid(row = 1, column = 0)

        if pname in plist:
            pseed = plist.index(pname)
        else:
            pseed = 0

        self.layoutselect = ttk.OptionMenu(master, self.pvar, plist[pseed], *plist,
				style='blue.TMenubutton', command=self.handle_choice)
        self.layoutselect.grid(row = 1, column = 1, sticky = 'ewns')

        # Create an entry form and checkbox for entering a new layout name, but
        # keep them unpacked unless the "(New layout)" selection is chosen.

        self.layoutbox = ttk.Frame(master)
        self.layoutlabel = ttk.Label(self.layoutbox, text='New layout name:')
        self.layoutlabel.grid(row = 0, column = 0, sticky = 'ewns')
        self.layoutentry = ttk.Entry(self.layoutbox)
        self.layoutentry.grid(row = 0, column = 1, sticky = 'ewns')
        self.layoutentry.insert(0, pname)

        # Only allow 'makeproject' checkbox if there is no project.json file
        jname = ppath + '/project.json'
        if not os.path.exists(jname):
            self.makeproject = ttk.Checkbutton(self.layoutbox,
			text='Make default project name',
			variable = self.confirm)
            self.makeproject.grid(row = 2, column = 0, columnspan = 2, sticky = 'ewns')
        return self.layoutselect # initial focus

    def handle_choice(self, event):
        if self.pvar.get() == '(New layout)':
            # Add entry and checkbox for creating ad-hoc project.json file
            self.layoutbox.grid(row = 1, column = 0, columnspan = 2, sticky = 'ewns')
        else:
            # Remove entry and checkbox
            self.layoutbox.grid_forget()
        return

    def apply(self):
        if self.pvar.get() == '(New layout)':
            if self.confirm.get() == 1:
                pname = self.pname
                master.create_ad_hoc_json(self.layoutentry.get(), pname)
            return self.layoutentry.get()
        else:
            return self.pvar.get()  # Note converts StringVar to string

#----------------------------------------------------------------
# Dialog for padframe: select existing ElecLib of existing project, type in a cellName.
#   Select an elecLib name from a drop-down list.
#   Text field for entry of a cellName.
#----------------------------------------------------------------

class ExistingElecLibCellDialog(tksimpledialog.Dialog):
    def body(self, master, descPre, seed='', descPost='', plist=None, seedLibNm=None, seedCellNm=''):
        warning = 'Pick existing Electric library; enter cell name'
        warning = (descPre or '') + ((descPre and ': ') or '') + warning + ((descPost and ' ') or '') + (descPost or '')
        ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')

        # Alphebetize list
        plist.sort()
        # Add electric libraries
        self.pvar = tkinter.StringVar(master)
        pNdx = 0
        if seedLibNm and seedLibNm in plist:
            pNdx = plist.index(seedLibNm)
        self.pvar.set(plist[pNdx])

        ttk.Label(master, text='Electric library:').grid(row = 1, column = 0, sticky = 'ens')
        self.libselect = ttk.OptionMenu(master, self.pvar, plist[pNdx], *plist, style='blue.TMenubutton')
        self.libselect.grid(row = 1, column = 1, sticky = 'wns')

        ttk.Label(master, text=('cell name:')).grid(row = 2, column = 0, sticky = 'ens')
        self.nentry = ttk.Entry(master)
        self.nentry.grid(row = 2, column = 1, sticky = 'ewns')
        self.nentry.insert(0, seedCellNm)

        return self.libselect # initial focus

    def apply(self):
        # return list of 2 strings: selected ElecLibName, typed-in cellName.
        return [self.pvar.get(), self.nentry.get()]  # Note converts StringVar to string

#------------------------------------------------------
# Simple dialog for confirming anything.
#------------------------------------------------------

class ConfirmDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        return self

    def apply(self):
        return 'okay'

#------------------------------------------------------
# More proactive dialog for confirming an invasive
# procedure like "delete project".  Requires user to
# click a checkbox to ensure this is not a mistake.
# confirmPrompt can be overridden, default='I am sure I want to do this.'
#------------------------------------------------------

class ProtectedConfirmDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed='', confirmPrompt=None):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        self.confirm = tkinter.IntVar(master)
        self.confirm.set(0)
        if not confirmPrompt:
            confirmPrompt='I am sure I want to do this.'
        ttk.Checkbutton(master, text=confirmPrompt,
			variable = self.confirm).grid(row = 1, columnspan = 2, sticky = 'enws')
        return self

    def apply(self):
        return 'okay' if self.confirm.get() == 1 else ''

#------------------------------------------------------
# Simple dialog to say "blah is not implemented yet."
#------------------------------------------------------

class NotImplementedDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed):
        if not warning:
            warning = "Sorry, that feature is not implemented yet"
        if warning:
            warning = "Sorry, " + warning + ", is not implemented yet"
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        return self

    def apply(self):
        return 'okay'

#------------------------------------------------------
# (This is actually a generic confirm dialogue, no install/overwrite intelligence)
# But so far dedicated to confirming the installation of one or more files,
# with notification of which (if any) will overwrite existing files.
#
# The warning parameter is fully constructed by caller, as multiple lines as either:
#   For the import of module 'blah',
#   CONFIRM installation of (*: OVERWRITE existing):
#    * path1
#      path2
#      ....
# or:
#   For the import of module 'blah',
#   CONFIRM installation of:
#      path1
#      path2
#      ....
# TODO: bastardizes warning parameter as multiple lines. Implement some other way?
#------------------------------------------------------

class ConfirmInstallDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed):
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        return self

    def apply(self):
        return 'okay'

#------------------------------------------------------
# Dialog to import a project into the project manager
#------------------------------------------------------

class ImportDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed, parent_pdk, parent_path, project_dir):
        self.badrex1 = re.compile("^\.")
        self.badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        
        self.projectpath = ""
        self.project_pdkdir = ""
        self.foundry = ""
        self.node = ""
        self.parentpdk = parent_pdk
        self.parentpath = parent_path
        self.projectdir = project_dir #folder that contains all projects
        
        if warning:
            ttk.Label(master, text=warning, wraplength=250).grid(row = 0, columnspan = 2, sticky = 'wns')
        ttk.Label(master, text="Enter new project name:").grid(row = 1, column = 0)
        
        self.entry_v = tkinter.StringVar()
        
        self.nentry = ttk.Entry(master, textvariable = self.entry_v)
        self.nentry.grid(row = 1, column = 1, sticky = 'ewns')
        
        self.entry_v.trace('w', self.text_validate)
        

        ttk.Button(master,
                        text = "Choose Project...",
                        command = self.browseFiles).grid(row = 3, column = 0)
                        
        self.pathlabel = ttk.Label(master, text = ("No project selected" if self.projectpath =="" else self.projectpath), style = 'red.TLabel', wraplength=300)
        
        self.pathlabel.grid(row = 3, column = 1)
        
        ttk.Label(master, text="Foundry/node:").grid(row = 4, column = 0)
        
        self.pdklabel = ttk.Label(master, text="N/A", style = 'red.TLabel')
        self.pdklabel.grid(row = 4, column = 1)
        
        self.importoption = tkinter.StringVar()
        
        self.importoption.set(("copy" if parent_pdk!='' else "link"))
        
        self.linkbutton = ttk.Radiobutton(master, text="Make symbolic link", variable=self.importoption, value="link")
        self.linkbutton.grid(row = 5, column = 0)
        ttk.Radiobutton(master, text="Copy project", variable=self.importoption, value="copy").grid(row = 5, column = 1)
        
        self.error_label = ttk.Label(master, text="", style = 'red.TLabel', wraplength=300)
        self.error_label.grid(row = 6, column = 0, columnspan = 2)
        
        self.entry_error = ttk.Label(master, text="", style = 'red.TLabel', wraplength=300)
        self.entry_error.grid(row = 2, column = 0, columnspan = 2)
        
        return self.nentry
    
    def text_validate(self, *args):
        newname = self.entry_v.get()
        projectpath = ''
        if self.parentpath!='':
            projectpath = self.parentpath + '/subcells/' + newname
        else:
            projectpath = self.projectdir + '/' + newname
             
        if ProjectManager.blacklisted( newname):
            self.entry_error.configure(text = newname + ' is not allowed for a project name.')
        elif newname == "":
            self.entry_error.configure(text = "")
        elif self.badrex1.match(newname):
            self.entry_error.configure(text =  'project name may not start with "."')
        elif self.badrex2.match(newname):
            self.entry_error.configure(text = 'project name contains illegal characters or whitespace.')
        elif os.path.exists(projectpath):
            self.entry_error.configure(text = newname + ' is already a project name.')
        else:
            self.entry_error.configure(text = '')
            return True
        return False
        
    def validate(self, *args):
        return self.text_validate(self) and self.pdk_validate(self)
        
    def browseFiles(self):
        initialdir = "~/"
        if os.path.isdir(self.projectpath):
            initialdir = os.path.split(self.projectpath)[0]
            
        selected_dir = filedialog.askdirectory(initialdir = initialdir, title = "Select a Project to Import",)
                                          
        if os.path.isdir(str(selected_dir)):
            self.error_label.configure(text = '')
            self.linkbutton.configure(state="normal")
            
            self.projectpath = selected_dir
            self.pathlabel.configure(text=self.projectpath, style = 'blue.TLabel')
            # Change label contents
            if (self.nentry.get() == ''):
                self.nentry.insert(0, os.path.split(self.projectpath)[1])
                
            self.pdk_validate(self)
    
    def pdk_validate(self, *args):
        if not os.path.exists(self.projectpath):
            self.error_label.configure(text = 'Invalid directory')
            return False
        
        if self.parentpath != "" and self.projectpath in self.parentpath:
            self.error_label.configure(text = 'Cannot import a parent directory into itself.')
            return False
        #Find project pdk
        if os.path.exists(self.projectpath + '/.config/techdir') or os.path.exists(self.projectpath + '/.ef-config/techdir'):
            self.project_pdkdir = os.path.realpath(self.projectpath + ProjectManager.config_path( self.projectpath) + '/techdir')
            self.foundry, foundry_name, self.node, desc, status = ProjectManager.pdkdir2fnd( self.project_pdkdir )
        else:
            if not os.path.exists(self.projectpath + '/info.yaml'):
                self.error_label.configure(text = self.projectpath + ' does not contain an info.yaml file.')
                self.project_pdkdir = ""
                self.foundry = ""
                self.node = ""
            else:                    
                self.project_pdkdir, self.foundry, self.node = ProjectManager.get_import_pdk( self.projectpath)
            
        if self.project_pdkdir == "":
            self.pdklabel.configure(text="Not found", style='red.TLabel')
            return False
        else:
            if (self.parentpdk!="" and self.parentpdk != self.foundry + '/' + self.node):
                self.importoption.set("copy")
                self.linkbutton.configure(state="disabled")
                self.error_label.configure(text = 'Warning: Parent project uses '+self.parentpdk+' instead of '+self.foundry + '/' + self.node+'. The imported project will be copied and cleaned.')
            self.pdklabel.configure(text=self.foundry + '/' + self.node, style='blue.TLabel')     
            return True
        
    
    def apply(self):
        return self.nentry.get(), self.project_pdkdir, self.projectpath, self.importoption.get()
    
#------------------------------------------------------
# Dialog to allow users to select a flow
#------------------------------------------------------
    
class SelectFlowDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed='', is_subproject = False):
        self.wait_visibility()
        if warning:
            ttk.Label(master, text=warning).grid(row = 0, columnspan = 2, sticky = 'wns')
        
        ttk.Label(master, text="Flow:").grid(row = 1, column = 0)
        
        project_flows = {
            'Analog':'Schematic, Simulation, Layout, DRC, LVS',
            'Digital':'Preparation, Synthesis, Placement, Static Timing Analysis, Routing, Post-Route STA, Migration, DRC, LVS, GDS, Cleanup',
            'Mixed-Signal':'',
            'Assembly':'',
        }
        
        subproject_flows = {
            'Analog':'Schematic, Simulation, Layout, DRC, LVS',
            'Digital':'Preparation, Synthesis, Placement, Static Timing Analysis, Routing, Post-Route STA, Migration, DRC, LVS, GDS, Cleanup',
            'Mixed-Signal': '',
        }
        self.flows = subproject_flows if is_subproject else project_flows
        self.flowvar = tkinter.StringVar(master, value = 'Analog')
        
        self.infolabel = ttk.Label(master, text=self.flows[self.flowvar.get()], style = 'brown.TLabel', wraplength=250)
        self.infolabel.grid(row = 2, column = 0, columnspan = 2, sticky = 'news')
        
        self.option_menu = ttk.OptionMenu(
            master,
            self.flowvar,
            self.flowvar.get(),
            *self.flows.keys(),
            command=self.show_info
        )
        
        self.option_menu.grid(row = 1, column = 1)

        return self.option_menu# initial focus
    
    def show_info(self, args):
        key = self.flowvar.get()
        print(key)
        desc = self.flows[key]
        if desc == '':
            self.infolabel.config(text='(no description available)')
        else:
            self.infolabel.config(text=desc)
    

    def apply(self):
        return str(self.flowvar.get())  # Note converts StringVar to string
        
#------------------------------------------------------
# Project Manager class
#------------------------------------------------------

class ProjectManager(ttk.Frame):
    """Project Management GUI."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent
        parent.withdraw()
        # self.update()
        self.update_idletasks()     # erase small initial frame asap
        self.init_gui()
        parent.protocol("WM_DELETE_WINDOW", self.on_quit)
        if splash:
            splash.destroy()
        parent.deiconify()

    def on_quit(self):
        """Exits program."""
        quit()

    def init_gui(self):
        """Builds GUI."""
        global designdir
        global importdir
        global archiveimportdir
        global currdesign
        global theProg
        global deferLoad

        message = []
        allPaneOpen = False
        prjPaneMinh = 10
        iplPaneMinh = 4
        impPaneMinh = 4

        # if deferLoad:         # temp. for testing... open all panes
        #     allPaneOpen = True

        # Read user preferences
        self.prefs = {}
        self.read_prefs()

        # Get default font size from user preferences
        fontsize = self.prefs['fontsize']

        s = ttk.Style()
        available_themes = s.theme_names()
        # print("themes: " + str(available_themes))
        s.theme_use(available_themes[0])

        s.configure('gray.TFrame', background='gray40')
        s.configure('blue_white.TFrame', bordercolor = 'blue', borderwidth = 3)
        s.configure('italic.TLabel', font=('Helvetica', fontsize, 'italic'))
        s.configure('title.TLabel', font=('Helvetica', fontsize, 'bold italic'),
                        foreground = 'brown', anchor = 'center')
        s.configure('title2.TLabel', font=('Helvetica', fontsize, 'bold italic'),
                        foreground = 'blue')
        s.configure('normal.TLabel', font=('Helvetica', fontsize))
        s.configure('red.TLabel', font=('Helvetica', fontsize), foreground = 'red')
        s.configure('brown.TLabel', font=('Helvetica', fontsize), foreground = 'brown3', background = 'gray95')
        s.configure('green.TLabel', font=('Helvetica', fontsize), foreground = 'green3')
        s.configure('blue.TLabel', font=('Helvetica', fontsize), foreground = 'blue')
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')
        s.configure('red.TButton', font=('Helvetica', fontsize), foreground = 'red', border = 3,
                        relief = 'raised')
        s.configure('green.TButton', font=('Helvetica', fontsize), foreground = 'green3', border = 3,
                        relief = 'raised')
        s.configure('blue.TMenubutton', font=('Helvetica', fontsize), foreground = 'blue', border = 3,
			relief = 'raised')

        # Create the help window
        self.help = HelpWindow(self, fontsize=fontsize)
        
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            self.help.add_pages_from_file(config.apps_path + '/manager_help.txt')
            message = buf.getvalue()
        

        # Set the help display to the first page
        self.help.page(0)

        # Create the profile settings window
        self.profile = Profile(self, fontsize=fontsize)

        # Variables used by option menus
        self.seltype = tkinter.StringVar(self)
        self.cur_project = tkinter.StringVar(self)
        self.cur_import = "(nothing selected)"
        self.project_name = ""

        # Root window title
        self.root.title('Project Manager')
        self.root.option_add('*tearOff', 'FALSE')
        self.pack(side = 'top', fill = 'both', expand = 'true')

        pane = tkinter.PanedWindow(self, orient = 'vertical', sashrelief='groove', sashwidth=6)
        pane.pack(side = 'top', fill = 'both', expand = 'true')
        self.toppane = ttk.Frame(pane)
        self.botpane = ttk.Frame(pane)

        # All interior windows size to toppane
        self.toppane.columnconfigure(0, weight = 1)
        # Projects window resizes preferably to others
        self.toppane.rowconfigure(3, weight = 1)

        # Get username, and from it determine the project directory.
        # Save this path, because it gets used often.
        username = self.prefs['username']
        self.projectdir = os.path.expanduser('~/' + designdir)
        self.cloudvdir = os.path.expanduser('~/' + cloudvdir)

        # Check that the project directory exists, and create it if not
        if not os.path.isdir(self.projectdir):
            os.makedirs(self.projectdir)

        # Label with the user
        self.toppane.user_frame = ttk.Frame(self.toppane)
        self.toppane.user_frame.grid(row = 0, sticky = 'news')

        # Put logo image in corner.  Ignore if something goes wrong, as this
        # is only decorative.  Note: ef_logo must be kept as a record in self,
        # or else it gets garbage collected.
        try:
            #EFABLESS PLATFORM
            self.ef_logo = tkinter.PhotoImage(file='/ef/efabless/opengalaxy/efabless_logo_small.gif')
            self.toppane.user_frame.logo = ttk.Label(self.toppane.user_frame, image=self.ef_logo)
            self.toppane.user_frame.logo.pack(side = 'left', padx = 5)
        except:
            pass

        self.toppane.user_frame.title = ttk.Label(self.toppane.user_frame, text='User:', style='red.TLabel')
        self.toppane.user_frame.user = ttk.Label(self.toppane.user_frame, text=username, style='blue.TLabel')

        self.toppane.user_frame.title.pack(side = 'left', padx = 5)
        self.toppane.user_frame.user.pack(side = 'left', padx = 5)

        #---------------------------------------------
        ttk.Separator(self.toppane, orient='horizontal').grid(row = 1, sticky = 'news')
        #---------------------------------------------

        # List of projects:
        self.toppane.design_frame = ttk.Frame(self.toppane)
        self.toppane.design_frame.grid(row = 2, sticky = 'news')

        self.toppane.design_frame.design_header = ttk.Label(self.toppane.design_frame, text='Projects',
			style='title.TLabel')
        self.toppane.design_frame.design_header.pack(side = 'left', padx = 5)

        self.toppane.design_frame.design_header2 = ttk.Label(self.toppane.design_frame,
			text='(' + self.projectdir + '/)', style='normal.TLabel')
        self.toppane.design_frame.design_header2.pack(side = 'left', padx = 5)

        # Get current project from ~/.open_pdks/currdesign and set the selection.
        try:
            with open(os.path.expanduser(currdesign), 'r') as f:
                pdirCur = f.read().rstrip()
        except:
            pdirCur = None

        
        # Create listbox of projects
        projectlist = self.get_project_list() if not deferLoad else []
        height = min(10, max(prjPaneMinh, 2 + len(projectlist)))
        self.projectselect = TreeViewChoice(self.toppane, fontsize=fontsize, deferLoad=deferLoad, selectVal=pdirCur, natSort=True)
        self.projectselect.populate("Available Projects:", projectlist,
			[["New", True, self.createproject],
			 ["Import", True, self.importproject],
			 ["Flow", False, self.startflow],
			 ["Copy", False, self.copyproject],
			 ["Rename", False, self.renameproject],
			 ["Delete", False, self.deleteproject],
			 ],
			height=height, columns=[0, 1])
        self.projectselect.grid(row = 3, sticky = 'news')
        self.projectselect.bindselect(self.setcurrent)

        tooltip.ToolTip(self.projectselect.get_button(0), text="Create a new project/subproject")
        tooltip.ToolTip(self.projectselect.get_button(1), text="Import a project/subproject")
        tooltip.ToolTip(self.projectselect.get_button(2), text="Start design flow")
        tooltip.ToolTip(self.projectselect.get_button(3), text="Make a copy of an entire project")
        tooltip.ToolTip(self.projectselect.get_button(4), text="Rename a project folder")
        tooltip.ToolTip(self.projectselect.get_button(5), text="Delete an entire project")

        pdklist = self.get_pdk_list(projectlist)
        self.projectselect.populate2("PDK", projectlist, pdklist)

        if pdirCur:
            try:
                curitem = next(item for item in projectlist if pdirCur == item)
            except StopIteration:
                pass
            else:
                if curitem:
                    self.projectselect.setselect(pdirCur)

        # Check that the import directory exists, and create it if not
        if not os.path.isdir(self.projectdir + '/' + importdir):
            os.makedirs(self.projectdir + '/' + importdir)

        # Create a watchdog on the project and import directories
        watchlist = [self.projectdir, self.projectdir + '/' + importdir]
        if os.path.isdir(self.projectdir + '/upload'):
            watchlist.append(self.projectdir + '/upload')
        
        # Check the creation time of the project manager app itself.  Because the project
        # manager tends to be left running indefinitely, it is important to know when it
        # has been updated.  This is checked once every hour since it is really expected
        # only to happen occasionally.

        thisapp = [theProg]
        self.watchself = WatchClock(self, thisapp, self.update_alert, 3600000)

        #---------------------------------------------

        # Add second button bar for major project applications
        self.toppane.apptitle = ttk.Label(self.toppane, text='Tools:', style='title2.TLabel')
        self.toppane.apptitle.grid(row = 4, sticky = 'news')
        self.toppane.appbar = ttk.Frame(self.toppane)
        self.toppane.appbar.grid(row = 5, sticky = 'news')

        # Define the application buttons and actions
        self.toppane.appbar.schem_button = ttk.Button(self.toppane.appbar, text='Edit Schematic',
		command=self.edit_schematic, style = 'normal.TButton')
        self.toppane.appbar.schem_button.pack(side = 'left', padx = 5)
        self.toppane.appbar.layout_button = ttk.Button(self.toppane.appbar, text='Edit Layout',
		command=self.edit_layout, style = 'normal.TButton')
        self.toppane.appbar.layout_button.pack(side = 'left', padx = 5)
        self.toppane.appbar.lvs_button = ttk.Button(self.toppane.appbar, text='Run LVS',
		command=self.run_lvs, style = 'normal.TButton')
        self.toppane.appbar.lvs_button.pack(side = 'left', padx = 5)
        self.toppane.appbar.char_button = ttk.Button(self.toppane.appbar, text='Characterize',
		command=self.characterize, style = 'normal.TButton')
        self.toppane.appbar.char_button.pack(side = 'left', padx = 5)
        self.toppane.appbar.synth_button = ttk.Button(self.toppane.appbar, text='Synthesis Flow',
		command=self.synthesize, style = 'normal.TButton')
        self.toppane.appbar.synth_button.pack(side = 'left', padx = 5)

        self.toppane.appbar.padframeCalc_button = ttk.Button(self.toppane.appbar, text='Pad Frame',
        	command=self.padframe_calc, style = 'normal.TButton')
        self.toppane.appbar.padframeCalc_button.pack(side = 'left', padx = 5)
        '''
        if self.prefs['schemeditor'] == 'xcircuit':
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'XCircuit' schematic editor")
        elif self.prefs['schemeditor'] == 'xschem':
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'XSchem' schematic editor")
        else:
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'Electric' schematic editor")

        if self.prefs['layouteditor'] == 'klayout':
            tooltip.ToolTip(self.toppane.appbar.layout_button, text="Start 'KLayout' layout editor")
        else:
            tooltip.ToolTip(self.toppane.appbar.layout_button, text="Start 'Magic' layout editor")
        '''  
        self.refreshToolTips()
        
        tooltip.ToolTip(self.toppane.appbar.lvs_button, text="Start LVS tool")
        tooltip.ToolTip(self.toppane.appbar.char_button, text="Start Characterization tool")
        tooltip.ToolTip(self.toppane.appbar.synth_button, text="Start Digital Synthesis tool")
        tooltip.ToolTip(self.toppane.appbar.padframeCalc_button, text="Start Pad Frame Generator")

        #---------------------------------------------
        ttk.Separator(self.toppane, orient='horizontal').grid(row = 6, sticky = 'news')
        #---------------------------------------------
        # List of IP libraries:
        '''
        self.toppane.library_frame = ttk.Frame(self.toppane)
        self.toppane.library_frame.grid(row = 7, sticky = 'news')

        self.toppane.library_frame.library_header = ttk.Label(self.toppane.library_frame, text='IP Library:',
			style='title.TLabel')
        self.toppane.library_frame.library_header.pack(side = 'left', padx = 5)

        self.toppane.library_frame.library_header2 = ttk.Label(self.toppane.library_frame,
			text='(' + self.projectdir + '/ip/)', style='normal.TLabel')
        self.toppane.library_frame.library_header2.pack(side = 'left', padx = 5)

        self.toppane.library_frame.library_header3 = ttk.Button(self.toppane.library_frame,
		text=(allPaneOpen and '-' or '+'), command=self.library_toggle, style = 'normal.TButton', width = 2)
        self.toppane.library_frame.library_header3.pack(side = 'right', padx = 5)

        # Create listbox of IP libraries
        iplist = self.get_library_list() if not deferLoad else []
        height = min(8, max(iplPaneMinh, 2 + len(iplist)))
        self.ipselect = TreeViewChoice(self.toppane, fontsize=fontsize, deferLoad=deferLoad, natSort=True)
        self.ipselect.populate("IP Library:", iplist,
			[], height=height, columns=[0, 1], versioning=True)
        valuelist = self.ipselect.getvaluelist()
        datelist = self.get_date_list(valuelist)
        itemlist = self.ipselect.getlist()
        self.ipselect.populate2("date", itemlist, datelist)
        if allPaneOpen:
            self.library_open()
        

        #---------------------------------------------
        ttk.Separator(self.toppane, orient='horizontal').grid(row = 9, sticky = 'news')
        
        #---------------------------------------------
        # List of imports:
        self.toppane.import_frame = ttk.Frame(self.toppane)
        self.toppane.import_frame.grid(row = 10, sticky = 'news')

        self.toppane.import_frame.import_header = ttk.Label(self.toppane.import_frame, text='Imports:',
			style='title.TLabel')
        self.toppane.import_frame.import_header.pack(side = 'left', padx = 5)

        self.toppane.import_frame.import_header2 = ttk.Label(self.toppane.import_frame,
			text='(' + self.projectdir + '/import/)', style='normal.TLabel')
        self.toppane.import_frame.import_header2.pack(side = 'left', padx = 5)

        self.toppane.import_frame.import_header3 = ttk.Button(self.toppane.import_frame,
		text=(allPaneOpen and '-' or '+'), command=self.import_toggle, style = 'normal.TButton', width = 2)
        self.toppane.import_frame.import_header3.pack(side = 'right', padx = 5)

        # Create listbox of imports
        importlist = self.get_import_list() if not deferLoad else []
        self.number_of_imports = len(importlist) if not deferLoad else None
        height = min(8, max(impPaneMinh, 2 + len(importlist)))
        self.importselect = TreeViewChoice(self.toppane, fontsize=fontsize, markDir=True, deferLoad=deferLoad)
        self.importselect.populate("Pending Imports:", importlist,
			[["Import As", False, self.importdesign],
			["Import Into", False, self.importintodesign],
			["Delete", False, self.deleteimport]], height=height, columns=[0, 1])
        valuelist = self.importselect.getvaluelist()
        datelist = self.get_date_list(valuelist)
        itemlist = self.importselect.getlist()
        self.importselect.populate2("date", itemlist, datelist)

        tooltip.ToolTip(self.importselect.get_button(0), text="Import as a new project")
        tooltip.ToolTip(self.importselect.get_button(1), text="Import into an existing project")
        tooltip.ToolTip(self.importselect.get_button(2), text="Remove the import file(s)")
        if allPaneOpen:
            self.import_open()
        '''
        #---------------------------------------------
        # ttk.Separator(self, orient='horizontal').grid(column = 0, row = 8, columnspan=4, sticky='ew')
        #---------------------------------------------

        # Add a text window below the import to capture output.  Redirect
        # print statements to it.
        self.botpane.console = ttk.Frame(self.botpane)
        self.botpane.console.pack(side = 'top', fill = 'both', expand = 'true')

        self.text_box = ConsoleText(self.botpane.console, wrap='word', height = 4)
        self.text_box.pack(side='left', fill='both', expand = 'true')
        console_scrollbar = ttk.Scrollbar(self.botpane.console)
        console_scrollbar.pack(side='right', fill='y')
        # attach console to scrollbar
        self.text_box.config(yscrollcommand = console_scrollbar.set)
        console_scrollbar.config(command = self.text_box.yview)

        # Give all the expansion weight to the message window.
        # self.rowconfigure(9, weight = 1)
        # self.columnconfigure(0, weight = 1)

        # at bottom (legacy mode): window height grows by one row.
        # at top the buttons share a row with user name, reduce window height, save screen real estate.
        bottomButtons = False

        # Add button bar: at the bottom of window (legacy mode), or share top row with user-name
        if bottomButtons:
            bbar =  ttk.Frame(self.botpane)
            bbar.pack(side='top', fill = 'x')
        else:
            bbar =  self.toppane.user_frame

        # Define help button
        bbar.help_button = ttk.Button(bbar, text='Help',
		                      command=self.help.open, style = 'normal.TButton')

        # Define profile settings button
        bbar.profile_button = ttk.Button(bbar, text='Settings',
		                         command=self.profile.open, style = 'normal.TButton')

        # Define the "quit" button and action
        bbar.quit_button = ttk.Button(bbar, text='Quit', command=self.on_quit,
                                      style = 'normal.TButton')
        # Tool tips for button bar
        tooltip.ToolTip(bbar.quit_button, text="Exit the project manager")
        tooltip.ToolTip(bbar.help_button, text="Show help window")

        if bottomButtons:
            bbar.help_button.pack(side = 'left', padx = 5)
            bbar.profile_button.pack(side = 'left', padx = 5)
            bbar.quit_button.pack(side = 'right', padx = 5)
        else:
            # quit at TR like window-title's close; help towards the outside, settings towards inside
            bbar.quit_button.pack(side = 'right', padx = 5)
            bbar.help_button.pack(side = 'right', padx = 5)
            bbar.profile_button.pack(side = 'right', padx = 5)

        # Add the panes once the internal geometry is known
        pane.add(self.toppane)
        pane.add(self.botpane)
        pane.paneconfig(self.toppane, stretch='first')
        # self.update_idletasks()

        #---------------------------------------------------------------
        # Project list
        # projects = os.listdir(os.path.expanduser('~/' + designdir))
        # self.cur_project.set(projects[0])
        # self.design_select = ttk.OptionMenu(self, self.cur_project, projects[0], *projects,
        #		style='blue.TMenubutton')

        # New import list
        # self.import_select = ttk.Button(self, text=self.cur_import, command=self.choose_import)

        #---------------------------------------------------------
        # Define project design actions
        # self.design_actions = ttk.Frame(self)
        # self.design_actions.characterize = ttk.Button(self.design_actions,
        #  	text='Upload and Characterize', command=self.characterize)
        # self.design_actions.characterize.grid(column = 0, row = 0)

        # Define import actions
        # self.import_actions = ttk.Frame(self)
        # self.import_actions.upload = ttk.Button(self.import_actions,
        #	text='Upload Challenge', command=self.make_challenge)
        # self.import_actions.upload.grid(column = 0, row = 0)

        self.watchclock = WatchClock(self, watchlist, self.update_project_views, 2000,
                                     0 if deferLoad else None) # do immediate forced refresh (1st in mainloop)
        # self.watchclock = WatchClock(self, watchlist, self.update_project_views, 2000)

        # Redirect stdout and stderr to the console as the last thing to do. . .
        # Otherwise errors in the GUI get sucked into the void.
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = ConsoleText.StdoutRedirector(self.text_box)
        sys.stderr = ConsoleText.StderrRedirector(self.text_box)

        if message:
            print(message)

        if self.prefs == {}:
            print("No user preferences file, using default settings.")

    # helper for Profile to do live mods of some of the user-prefs (without restart projectManager):
    def setUsername(self, newname):
        self.toppane.user_frame.user.config(text=newname)
        
    def refreshToolTips(self):
        if self.prefs['schemeditor'] == 'xcircuit':
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'XCircuit' schematic editor")
        elif self.prefs['schemeditor'] == 'xschem':
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'XSchem' schematic editor")
        else:
            tooltip.ToolTip(self.toppane.appbar.schem_button, text="Start 'Electric' schematic editor")

        if self.prefs['layouteditor'] == 'klayout':
            tooltip.ToolTip(self.toppane.appbar.layout_button, text="Start 'KLayout' layout editor")
        else:
            tooltip.ToolTip(self.toppane.appbar.layout_button, text="Start 'Magic' layout editor")
    
    @classmethod
    def config_path(cls, path):
        #returns the config directory that 'path' contains between .config and .ef-config
        if (os.path.exists(path + '/.config')):
            return '/.config'
        elif (os.path.exists(path + '/.ef-config')):
            return '/.ef-config'
        raise Exception('Neither '+path+'/.config nor '+path+'/.ef-config exists.')

    #------------------------------------------------------------------------
    # Check if a name is blacklisted for being a project folder
    #------------------------------------------------------------------------
    
    @classmethod
    def blacklisted(cls, dirname):
        # Blacklist:  Do not show files of these names:
        blacklist = [importdir, 'ip', 'upload', 'export', 'lost+found', 'subcells']
        if dirname in blacklist:
            return True
        else:
            return False

    def write_prefs(self):
        global prefsfile

        if self.prefs:
            expprefsfile = os.path.expanduser(prefsfile)
            prefspath = os.path.split(expprefsfile)[0]
            if not os.path.exists(prefspath):
                os.makedirs(prefspath)
            with open(os.path.expanduser(prefsfile), 'w') as f:
                json.dump(self.prefs, f, indent = 4)

    def read_prefs(self):
        global prefsfile

        # Set all known defaults even if they are not in the JSON file so
        # that it is not necessary to check for the existence of the keyword
        # in the dictionary every time it is accessed.
        if 'fontsize' not in self.prefs:
            self.prefs['fontsize'] = 11
        userid = os.environ['USER']
        uid = ''
        username = userid
        self.prefs['username'] = username
        
        '''
        if 'username' not in self.prefs:
            
            # 
            #EFABLESS PLATFORM
            p = subprocess.run(['/ef/apps/bin/withnet' ,
			config.apps_path + '/og_uid_service.py', userid],
			stdout = subprocess.PIPE)
            if p.stdout:
                uid_string = p.stdout.splitlines()[0].decode('utf-8')
                userspec = re.findall(r'[^"\s]\S*|".+?"', uid_string)
                if len(userspec) > 0:
                    username = userspec[0].strip('"')
                    # uid = userspec[1]
                    # Note userspec[1] = UID and userspec[2] = role, useful
                    # for future applications.
                else:
                    username = userid
            else:
                username = userid
            self.prefs['username'] = username
            # self.prefs['uid'] = uid
        '''
        if 'schemeditor' not in self.prefs:
            self.prefs['schemeditor'] = 'electric'

        if 'layouteditor' not in self.prefs:
            self.prefs['layouteditor'] = 'magic'

        if 'magic-graphics' not in self.prefs:
            self.prefs['magic-graphics'] = 'X11'

        if 'development' not in self.prefs:
            self.prefs['development'] = False

        if 'devstdcells' not in self.prefs:
            self.prefs['devstdcells'] = False

        # Any additional user preferences go above this line.

        # Get user preferences from ~/design/.profile/prefs.json and use it to
        # overwrite default entries in self.prefs
        try:
            with open(os.path.expanduser(prefsfile), 'r') as f:
                prefsdict = json.load(f)
                for key in prefsdict:
                    self.prefs[key] = prefsdict[key]
        except:
            # No preferences file, so create an initial one.
            if not os.path.exists(prefsfile):
                self.write_prefs()
        
        # if 'User:' Label exists, this updates it live (Profile calls read_prefs after write)
        try:
            self.setUsername(self.prefs['username'])
        except:
            pass

    #------------------------------------------------------------------------
    # Get a list of the projects in the user's design directory.  Exclude
    # items that are not directories, or which are blacklisted.
    #------------------------------------------------------------------------

    def get_project_list(self):
        global importdir

        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[ \t\n].*")

        # Get contents of directory.  Look only at directories
     
        projectlist = []
        
        def add_projects(projectpath):
            # Recursively add subprojects to projectlist
            projectlist.append(projectpath)
            #check for subprojects and add them
            if os.path.isdir(projectpath + '/subcells'):
                for subproj in os.listdir(projectpath + '/subcells'):
                    if os.path.isdir(projectpath + '/subcells/' + subproj):
                        add_projects(projectpath + '/subcells/' + subproj)
        
        for item in os.listdir(self.projectdir):
            if os.path.isdir(self.projectdir + '/' + item):
                projectpath = self.projectdir + '/' + item
                add_projects(projectpath)
         
                        
        # 'import' and others in the blacklist are not projects!
        # Files beginning with '.' and files with whitespace are
        # also not listed.
        for item in projectlist[:]:
            name = os.path.split(item)[1]
            if self.blacklisted(name):
                projectlist.remove(item)
            elif badrex1.match(name):
                projectlist.remove(item)
            elif badrex2.match(name):
                projectlist.remove(item)
        return projectlist

    #------------------------------------------------------------------------
    # Get a list of the projects in the user's cloudv directory.  Exclude
    # items that are not directories, or which are blacklisted.
    #------------------------------------------------------------------------

    def get_cloudv_project_list(self):
        global importdir

        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[ \t\n].*")

        if not os.path.exists(self.cloudvdir):
            print('No user cloudv dir exists;  no projects to import.')
            return None

        # Get contents of cloudv directory.  Look only at directories
        projectlist = list(item for item in os.listdir(self.cloudvdir) if
			os.path.isdir(self.cloudvdir + '/' + item))

        # 'import' and others in the blacklist are not projects!
        # Files beginning with '.' and files with whitespace are
        # also not listed.
        for item in projectlist[:]:
            if self.blacklisted(item):
                projectlist.remove(item)
            elif badrex1.match(item):
                projectlist.remove(item)
            elif badrex2.match(item):
                projectlist.remove(item)

        # Add pathname to all items in projectlist
        projectlist = [self.cloudvdir + '/' + item for item in projectlist]
        return projectlist

    #------------------------------------------------------------------------
    # utility: [re]intialize a project's elec/ dir: the .java preferences and LIBDIRS.
    # So user can just delete .java, and restart electric (from projectManager), to reinit preferences.
    # So user can just delete LIBDIRS, and restart electric (from projectManager), to reinit LIBDIRS.
    # So project copies/imports can filter ngspice/run (and ../.allwaves), we'll recreate it here.
    #
    # The global /ef/efabless/deskel/* is used and the PDK name substituted.
    #
    # This SINGLE function is used to setup elec/ contents for new projects, in addition to being
    # called in-line prior to "Edit Schematics" (on-the-fly).
    #------------------------------------------------------------------------
    @classmethod
    def reinitElec(cls, design):
        pdkdir = os.path.join( design, ".ef-config/techdir")
        elec = os.path.join( design, "elec")

        # on the fly, ensure has elec/ dir, ensure has ngspice/run/allwaves dir
        try:
            os.makedirs(design + '/elec', exist_ok=True)
        except IOError as e:
            print('Error in os.makedirs(elec): ' + str(e))
        try:
            os.makedirs(design + '/ngspice/run/.allwaves', exist_ok=True)
        except IOError as e:
            print('Error in os.makedirs(.../.allwaves): ' + str(e))
        #EFABLESS PLATFORM
        deskel = '/ef/efabless/deskel'
        
        # on the fly:
        # .../elec/.java : reinstall if missing. From PDK-specific if any.
        if not os.path.exists( os.path.join( elec, '.java')):
            # Copy Electric preferences
            try:
                shutil.copytree(deskel + '/dotjava', design + '/elec/.java', symlinks = True)
            except IOError as e:
                print('Error copying files: ' + str(e))

        # .../elec/LIBDIRS : reinstall if missing, from PDK-specific LIBDIRS
        # in libs.tech/elec/LIBDIRS

        libdirsloc = pdkdir + '/libs.tech/elec/LIBDIRS'

        if not os.path.exists( os.path.join( elec, 'LIBDIRS')):
            if os.path.exists( libdirsloc ):
                # Copy Electric LIBDIRS
                try:
                    shutil.copy(libdirsloc, design + '/elec/LIBDIRS')
                except IOError as e:
                    print('Error copying files: ' + str(e))
            else:
                print('Info: PDK not configured for Electric: no libs.tech/elec/LIBDIRS')

        return None

    #------------------------------------------------------------------------
    # utility: filter a list removing: empty strings, strings with any whitespace
    #------------------------------------------------------------------------
    whitespaceREX = re.compile('\s')
    @classmethod
    def filterNullOrWS(cls, inlist):
        return [ i for i in inlist if i and not cls.whitespaceREX.search(i) ]

    #------------------------------------------------------------------------
    # utility: do a glob.glob of relative pattern, but specify the rootDir,
    # so returns the matching paths found below that rootDir.
    #------------------------------------------------------------------------
    @classmethod
    def globFromDir(cls, pattern, dir=None):
        if dir:
            dir = dir.rstrip('/') + '/'
            pattern = dir + pattern
        result = glob.glob(pattern)
        if dir and result:
            nbr = len(dir)
            result = [ i[nbr:] for i in result ]
        return result

    #------------------------------------------------------------------------
    # utility: from a pdkPath, return list of 3 strings: <foundry>, <node>, <description>.
    # i.e. pdkPath has form '[.../]<foundry>[.<ext>]/<node>'. For now the description
    # is always ''. And an optional foundry extension is pruned/dropped.
    # thus '.../XFAB.2/EFXP018A4' -> 'XFAB', 'EFXP018A4', ''
    #
    # optionally store in each PDK: .ef-config/nodeinfo.json which can define keys:
    # 'foundry', 'node', 'description' to override the foundry (computed from the path)
    # and (fixed, empty) description currently returned by this.
    #
    # Intent: keep a short-description field at least, intended to be one-line max 40 chars,
    # suitable for a on-hover-tooltip display. (Distinct from a big multiline description).
    #
    # On error (malformed pdkPath: can't determine foundry or node), the foundry or node
    # or both may be '' or as specified in the optional default values (if you're
    # generating something for display and want an unknown to appear as 'none' etc.).
    #------------------------------------------------------------------------
    @classmethod
    def pdkdir2fnd(cls, pdkdir, def_foundry='', def_node='', def_description=''):
        foundry = ''
        foundry_name = ''
        node = ''
        description = ''
        status = 'active'
        if pdkdir:
            # Code should only be for efabless platform
            '''
            split = os.path.split(os.path.realpath(pdkdir))
            # Full path should be [<something>/]<foundry>[.ext]/<node>
            node = split[1]
            foundry = os.path.split(split[0])[1]
            foundry = os.path.splitext(foundry)[0]
            '''
            # Check for nodeinfo.json
            infofile = pdkdir + '/.config/nodeinfo.json'
            if os.path.exists(infofile):
                with open(infofile, 'r') as ifile:
                    nodeinfo = json.load(ifile)
                if 'foundry' in nodeinfo:
                    foundry = nodeinfo['foundry']
                if 'foundry-name' in nodeinfo:
                    foundry_name = nodeinfo['foundry-name']
                if 'node' in nodeinfo:
                    node = nodeinfo['node']
                if 'description' in nodeinfo:
                    description = nodeinfo['description']
                if 'status' in nodeinfo:
                    status = nodeinfo['status']
                return foundry, foundry_name, node, description, status
            
            infofile = pdkdir + '/.ef-config/nodeinfo.json'
            if os.path.exists(infofile):
                with open(infofile, 'r') as ifile:
                    nodeinfo = json.load(ifile)
                if 'foundry' in nodeinfo:
                    foundry = nodeinfo['foundry']
                if 'foundry-name' in nodeinfo:
                    foundry_name = nodeinfo['foundry-name']
                if 'node' in nodeinfo:
                    node = nodeinfo['node']
                if 'description' in nodeinfo:
                    description = nodeinfo['description']
                if 'status' in nodeinfo:
                    status = nodeinfo['status']
                return foundry, foundry_name, node, description, status
        raise Exception('malformed pdkPath: can\'t determine foundry or node')

    #------------------------------------------------------------------------
    # Get a list of the electric-libraries (DELIB only) in a given project.
    # List of full-paths each ending in '.delib'
    #------------------------------------------------------------------------

    def get_elecLib_list(self, pname):
        elibs = self.globFromDir(pname + '/elec/*.delib/', self.projectdir)
        elibs = [ re.sub("/$", "", i) for i in elibs ]
        return self.filterNullOrWS(elibs)

    #------------------------------------------------------------------------
    # Create a list of datestamps for each import file
    #------------------------------------------------------------------------
    def get_date_list(self, valuelist):
        datelist = []
        for value in valuelist:
            try:
                importfile = value[0]
                try:
                    statbuf = os.stat(importfile)
                except:
                    # Note entries that can't be accessed.
                    datelist.append("(unknown)")
                else:
                    datestamp = datetime.datetime.fromtimestamp(statbuf.st_mtime)
                    datestr = datestamp.strftime("%c")
                    datelist.append(datestr)
            except:
                datelist.append("(N/A)")

        return datelist

    #------------------------------------------------------------------------
    # Get the PDK attached to a project for display as: '<foundry> : <node>'
    # unless path=True: then return true PDK dir-path.
    #
    # TODO: the ef-config prog output is not used below. Intent was use
    # ef-config to be the one official query for *any* project's PDK value, and
    # therein-only hide a built-in default for legacy projects without techdir symlink.
    # In below ef-config will always give an EF_TECHDIR, so that code-branch always
    # says '(default)', the ef-config subproc is wasted, and '(no PDK)' is never
    # reached.
    #------------------------------------------------------------------------
    def get_pdk_dir(self, project, path=False):
        pdkdir = os.path.realpath(project + self.config_path(project)+'/techdir')
        if path:
            return pdkdir
        foundry, foundry_name, node, desc, status = self.pdkdir2fnd( pdkdir )
        return foundry + ' : ' + node
        '''
        if os.path.isdir(project + '/.ef-config'):
            if os.path.exists(project + '/.ef-config/techdir'):
                pdkdir = os.path.realpath(project + '/.ef-config/techdir')
                
        elif os.path.isdir(project + '/.config'):
            if os.path.exists(project + '/.config/techdir'):
                pdkdir = os.path.realpath(project + '/.config/techdir')
                if path:
                    return pdkdir
                foundry, node, desc, status = self.pdkdir2fnd( pdkdir )
                return foundry + ' : ' + node
        '''
        '''
        if not pdkdir:
            # Run "ef-config" script for backward compatibility
            export = {'EF_DESIGNDIR': project}
            #EFABLESS PLATFORM
            p = subprocess.run(['/ef/efabless/bin/ef-config', '-sh', '-t'],
			stdout = subprocess.PIPE, env = export)
            config_out = p.stdout.splitlines()
            for line in config_out:
                setline = line.decode('utf-8').split('=')
                if setline[0] == 'EF_TECHDIR':
                    pdkdir = ( setline[1] if path else '(default)' )
            if not pdkdir:
                pdkdir = ( None if path else '(no PDK)' )    # shouldn't get here
        '''
        
        

        return pdkdir
#------------------------------------------------------------------------
    # Get PDK directory for projects without a techdir (most likely the project is being imported)
    #------------------------------------------------------------------------
    @classmethod
    def get_import_pdk(cls, projectpath):
        print(projectpath)
        yamlname = projectpath + '/info.yaml'
       
        with open(yamlname, 'r') as f:
            datatop = yaml.safe_load(f)
            project_data = datatop['project']
            project_foundry = project_data['foundry']
            project_process = project_data['process']
                
        project_pdkdir = ''
       
        for pdkdir_lr in glob.glob('/usr/share/pdk/*/libs.tech/'):
            pdkdir = os.path.split( os.path.split( pdkdir_lr )[0])[0]
            foundry, foundry_name, node, desc, status = ProjectManager.pdkdir2fnd( pdkdir )
            if not foundry or not node:
                continue
            if (foundry == project_foundry or foundry_name == project_foundry) and node == project_process:
                project_pdkdir = pdkdir
                break
          
        return project_pdkdir, foundry, node #------------------------------------------------------------------------
    # Get the list of PDKs that are attached to each project
    #------------------------------------------------------------------------
    def get_pdk_list(self, projectlist):
        pdklist = []
        for project in projectlist:
            pdkdir = self.get_pdk_dir(project)
            pdklist.append(pdkdir)
            
        return pdklist

    #------------------------------------------------------------------------
    # Find a .json's associated tar.gz (or .tgz) if any.
    # Return path to the tar.gz if any, else None.
    #------------------------------------------------------------------------

    def json2targz(self, jsonPath):
        root = os.path.splitext(jsonPath)[0]
        for ext in ('.tgz', '.tar.gz'):
            if os.path.isfile(root + ext):
                return root + ext
        return None
        
    def yaml2targz(self, yamlPath):
        root = os.path.splitext(yamlPath)[0]
        for ext in ('.tgz', '.tar.gz'):
            if os.path.isfile(root + ext):
                return root + ext
        return None

    #------------------------------------------------------------------------
    # Remove a .json and associated tar.gz (or .tgz) if any.
    # If not a .json, remove just that file (no test for a tar).
    #------------------------------------------------------------------------

    def removeJsonPlus(self, jsonPath):
        ext = os.path.splitext(jsonPath)[1]
        if ext == ".json":
            tar = self.json2targz(jsonPath)
            if tar: os.remove(tar)
        return os.remove(jsonPath)

    #------------------------------------------------------------------------
    # MOVE a .json and associated tar.gz (or .tgz) if any, to targetDir.
    # If not a .json, move just that file (no test for a tar).
    #------------------------------------------------------------------------

    def moveJsonPlus(self, jsonPath, targetDir):
        ext = os.path.splitext(jsonPath)[1]
        if ext == ".json":
            tar = self.json2targz(jsonPath)
            if tar:
                shutil.move(tar,      targetDir)
        # believe the move throws an error. So return value (the targetDir name) isn't really useful.
        return  shutil.move(jsonPath, targetDir)

    #------------------------------------------------------------------------
    # Get a list of the libraries in the user's ip folder
    #------------------------------------------------------------------------

    def get_library_list(self):
        # Get contents of directory
        try:
            iplist = glob.glob(self.projectdir + '/ip/*/*')
        except:
            iplist = []
        else:
            pass
      
        return iplist

    #------------------------------------------------------------------------
    # Get a list of the files in the user's design import folder
    # (use current 'import' but also original 'upload')
    #------------------------------------------------------------------------

    def get_import_list(self):
        # Get contents of directory
        importlist = os.listdir(self.projectdir + '/' + importdir)

        # If entries have both a .json and .tar.gz file, remove the .tar.gz (also .tgz).
        # Also ignore any .swp files dropped by the vim editor.
        # Also ignore any subdirectories of import
        for item in importlist[:]:
            if item[-1] in '#~':
                importlist.remove(item)
                continue
            ipath = self.projectdir + '/' + importdir + '/' + item

            # recognize dirs (as u2u projects) if not symlink and has a 'project.json',
            # hide dirs named *.bak. If originating user does u2u twice before target user
            # can consume/import it, the previous one (only) is retained as *.bak.
            if os.path.isdir(ipath):
                if os.path.islink(ipath) or not self.validProjectName(item) \
                   or self.importProjNameBadrex1.match(item) \
                   or not os.path.isfile(ipath + '/info.yaml'):
                    importlist.remove(item)
                    continue
            else:
                ext = os.path.splitext(item)
                if ext[1] == '.json':
                    if ext[0] + '.tar.gz' in importlist:
                        importlist.remove(ext[0] + '.tar.gz')
                    elif ext[0] + '.tgz' in importlist:
                        importlist.remove(ext[0] + '.tgz')
                elif ext[1] == '.swp':
                    importlist.remove(item)
                elif os.path.isdir(self.projectdir + '/' + importdir + '/' + item):
                    importlist.remove(item)

        # Add pathname to all items in projectlist
        importlist = [self.projectdir + '/' + importdir + '/' + item for item in importlist]

        # Add support for original "upload" directory (backward compatibility)
        if os.path.exists(self.projectdir + '/upload'):
            uploadlist = os.listdir(self.projectdir + '/upload')

            # If entries have both a .json and .tar.gz file, remove the .tar.gz (also .tgz).
            # Also ignore any .swp files dropped by the vim editor.
            for item in uploadlist[:]:
                ext = os.path.splitext(item)
                if ext[1] == '.json':
                    if ext[0] + '.tar.gz' in uploadlist:
                        uploadlist.remove(ext[0] + '.tar.gz')
                    elif ext[0] + '.tgz' in uploadlist:
                        uploadlist.remove(ext[0] + '.tgz')
                elif ext[1] == '.swp':
                    uploadlist.remove(item)

            # Add pathname to all items in projectlist
            uploadlist = [self.projectdir + '/upload/' + item for item in uploadlist]
            importlist.extend(uploadlist)

        # Remember the size of the list so we know when it changed
        self.number_of_imports = len(importlist)
        return importlist 

    #------------------------------------------------------------------------
    # Import for json documents and related tarballs (.gz or .tgz):  
    #------------------------------------------------------------------------

    def importyaml(self, projname, importfile):
        # (1) Check if there is a tarball with the same root name as the JSON
        importroot = os.path.splitext(importfile)[0]
        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        if os.path.isfile(importroot + '.tgz'):
           tarname = importroot + '.tgz'
        elif os.path.isfile(importroot + '.tar.gz'):
           tarname = importroot + '.tar.gz'
        else:
           tarname = []
        # (2) Check for name conflict
        origname = projname
        newproject = self.projectdir + '/' + projname
        newname = projname
        while os.path.isdir(newproject) or self.blacklisted(newname):
            if self.blacklisted(newname):
                warning = "Name " + newname + " is not allowed for a project name."
            elif badrex1.match(newname):
                warning = 'project name may not start with "."'
            elif badrex2.match(newname):
                warning = 'project name contains illegal characters or whitespace.'
            else:
                warning = "Project " + newname + " already exists!"
            newname = ProjectNameDialog(self, warning, seed=newname).result
            if not newname:
                return 0	# Canceled, no action.
            newproject = self.projectdir + '/' + newname
        print("New project name is " + newname + ".")
        # (3) Create new directory
        os.makedirs(newproject)
        # (4) Dump the tarball (if any) in the new directory
        if tarname:
            with tarfile.open(tarname, mode='r:gz') as archive:
                for member in archive:
                    archive.extract(member, newproject)
        # (5) Copy the YAML document into the new directory.  Keep the
        # original name of the project, so as to overwrite any existing
        # document, then change the name to match that of the project
        # folder.

        yamlfile = newproject + '/info.yaml'

        try:
            shutil.copy(importfile, yamlfile)
        except IOError as e:
            print('Error copying files: ' + str(e))
            return None

        # (6) Remove the original files from the import folder
        os.remove(importfile)
        if tarname:
            os.remove(tarname)

        # (7) Standard project setup:  if spi/, elec/, and ngspice/ do not
        # exist, create them.  If elec/.java does not exist, create it and
        # seed from deskel.  If ngspice/run and ngspice/run/.allwaves do not
        # exist, create them.

        if not os.path.exists(newproject + '/spi'):
            os.makedirs(newproject + '/spi')
        if not os.path.exists(newproject + '/spi/pex'):
            os.makedirs(newproject + '/spi/pex')
        if not os.path.exists(newproject + '/spi/lvs'):
            os.makedirs(newproject + '/spi/lvs')
        if not os.path.exists(newproject + '/ngspice'):
            os.makedirs(newproject + '/ngspice')
        if not os.path.exists(newproject + '/ngspice/run'):
            os.makedirs(newproject + '/ngspice/run')
        if not os.path.exists(newproject + '/ngspice/run/.allwaves'):
            os.makedirs(newproject + '/ngspice/run/.allwaves')
        if not os.path.exists(newproject + '/elec'):
            os.makedirs(newproject + '/elec')
        if not os.path.exists(newproject + '/xcirc'):
            os.makedirs(newproject + '/xcirc')
        if not os.path.exists(newproject + '/mag'):
            os.makedirs(newproject + '/mag')

        self.reinitElec(newproject)   # [re]install elec/.java, elec/LIBDIRS if needed, from pdk-specific if-any

        return 1	# Success

    #------------------------------------------------------------------------
    # Import for netlists (.spi):
    # (1) Request project name
    # (2) Create new project if name does not exist, or
    #     place netlist in existing project if it does.
    #------------------------------------------------------------------------

    #--------------------------------------------------------------------
    # Install netlist in electric:
    # "importfile" is the filename in ~/design/import
    # "pname" is the name of the target project (folder)
    # "newfile" is the netlist file name (which may or may not be the same
    #     as 'importfile').
    #--------------------------------------------------------------------

    def install_in_electric(self, importfile, pname, newfile, isnew=True):
        #--------------------------------------------------------------------
        # Install the netlist.
        # If netlist is CDL, then call cdl2spi first
        #--------------------------------------------------------------------

        newproject = self.projectdir + '/' + pname
        if not os.path.isdir(newproject + '/spi/'):
            os.makedirs(newproject + '/spi/')
        if os.path.splitext(newfile)[1] == '.cdl':
            if not os.path.isdir(newproject + '/cdl/'):
                os.makedirs(newproject + '/cdl/')
            shutil.copy(importfile, newproject + '/cdl/' + newfile)
            try:
                p = subprocess.run(['/ef/apps/bin/cdl2spi', importfile],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE,
			check = True)
            except subprocess.CalledProcessError as e:
                print('Error running cdl2spi: ' + e.output.decode('utf-8'))
                if isnew == True:
                    shutil.rmtree(newproject)
                return None
            else:
                spi_string = p.stdout.splitlines()[0].decode('utf-8')
                if p.stderr:
                    err_string = p.stderr.splitlines()[0].decode('utf-8')
                    # Print error messages to console
                    print(err_string)
            if not spi_string:
                print('Error: cdl2spi has no output')
                if isnew == True:
                    shutil.rmtree(newproject)
                return None
            outname = os.path.splitext(newproject + '/spi/' + newfile)[0] + '.spi'
            with open(outname, 'w') as f:
                f.write(spi_string)
        else:
            outname = newproject + '/spi/' + newfile
            try:
                shutil.copy(importfile, outname)
            except IOError as e:
                print('Error copying files: ' + str(e))
                if isnew == True:
                    shutil.rmtree(newproject)
                return None

        #--------------------------------------------------------------------
        # Symbol generator---this code to be moved into its own def.
        #--------------------------------------------------------------------
        # To-do, need a more thorough SPICE parser, maybe use netgen to parse.
        # Need to find topmost subcircuit, by parsing the hieararchy.
        subcktrex = re.compile('\.subckt[ \t]+([^ \t]+)[ \t]+', re.IGNORECASE)
        subnames = []
        with open(importfile, 'r') as f:
            for line in f:
                lmatch = subcktrex.match(line)
                if lmatch:
                    subnames.append(lmatch.group(1))

        if subnames:
            subname = subnames[0]

        # Run cdl2icon perl script
        try:
            p = subprocess.run(['/ef/apps/bin/cdl2icon', '-file', importfile, '-cellname',
			subname, '-libname', pname, '-projname', pname, '--prntgussddirs'],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True)
        except subprocess.CalledProcessError as e:
            print('Error running cdl2spi: ' + e.output.decode('utf-8'))
            return None
        else:
            pin_string = p.stdout.splitlines()[0].decode('utf-8')
            if not pin_string:
                print('Error: cdl2icon has no output')
                if isnew == True:
                    shutil.rmtree(newproject)
                return None
            if p.stderr:
                err_string = p.stderr.splitlines()[0].decode('utf-8')
                print(err_string)

        # Invoke dialog to arrange pins here
        pin_info_list = SymbolBuilder(self, pin_string.split(), fontsize=self.prefs['fontsize']).result
        if not pin_info_list:
            # Dialog was canceled
            print("Symbol builder was canceled.")
            if isnew == True:
                shutil.rmtree(newproject)
            return 0

        for pin in pin_info_list:
            pin_info = pin.split(':')
            pin_name = pin_info[0]
            pin_type = pin_info[1]

        # Call cdl2icon with the final pin directions
        outname = newproject + '/elec/' + pname + '.delib/' + os.path.splitext(newfile)[0] + '.ic'
        try:
            p = subprocess.run(['/ef/apps/bin/cdl2icon', '-file', importfile, '-cellname',
			subname, '-libname', pname, '-projname', pname, '-output',
			outname, '-pindircmbndstring', ','.join(pin_info_list)],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True)
        except subprocess.CalledProcessError as e:
            print('Error running cdl2icon: ' + e.output.decode('utf-8'))
            if isnew == True:
                shutil.rmtree(newproject)
            return None
        else:
            icon_string = p.stdout.splitlines()[0].decode('utf-8')   # not used, AFAIK
            if p.stderr:
                err_string = p.stderr.splitlines()[0].decode('utf-8')
                print(err_string)

        return 1	# Success

    #------------------------------------------------------------------------
    # Import netlist file into existing project
    #------------------------------------------------------------------------

    def importspiceinto(self, newfile, importfile):
        # Require existing project location
        ppath = ExistingProjectDialog(self, self.get_project_list()).result
        if not ppath:
            return 0		# Canceled in dialog, no action.
        pname = os.path.split(ppath)[1]
        print("Importing into existing project " + pname)
        result = self.install_in_electric(importfile, pname, newfile, isnew=False)
        if result == None:
            print('Error during import.')
            return None
        elif result == 0:
            return 0    # Canceled
        else:
            # Remove original file from imports area
            os.remove(importfile)
            return 1    # Success

    #------------------------------------------------------------------------
    # Import netlist file as a new project
    #------------------------------------------------------------------------

    def importspice(self, newfile, importfile):
        # Use create project code first to generate a valid project space.
        newname = self.createproject(None)
        if not newname:
            return 0		# Canceled in dialog, no action.
        print("Importing as new project " + newname + ".")
        result = self.install_in_electric(importfile, newname, newfile, isnew=True)
        if result == None:
            print('Error during install')
            return None
        elif result == 0: 
            # Canceled, so do not remove the import
            return 0
        else: 
            # Remove original file from imports area
            os.remove(importfile)
            return 1    # Success

    #------------------------------------------------------------------------
    # Determine if JSON's tar can be imported as-if it were just a *.v.
    # This is thin wrapper around tarVglImportable. Find the JSON's associated
    # tar.gz if any, and call tarVglImportable.
    # Returns list of two:
    #   None if rules not satisified; else path of the single GL .v member.
    #   None if rules not satisified; else root-name of the single .json member.
    #------------------------------------------------------------------------

    def jsonTarVglImportable(self, path):
        ext = os.path.splitext(path)[1]
        if ext != '.json': return None, None, None

        tar = self.json2targz(path)
        if not tar: return None, None, None

        return self.tarVglImportable(tar)
    
    def yamlTarVglImportable(self, path):
        ext = os.path.splitext(path)[1]
        if ext != '.yaml': return None, None, None

        tar = self.yaml2targz(path)
        if not tar: return None, None, None

        return self.tarVglImportable(tar)
    #------------------------------------------------------------------------
    # Get a single named member (memPath) out of a JSON's tar file.
    # This is thin wrapper around tarMember2tempfile. Find the JSON's associated
    # tar.gz if any, and call tarMember2tempfile.
    #------------------------------------------------------------------------

    def jsonTarMember2tempfile(self, path, memPath):
        ext = os.path.splitext(path)[1]
        if ext != '.json': return None

        tar = self.json2targz(path)
        if not tar: return None

        return self.tarMember2tempfile(tar, memPath)
        
    def yamlTarMember2tempfile(self, path, memPath):
        ext = os.path.splitext(path)[1]
        if ext != '.yaml': return None

        tar = self.yaml2targz(path)
        if not tar: return None

        return self.tarMember2tempfile(tar, memPath)

    #------------------------------------------------------------------------
    # Determine if tar-file can be imported as-if it were just a *.v.
    # Require exactly one yosys-output .netlist.v, and exactly one .json.
    # Nothing else matters: Ignore all other *.v, *.tv, *.jelib, *.vcd...
    #
    # If user renames *.netlist.v in cloudv before export to not end in
    # netlist.v, we won't recognize it.
    #
    # Returns list of two:
    #   None if rules not satisified; else path of the single GL netlist.v member.
    #   None if rules not satisified; else root-name of the single .json member.
    #------------------------------------------------------------------------

    def tarVglImportable(self, path):
        # count tar members by extensions. Track the .netlist.v. and .json. Screw the rest.
        nbrExt = {'.v':0, '.netlist.v':0, '.tv':0, '.jelib':0, '.json':0, '/other/':0, '/vgl/':0}
        nbrGLv = 0
        jname = None
        vfile = None
        node = None
        t = tarfile.open(path)
        for i in t:
            # ignore (without counting) dir entries. From cloudv (so far) the tar does not
            # have dir-entries, but most tar do (esp. most manually made test cases).
            if i.isdir():
                continue
            # TODO: should we require all below counted files to be plain files (no symlinks etc.)?
            # get extension, but recognize a multi-ext for .netlist.v case
            basenm = os.path.basename(i.name)
            ext = os.path.splitext(basenm)[1]
            root = os.path.splitext(basenm)[0]
            ext2 = os.path.splitext(root)[1]
            if ext2 == '.netlist' and ext == '.v':
                ext = ext2 + ext
            if ext and ext not in nbrExt:
                ext = '/other/'
            elif ext == '.netlist.v' and self.tarMemberIsGLverilog(t, i.name):
                vfile = i.name
                ext = '/vgl/'
            elif ext == '.json':
                node = self.tarMemberHasFoundryNode(t, i.name)
                jname = root
            nbrExt[ext] += 1

        # check rules. Require exactly one yosys-output .netlist.v, and exactly one .json.
        # Quantities of other types are all don't cares.
        if (nbrExt['/vgl/'] == 1 and nbrExt['.json'] == 1):
            # vfile is the name of the verilog netlist in the tarball, while jname
            # is the root name of the JSON file found in the tarball (if any) 
            return vfile, jname, node

        # failed, not gate-level-verilog importable:
        return None, None, node


    #------------------------------------------------------------------------
    # OBSOLETE VERSION: Determine if tar-file can be imported as-if it were just a *.v.
    # Rules for members: one *.v, {0,1} *.jelib, {0,1} *.json, 0 other types.
    # Return None if rules not satisified; else return path of the single .v.
    #------------------------------------------------------------------------
    #
    # def tarVglImportable(self, path):
    #     # count tar members by extensions. Track the .v.
    #     nbrExt = {'.v':0, '.jelib':0, '.json':0, 'other':0}
    #     vfile = ""
    #     t = tarfile.open(path)
    #     for i in t:
    #         ext = os.path.splitext(i.name)[1]
    #         if ext not in nbrExt:
    #             ext = 'other'
    #         nbrExt[ext] += 1
    #         if ext == ".v": vfile = i.name
    #
    #     # check rules.
    #     if (nbrExt['.v'] != 1 or nbrExt['other'] != 0 or
    #         nbrExt['.jelib'] > 1 or nbrExt['.json'] > 1):
    #         return None
    #     return vfile

    #------------------------------------------------------------------------
    # Get a single named member (memPath) out of a tar file (tarPath), into a
    # temp-file, so subprocesses can process it.
    # Return path to the temp-file, or None if member not found in the tar.
    #------------------------------------------------------------------------

    def tarMember2tempfile(self, tarPath, memPath):
        t = tarfile.open(tarPath)
        member = t.getmember(memPath)
        if not member: return None

        # Change member.name so it extracts into our new temp-file.
        # extract() can specify the root-dir befow which the member path
        # resides. If temp is an absolute-path, that root-dir must be /.
        tmpf1 = tempfile.NamedTemporaryFile(delete=False)
        if tmpf1.name[0] != "/":
            raise ValueError("assertion failed, temp-file path not absolute: %s" % tmpf1.name)
        member.name = tmpf1.name
        t.extract(member,"/")

        return tmpf1.name

    #------------------------------------------------------------------------
    # Create an electric .delib directory and seed it with a header file
    #------------------------------------------------------------------------

    def create_electric_header_file(self, project, libname):
        if not os.path.isdir(project + '/elec/' + libname + '.delib'):
            os.makedirs(project + '/elec/' + libname + '.delib')

        p = subprocess.run(['electric', '-v'], stdout=subprocess.PIPE)
        eversion = p.stdout.splitlines()[0].decode('utf-8')
        # Create header file
        with open(project + '/elec/' + libname + '.delib/header', 'w') as f:
            f.write('# header information:\n')
            f.write('H' + libname + '|' + eversion + '\n\n')
            f.write('# Tools:\n')
            f.write('Ouser|DefaultTechnology()Sschematic\n')
            f.write('Osimulation|VerilogUseAssign()BT\n')
            f.write('C____SEARCH_FOR_CELL_FILES____\n')

    #------------------------------------------------------------------------
    # Create an ad-hoc "project.json" dictionary and fill essential records
    #------------------------------------------------------------------------

    def create_ad_hoc_json(self, ipname, pname):
        # Create ad-hoc JSON file and fill it with the minimum
        # necessary entries to define a project.
        jData = {}
        jDS = {}
        '''
        jDS['ip-name'] = ipname
        
        pdkdir = self.get_pdk_dir(pname, path=True)
        try:
            jDS['foundry'], jDS['node'], pdk_desc, pdk_stat = self.pdkdir2fnd( pdkdir )
        except:
            # Cannot parse PDK name, so foundry and node will remain undefined
            pass
        '''
        jDS['format'] = '3'
        pparams = []
        param = {}
        param['unit'] = "\u00b5m\u00b2"
        param['condition'] = "device_area"
        param['display'] = "Device area"
        pmax = {}
        pmax['penalty'] = '0'
        pmax['target'] = '100000'
        param['max'] = pmax
        pparams.append(param)
    
        param = {}
        param['unit'] = "\u00b5m\u00b2"
        param['condition'] = "area"
        param['display'] = "Layout area"
        pmax = {}
        pmax['penalty'] = '0'
        pmax['target'] = '100000'
        param['max'] = pmax
        pparams.append(param)

        param = {}
        param['unit'] = "\u00b5m"
        param['condition'] = "width"
        param['display'] = "Layout width"
        pmax = {}
        pmax['penalty'] = '0'
        pmax['target'] = '300'
        param['max'] = pmax
        pparams.append(param)

        param = {}
        param['condition'] = "DRC_errors"
        param['display'] = "DRC errors"
        pmax = {}
        pmax['penalty'] = 'fail'
        pmax['target'] = '0'
        param['max'] = pmax
        pparams.append(param)

        param = {}
        param['condition'] = "LVS_errors"
        param['display'] = "LVS errors"
        pmax = {}
        pmax['penalty'] = 'fail'
        pmax['target'] = '0'
        param['max'] = pmax
        pparams.append(param)

        jDS['physical-params'] = pparams
        jData['data-sheet'] = jDS

        return jData

#------------------------------------------------------------------------
    # Create info.yaml file (automatically done in create_project.py in case it's executed from the command line)
    #------------------------------------------------------------------------
   
    def create_yaml(self, ipname, pdk_dir, description="(Add project description here)"):
        # ipname: Project Name
        data = {}
        project= {}
        project['description'] = description
        try:
            project['foundry'], foundry_name, project['process'], pdk_desc, pdk_stat = self.pdkdir2fnd( pdk_dir )
        except:
            # Cannot parse PDK name, so foundry and node will remain undefined
            pass
        project['project_name'] = ipname
        project['flow'] = 'none'
        data['project']=project
        return data
    #------------------------------------------------------------------------
    # For a single named member (memPath) out of an open tarfile (tarf),
    # determine if it is a JSON file, and attempt to extract value of entry
    # 'node' in dictionary entry 'data-sheet'.  Otherwise return None.
    #------------------------------------------------------------------------

    def tarMemberHasFoundryNode(self, tarf, memPath):
        fileJSON = tarf.extractfile(memPath)
        if not fileJSON: return None

        try:
            # NOTE: tarfile data is in bytes, json.load(fileJSON) does not work.
            datatop = json.loads(fileJSON.read().decode('utf-8'))
        except:
            print("Failed to load extract file " + memPath + " as JSON data")
            return None
        else:
            node = None
            if 'data-sheet' in datatop:
                dsheet = datatop['data-sheet']
                if 'node' in dsheet:
                    node = dsheet['node']

        fileJSON.close()     # close open-tarfile before any return
        return node

    #------------------------------------------------------------------------
    # For a single named member (memPath) out of an open tarfile (tarf),
    # determine if first line embeds (case-insensitive match): Generated by Yosys
    # Return True or False. If no such member or it has no 1st line, returns False.
    #------------------------------------------------------------------------

    def tarMemberIsGLverilog(self, tarf, memPath):
        fileHdl = tarf.extractfile(memPath)
        if not fileHdl: return False

        line = fileHdl.readline()
        fileHdl.close()     # close open-tarfile before any return
        if not line: return False
        return ('generated by yosys' in line.decode('utf-8').lower())

    #------------------------------------------------------------------------
    # Import vgl-netlist file INTO existing project.
    # The importfile can be a .v; or a .json-with-tar that embeds a .v.
    # What is newfile? not used here.
    #
    # PROMPT to select an existing project is here.
    # (Is also a PROMPT to select existing electric lib, but that's within importvgl).
    #------------------------------------------------------------------------

    def importvglinto(self, newfile, importfile):
        # Require existing project location
        ppath = ExistingProjectDialog(self, self.get_project_list()).result
        if not ppath:   return 0		# Canceled in dialog, no action.
        pname = os.path.split(ppath)[1]
        print( "Importing into existing project: %s" % (pname))

        return self.importvgl(newfile, importfile, pname)

    #------------------------------------------------------------------------
    # Import cloudv project as new project.
    #------------------------------------------------------------------------

    def install_from_cloudv(self, opath, ppath, pdkname, stdcellname, ydicts):
        oname = os.path.split(opath)[1]
        pname = os.path.split(ppath)[1]

        print('Cloudv project name is ' + str(oname))
        print('New project name is ' + str(pname))

        os.makedirs(ppath + '/verilog', exist_ok=True)

        vfile = None
        isfullchip = False
        ipname = oname

        # First check for single synthesized projects, or all synthesized
	# digital sub-blocks within a full-chip project.

        os.makedirs(ppath + '/verilog/source', exist_ok=True)
        bfiles = glob.glob(opath + '/build/*.netlist.v')
        for bfile in bfiles:
            tname = os.path.split(bfile)[1]
            vname = os.path.splitext(os.path.splitext(tname)[0])[0]
            tfile = ppath + '/verilog/' + vname + '/' + vname + '.vgl'
            print('Making qflow sub-project ' + vname)
            os.makedirs(ppath + '/verilog/' + vname, exist_ok=True)
            shutil.copy(bfile, tfile)
            if vname == oname:
                vfile = tfile

            # Each build project gets its own qflow directory.  Create the
            # source/ subdirectory and make a link back to the .vgl file.
            # qflow prep should do the rest.

            os.makedirs(ppath + '/qflow', exist_ok=True)
            os.makedirs(ppath + '/qflow/' + vname)
            os.makedirs(ppath + '/qflow/' + vname + '/source')

            # Make sure the symbolic link is relative, so that it is portable
            # through a shared project.
            curdir = os.getcwd()
            os.chdir(ppath + '/qflow/' + vname + '/source')
            os.symlink('../../../verilog/' + vname + '/' + vname + '.vgl', vname + '.v')
            os.chdir(curdir)

            # Create a simple qflow_vars.sh file so that the project manager
            # qflow launcher will see it as a qflow sub-project.  If the meta.yaml
            # file has a "stdcell" entry for the subproject, then add the line
            # "techname=" with the name of the standard cell library as pulled
            # from meta.yaml.

            stdcell = None
            buildname = 'build/' + vname + '.netlist.v'
            for ydict in ydicts:
                if buildname in ydict:
                    yentry = ydict[buildname]
                    if 'stdcell' in yentry:
                        stdcell = yentry['stdcell']

            with open(ppath + '/qflow/' + vname + '/qflow_vars.sh', 'w') as ofile:
                print('#!/bin/tcsh -f', file=ofile)
                if stdcell:
                    print('set techname=' + stdcell, file=ofile)

        # Now check for a full-chip verilog SoC (from CloudV)

        modrex = re.compile('[ \t]*module[ \t]+[^ \t(]*_?soc[ \t]*\(')
        genmodrex = re.compile('[ \t]*module[ \t]+([^ \t(]+)[ \t]*\(')

        bfiles = glob.glob(opath + '/*.model/*.v')
        for bfile in bfiles:
            tname = os.path.split(bfile)[1]
            vpath = os.path.split(bfile)[0]
            ipname = os.path.splitext(tname)[0]
            tfile = ppath + '/verilog/' + ipname + '.v'
            isfullchip = True
            break

        if isfullchip:
            print('Cloudv project IP name is ' + str(ipname))

            # All files in */ paths should be copied to project verilog/source/,
            # except for the module containing the SoC itself.  Note that the actual
            # verilog source goes here, not the synthesized netlist, although that is
            # mainly for efficiency of the simulation, which would normally be done in
            # cloudV and not in Open Galaxy.  For Open Galaxy, what is needed is the
            # existence of a verilog file containing a module name, which is used to
            # track down the various files (LEF, DEF, etc.) that are needed for full-
            # chip layout.
            #
            # (Sept. 2019) Added copying of files in /SW/ -> /sw/ and /Verify/ ->
	    # /verify/ for running full-chip simulations on the Open Galaxy side.

            os.makedirs(ppath + '/verilog', exist_ok=True)

            cfiles = glob.glob(vpath + '/source/*')
            for cfile in cfiles:
                cname = os.path.split(cfile)[1]
                if cname != tname:
                    tpath = ppath + '/verilog/source/' + cname
                    os.makedirs(ppath + '/verilog/source', exist_ok=True)
                    shutil.copy(cfile, tpath)

            cfiles = glob.glob(vpath + '/verify/*')
            for cfile in cfiles:
                cname = os.path.split(cfile)[1]
                tpath = ppath + '/verilog/verify/' + cname
                os.makedirs(ppath + '/verilog/verify', exist_ok=True)
                shutil.copy(cfile, tpath)

            cfiles = glob.glob(vpath + '/sw/*')
            for cfile in cfiles:
                cname = os.path.split(cfile)[1]
                tpath = ppath + '/verilog/sw/' + cname
                os.makedirs(ppath + '/verilog/sw', exist_ok=True)
                shutil.copy(cfile, tpath)

            # Read the top-level SoC verilog and recast it for OpenGalaxy.
            with open(bfile, 'r') as ifile:
                chiplines = ifile.read().splitlines()

            # Find the modules used, track them down, and add the source location
            # in the Open Galaxy environment as an "include" line in the top level
            # verilog.

            parentdir = os.path.split(bfile)[0]
            modfile = parentdir + '/docs/modules.txt'

            modules = []
            if os.path.isfile(modfile):
                with open(modfile, 'r') as ifile:
                    modules = ifile.read().splitlines()
            else:
                print("Warning:  No modules.txt file for the chip top level module in "
				+ parentdir + "/docs/.\n")

            # Get the names of verilog libraries in this PDK.
            pdkdir = os.path.realpath(ppath + '/.ef-config/techdir')
            pdkvlog = pdkdir + '/libs.ref/verilog'
            pdkvlogfiles = glob.glob(pdkvlog + '/*/*.v')

            # Read the verilog libraries and create a dictionary mapping each
            # module name to a location of the verilog file where it is located.
            moddict = {}
            for vlogfile in pdkvlogfiles:
                with open(vlogfile, 'r') as ifile:
                    for line in ifile.read().splitlines():
                        mmatch = genmodrex.match(line)
                        if mmatch:
                            modname = mmatch.group(1)
                            moddict[modname] = vlogfile

            # Get the names of verilog libraries in the user IP space.
            # (TO DO:  Need to know the IP version being used!)
            designdir = os.path.split(ppath)[0]
            ipdir = designdir + '/ip/'
            uservlogfiles = glob.glob(ipdir + '/*/*/verilog/*.v')
            for vlogfile in uservlogfiles:
                # Strip ipdir from the front
                vlogpath = vlogfile.replace(ipdir, '', 1)
                with open(vlogfile, 'r') as ifile:
                    for line in ifile.read().splitlines():
                        mmatch = genmodrex.match(line)
                        if mmatch:
                            modname = mmatch.group(1)
                            moddict[modname] = vlogpath

            # Find all netlist builds from the project (those that were copied above)
            buildfiles = glob.glob(ppath + '/verilog/source/*.v')
            for vlogfile in buildfiles:
                # Strip ipdir from the front
                vlogpath = vlogfile.replace(ppath + '/verilog/source/', '', 1)
                with open(vlogfile, 'r') as ifile:
                    for line in ifile.read().splitlines():
                        mmatch = genmodrex.match(line)
                        if mmatch:
                            modname = mmatch.group(1)
                            moddict[modname] = vlogpath

            # (NOTE:  removing 'ifndef LVS' as netgen should be able to handle
            #  the contents of included files, and they are preferred since any
            #  arrays are declared in each module I/O)
            # chiplines.insert(0, '`endif')
            chiplines.insert(0, '//--- End of list of included module dependencies ---')
            includedfiles = []
            for module in modules:
                # Determine where this module comes from.  Look in the PDK, then in
                # the user ip/ directory, then in the local hierarchy.  Note that
                # the local hierarchy expects layouts from synthesized netlists that
                # have not yet been created, so determine the expected location.

                if module in moddict:
                    if moddict[module] not in includedfiles:
                        chiplines.insert(0, '`include "' + moddict[module] + '"')
                        includedfiles.append(moddict[module])

            # chiplines.insert(0, '`ifndef LVS')
            chiplines.insert(0, '//--- List of included module dependencies ---')
            chiplines.insert(0, '// iverilog simulation requires the use of -I source -I ~/design/ip')
            chiplines.insert(0, '// NOTE:  Includes may be rooted at ~/design/ip/ or at ./source')
            chiplines.insert(0, '// SoC top level verilog copied and modified by project manager')

            # Copy file, but replace the module name "soc" with the ip-name
            with open(tfile, 'w') as ofile:
                for chipline in chiplines:
                    print(modrex.sub('module ' + ipname + ' (', chipline), file=ofile)

        # Need to define behavior:  What if there is more than one netlist?
        # Which one is to be imported?  For now, ad-hoc behavior is to select
        # the last netlist file in the list if no file matches the ip-name.

        # Note that for full-chip projects, the full chip verilog file is always
        # the last one set.

        if not vfile:
            try:
                vfile = tfile
            except:
                pass

        # NOTE:  vfile was being used to create a symbol, but not any more;
        # see below.  All the above code referencing vfile can probably be
        # removed.

        try:
            sfiles = glob.glob(vpath + '/source/*')
            sfiles.extend(glob.glob(vpath + '/*/source/*'))
        except:
            sfiles = glob.glob(opath + '/*.v')
            sfiles.extend(glob.glob(opath + '/*.sv'))
            sfiles.extend(glob.glob(opath + '/local/*'))

        for fname in sfiles:
            sname = os.path.split(fname)[1]
            tfile = ppath + '/verilog/source/' + sname
            # Reject '.model' and '.soc" files (these are meaningful only to CloudV)
            fileext = os.path.splitext(fname)[1]
            if fileext == '.model' or fileext == '.soc':
                continue
            if os.path.isfile(fname):
                # Check if /verilog/source/ has been created
                if not os.path.isdir(ppath + '/verilog/source'):
                    os.makedirs(ppath + '/verilog/source')
                shutil.copy(fname, tfile)

        # Add standard cell library name to project.json
        pjsonfile = ppath + '/project.json'
        if os.path.exists(pjsonfile):
            with open(pjsonfile, 'r') as ifile:
                datatop = json.load(ifile)
        else:
            datatop = self.create_ad_hoc_json(ipname, ppath)

        # Generate a symbol in electric for the verilog top module
        iconfile = ppath + '/elec/' + ipname + '.delib/' + ipname + '.ic'
        if not os.path.exists(iconfile):
            # NOTE:  Symbols are created by qflow migration for project
            # builds.  Only the chip top-level needs to run create_symbol
            # here.

            if isfullchip:
                print("Creating symbol for module " + ipname + " automatically from verilog source.")
                create_symbol(ppath, vfile, ipname, iconfile, False)
            # Add header file
            self.create_electric_header_file(ppath, ipname)
          
        dsheet = datatop['data-sheet']
        if not stdcellname or stdcellname == "":
            dsheet['standard-cell'] = 'default'
        else:
            dsheet['standard-cell'] = stdcellname

        with open(pjsonfile, 'w') as ofile:
            json.dump(datatop, ofile, indent = 4)

        return 0

    #------------------------------------------------------------------------
    # Import vgl-netlist AS new project.
    # The importfile can be a .v; or a .json-with-tar that embeds a .v.
    # What is newfile? not used here.
    #
    # PROMPT to select an create new project is within importvgl.
    #------------------------------------------------------------------------

    def importvglas(self, newfile, importfile, seedname):
        print('importvglas:  seedname is ' + str(seedname))
        return self.importvgl(newfile, importfile, newname=None, seedname=seedname)

    #------------------------------------------------------------------------
    # Utility shared/used by both: Import vgl-netlist file AS or INTO a project.
    # Called directly for AS. Called via importvglinto for INTO.
    #   importfile : source of .v to import, actual .v or json-with-tar that embeds a .v
    #   newfile : not used
    #   newname : target project-name (INTO), or None (AS: i.e. prompt to create one).
    # Either newname is given: we PROMPT to pick an existing elecLib;
    # Else PROMPT for new projectName and CREATE it (and use elecLib of same name).
    #------------------------------------------------------------------------

    
    def importvgl(self, newfile, importfile, newname=None, seedname=None):
        elecLib = None
        isnew = not newname

        # Up front:  Determine if this import has a .json file associated
        # with it.  If so, then parse the JSON data to find if there is a
        # foundry and node set for the project.  If so, then the foundry
        # node is not selectable at time of import.  Likewise, if "isnew"
        # is false, then we need to check if there is a directory called
        # "newname" and if it is set to the same foundry node.  If not,
        # then the import must be rejected.

        tarVfile, jName, importnode = self.jsonTarVglImportable(importfile)

        if isnew:
            print('importvgl:  seedname is ' + str(seedname))
            # Use create project code first to generate a valid project space.
            newname = self.createproject(None, seedname, importnode)
            if not newname: return 0		# Canceled in dialog, no action.
            print("Importing as new project " + newname + ".")
            elecLib = newname

        ppath = self.projectdir + '/' + newname
        if not elecLib:
            choices = self.get_elecLib_list(newname)
            if not choices:
                print( "Aborted: No existing electric libraries found to import into.")
                return 0
                
            elecLib = ExistingElecLibDialog(self, choices).result
            if not elecLib:
                # Never a just-created project to delete here: We only PROMPT to pick elecLib in non-new case.
                return 0		# Canceled in dialog, no action.
            
            # Isolate just electric lib name without extension. ../a/b.delib -> b
            elecLib = os.path.splitext(os.path.split(elecLib)[-1])[0]
            print("Importing to project: %s, elecLib: %s" % (newname, elecLib))

        # Determine isolated *.v as importactual. May be importfile or tar-member (as temp-file).
        importactual = importfile
        if tarVfile:
            importactual = self.jsonTarMember2tempfile(importfile, tarVfile)
            print("importing json-with-tar's member: %s" % (tarVfile))

        if not os.path.isfile(importactual):
            # TODO: should this be a raise instead?
            print('Error determining *.v to import')
            return None

        result = self.vgl_install(importactual, newname, elecLib, newfile, isnew=isnew)
        if result == None:
            print('Error during install')
            return None
        elif result == 0: 
            # Canceled, so do not remove the import
            return 0
        else: 
            # If jName is non-NULL then there is a JSON file in the tarball.  This is
            # to be used as the project JSON file.  Contents of file coming from
            # CloudV are correct as of 12/8/2017.
            pname = os.path.expanduser('~/design/' + newname)
            legacyjname = pname + '/' + newname + '.json'
            # New behavior 12/2018:  Project JSON file always named 'project.json'
            jname = pname + '/project.json'

            # Do not overwrite an existing JSON file.  Overwriting is a problem for
            # "import into", as the files go into an existing project, which would
            # normally have its own JSON file.

            if not os.path.exists(jname) and not os.path.exists(legacyjname):
                try:
                    tarJfile = os.path.split(tarVfile)[0] + '/' + jName + '.json'
                    importjson = self.jsonTarMember2tempfile(importfile, tarJfile)
                except:
                    jData = self.create_ad_hoc_json(newname, pname)
    
                    with open(jname, 'w') as ofile:
                        json.dump(jData, ofile, indent = 4)

                else:
                    # Copy the temporary file pulled from the tarball and
                    # remove the temporary file.
                    shutil.copy(importjson, jname)
                    os.remove(importjson)

            # For time-being, if a tar.gz & json: archive them in the target project, also as extracted.
            # Remove original file from imports area (either .v; or .json plus tar)
            # plus temp-file if extracted from the tar.
            if importactual != importfile:
                os.remove(importactual)
                pname = self.projectdir + '/' + newname
                importd = pname + '/' + archiveimportdir      # global: archiveimportdir
                os.makedirs(importd, exist_ok=True)
                # Dirnames to embed a VISIBLE date (UTC) of when populated.
                # TODO: improve dir naming or better way to store & understand later when it was processed (a log?),
                # without relying on file-system mtime.
                archived = tempfile.mkdtemp( dir=importd, prefix='{:%Y-%m-%d.%H:%M:%S}-'.format(datetime.datetime.utcnow()))
                tarname = self.json2targz(importfile)
                if tarname:
                    with tarfile.open(tarname, mode='r:gz') as archive:
                        for member in archive:
                            archive.extract(member, archived)
                self.moveJsonPlus(importfile, archived)
            else:
                self.removeJsonPlus(importfile)
            return 1    # Success

    #------------------------------------------------------------------------
    # Prepare multiline "warning" indicating which files to install already exist.
    # TODO: ugly, don't use a simple confirmation dialogue: present a proper table.
    #------------------------------------------------------------------------
    def installsConfirmMarkOverwrite(self, module, files):
        warning = [ "For import of module: %s," % module ]
        anyExists = False
        for i in files:
            exists = os.path.isfile(os.path.expanduser(i))
            if exists: anyExists = True
            warning += [ (" * " if exists else "   ") + i ]
        if anyExists:
            titleSuffix = "\nCONFIRM installation of (*: OVERWRITE existing):"
        else:
            titleSuffix = "\nCONFIRM installation of:"
        warning[0] += titleSuffix
        return ConfirmInstallDialog(self,   "\n".join(warning)).result

    def vgl_install(self, importfile, pname, elecLib, newfile, isnew=True):
        #--------------------------------------------------------------------
        # Convert the in .v to: spi, cdl, elec-icon, elec-text-view forms.
        # TODO: Prompt to confirm final install of 5 files in dir-structure.
        #
        # newfile: argument is not used. What is it for?
        # Target project AND electricLib MAY BE same (pname) or different.
        # Rest of the filenames are determined by the module name in the source .v.
        #--------------------------------------------------------------------

        newproject = self.projectdir + '/' + pname
        try:
            p = subprocess.run(['/ef/apps/bin/vglImport', importfile, pname, elecLib],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=True, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            if hasattr(e, 'stdout') and e.stdout: print(e.stdout)
            if hasattr(e, 'stderr') and e.stderr: print(e.stderr)
            print('Error running vglImport: ' + str(e))
            if isnew == True: shutil.rmtree(newproject)
            return None
        else:
            dataLines = p.stdout.splitlines()
            if p.stderr:
                # Print error messages to console
                for i in p.stderr.splitlines(): print(i)
            if not dataLines or len(dataLines) != 11:
                print('Error: vglImport has no output, or wrong #outputs (%d vs 11)' % len(dataLines))
                if isnew == True: shutil.rmtree(newproject)
                return None
            else:
                module = dataLines[0]
                confirm = self.installsConfirmMarkOverwrite(module, dataLines[2::2])
                if not confirm:
                    print("Cancelled")
                    if isnew == True: shutil.rmtree(newproject)
                    return 0
                # print("Proceed")
                clean = dataLines[1:]
                nbr = len(dataLines)
                ndx = 1
                # trap I/O errors and clean-up if any
                try:
                    while ndx+1 < nbr:
                        trg = os.path.expanduser(dataLines[ndx+1])
                        os.makedirs(os.path.dirname(trg), exist_ok=True)
                        shutil.move(dataLines[ndx], trg)
                        ndx += 2
                except IOError as e:
                    print('Error copying files: ' + str(e))
                    for i in clean:
                        with contextlib.suppress(FileNotFoundError): os.remove(i)
                    if isnew == True: shutil.rmtree(newproject)
                    return 0
                print( "For import of module %s installed: %s" % (module, " ".join(dataLines[2::2])))
                return 1    # Success


    #------------------------------------------------------------------------
    # Callback function from "Import Into" button on imports list box.
    #------------------------------------------------------------------------

    def importintodesign(self, value):
        if not value['values']:
            print('No import selected.')
            return

        # Stop the watchdog timer while this is going on
        self.watchclock.stop()
        newname = value['text']
        importfile = value['values'][0]
        print('Import project name: ' + newname + '')
        print('Import file name: ' + importfile + '')

        # Behavior depends on what kind of file is being imported.
        # Tarballs are entire projects.  Other files are individual
        # files and may be imported into new or existing projects

        if os.path.isdir(importfile):
            print('File is a project, must import as new project.')
            result = self.import2project(importfile, addWarn='Redirected: A projectDir must Import-As new project.')
        else:
            ext = os.path.splitext(importfile)[1]
            vFile, jName, importnode = self.jsonTarVglImportable(importfile)
            if ((ext == '.json' and vFile) or ext == '.v'):
                result = self.importvglinto(newname, importfile)
            elif ext == '.json':
                # Same behavior as "Import As", at least for now
                print('File is a project, must import as new project.')
                result = self.importjson(newname, importfile)
            else:
                result = self.importspiceinto(newname, importfile)

        if result:
            self.update_project_views(force=True)
        self.watchclock.restart()

    #------------------------------------------------------------------------
    # Callback function from "Import As" button on imports list box.
    #------------------------------------------------------------------------

    def importdesign(self, value):
        if not value['values']:
            print('No import selected.')
            return

        # Stop the watchdog timer while this is going on
        self.watchclock.stop()
        newname = value['text']
        importfile = value['values'][0]
        print('Import project name: ' + newname)
        print('Import file name: ' + importfile)

        # Behavior depends on what kind of file is being imported.
        # Tarballs are entire projects.  Other files are individual
        # files and may be imported into new or existing projects

        if os.path.isdir(importfile):
            result = self.import2project(importfile)
        else:
            pathext = os.path.splitext(importfile)
            vfile, seedname, importnode = self.jsonTarVglImportable(importfile)
            if ((pathext[1] == '.json' and seedname) or pathext[1] == '.v'):
                result = self.importvglas(newname, importfile, seedname)
            elif pathext[1] == '.json':
                result = self.importjson(newname, importfile)
            else:
                result = self.importspice(newname, importfile)

        if result:
            self.update_project_views(force=True)
        self.watchclock.restart()

    def deleteimport(self, value):
        if not value['values']:
            print('No import selected.')
            return

        print("Delete import " + value['text'] + '  ' + value['values'][0] + " !")
        # Require confirmation
        warning = 'Confirm delete import ' + value['text'] + '?'
        confirm = ProtectedConfirmDialog(self, warning).result
        if not confirm == 'okay':
            return
        print('Delete confirmed!')
        item = value['values'][0]

        if not os.path.islink(item) and os.path.isdir(item):
            shutil.rmtree(item)
            return

        os.remove(item)
        ext = os.path.splitext(item)
        # Where import is a pair of .json and .tar.gz files, remove both.
        if ext[1] == '.json':
            if os.path.exists(ext[0] + '.tar.gz'):
                os.remove(ext[0] + '.tar.gz')
            elif os.path.exists(ext[0] + '.tgz'):
                os.remove(ext[0] + '.tgz')

    def update_project_views(self, force=False):
        # More than updating project views, this updates projects, imports, and
        # IP libraries.
        
        projectlist = self.get_project_list()
        self.projectselect.repopulate(projectlist)
        pdklist = self.get_pdk_list(projectlist)
        self.projectselect.populate2("PDK", projectlist, pdklist)

        '''
        old_imports = self.number_of_imports
        importlist = self.get_import_list()
        self.importselect.repopulate(importlist)
        valuelist = self.importselect.getvaluelist()
        datelist = self.get_date_list(valuelist)
        itemlist = self.importselect.getlist()
        self.importselect.populate2("date", itemlist, datelist)
        

        # To do:  Check if itemlist in imports changed, and open if a new import
        # has arrived.
     
        if force or (old_imports != None) and (old_imports < self.number_of_imports):
            self.import_open()

        iplist = self.get_library_list()
        self.ipselect.repopulate(iplist, versioning=True)
        valuelist = self.ipselect.getvaluelist()
        datelist = self.get_date_list(valuelist)
        itemlist = self.ipselect.getlist()
        self.ipselect.populate2("date", itemlist, datelist)
        '''
    def update_alert(self):
        # Project manager has been updated.  Generate an alert window and
        # provide option to restart the project manager.

        warning = 'Project manager app has been updated.  Restart now?'
        confirm = ConfirmDialog(self, warning).result
        if not confirm == 'okay':
            print('Warning: Must quit and restart to get any fixes or updates.')
            return
        os.execl('/ef/efabless/opengalaxy/project_manager.py', 'appsel_zenity.sh')
        # Does not return; replaces existing process.

    #----------------------------------------------------------------------
    # Delete a project from the design folder.
    #----------------------------------------------------------------------

    def deleteproject(self, value):
        if not value['values']:
            print('No project selected.')
            return
        path = value['values'][0]
        print('Delete project ' + value['values'][0])
        # Require confirmation
        warning = 'Confirm delete entire project ' + value['text'] + '?'
        confirm = ProtectedConfirmDialog(self, warning).result
        if not confirm == 'okay':
            return
        if os.path.islink(path):
            os.unlink(path)
            self.update_project_views()  
        else:
            shutil.rmtree(value['values'][0])
        if ('subcells' in path):
            self.update_project_views()      

    #----------------------------------------------------------------------
    # Clean out the simulation folder.  Traditionally this was named
    # 'ngspice', so this is checked for backward-compatibility.  The
    # proper name of the simulation directory is 'simulation'.
    #----------------------------------------------------------------------

    def cleanproject(self, value):
        if not value['values']:
            print('No project selected.')
            return
        ppath = value['values'][0]
        print('Clean simulation raw data from directory ' + ppath)
        # Require confirmation
        warning = 'Confirm clean project ' + value['text'] + ' contents?'
        confirm = ConfirmDialog(self, warning).result
        if not confirm == 'okay':
            return
        else:
            self.clean(ppath)
            
    def clean(self, ppath):
        if os.path.isdir(ppath + '/simulation'):
            simpath = 'simulation'
        elif os.path.isdir(ppath + '/ngspice'):
            simpath = 'ngspice'
        else:
            print('Project has no simulation folder.')
            return

        filelist = os.listdir(ppath + '/' + simpath)
        for sfile in filelist:
            if os.path.splitext(sfile)[1] == '.raw':
                os.remove(ppath + '/ngspice/' + sfile)                
        print('Project simulation folder cleaned.')

        # Also clean the log file
        filelist = os.listdir(ppath)
        for sfile in filelist:
            if os.path.splitext(sfile)[1] == '.log':
                os.remove(ppath + '/' + sfile)                

    #---------------------------------------------------------------------------------------
    # Determine which schematic editors are compatible with the PDK, and return a list of them.
    #---------------------------------------------------------------------------------------

    def list_valid_schematic_editors(self, pdktechdir):
        # Check PDK technology directory for xcircuit, xschem, and electric
        applist = []
        if os.path.exists(pdktechdir + '/elec'):
            applist.append('electric')
        if os.path.exists(pdktechdir + '/xschem'):
            applist.append('xschem')
        if os.path.exists(pdktechdir + '/xcircuit'):
            applist.append('xcircuit')

        return applist

    #------------------------------------------------------------------------------------------
    # Determine which layout editors are compatible with the PDK, and return a list of them.
    #------------------------------------------------------------------------------------------

    def list_valid_layout_editors(self, pdktechdir):
        # Check PDK technology directory for magic and klayout
        applist = []
        if os.path.exists(pdktechdir + '/magic'):
            applist.append('magic')
        if os.path.exists(pdktechdir + '/klayout'):
            applist.append('klayout')
        return applist

    #----------------------------------------------------------------------
    # Create a new project folder and initialize it (see below for steps)
    #----------------------------------------------------------------------

    def createproject(self, value, seedname=None, importnode=None):
        global currdesign
        # Note:  value is current selection, if any, and is ignored
        # Require new project location and confirmation
        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        warning = 'Create new project:'
        print(warning)
        development = self.prefs['development']
        
        # Find out whether the user wants to create a subproject or project
        parent_pdk = ''
        try:
            with open(os.path.expanduser(currdesign), 'r') as f:
                pdirCur = f.read().rstrip()
                if ('subcells' in pdirCur):
                    # subproject is selected
                    parent_path = os.path.split(os.path.split(pdirCur)[0])[0]
                    pdkdir = self.get_pdk_dir(parent_path, path=True)
                    (foundry, foundry_name, node, desc, status) = self.pdkdir2fnd( pdkdir )
                    parent_pdk = foundry + '/' + node
                    warning = 'Create new subproject in '+ parent_path + ':'
                elif (pdirCur[0] == '.'):
                    # the project's 'subproject' of itself is selected
                    parent_path = pdirCur[1:]
                    pdkdir = self.get_pdk_dir(parent_path, path=True)
                    (foundry, foundry_name, node, desc, status) = self.pdkdir2fnd( pdkdir )
                    parent_pdk = foundry + '/' + node
                    warning = 'Create new subproject in '+ parent_path + ':'
                
        except:
            pass
        
        while True:
            try:
                if seedname:
                    newname, newpdk = NewProjectDialog(self, warning, seed=seedname, importnode=importnode, development=development, parent_pdk=parent_pdk).result
                else:
                    newname, newpdk = NewProjectDialog(self, warning, seed='', importnode=importnode, development=development, parent_pdk=parent_pdk).result
            except TypeError:
                # TypeError occurs when "Cancel" is pressed, just handle exception.
                return None
            if not newname:
                return None	# Canceled, no action.
            
            if parent_pdk == '':
                newproject = self.projectdir + '/' + newname
            else:
                newproject = parent_path + '/subcells/' + newname
            
            if self.blacklisted(newname):
                warning = newname + ' is not allowed for a project name.'
            elif badrex1.match(newname):
                warning = 'project name may not start with "."'
            elif badrex2.match(newname):
                warning = 'project name contains illegal characters or whitespace.'
            elif os.path.exists(newproject):
                warning = newname + ' is already a project name.'
            else:
                break
        
        if parent_pdk !='' and not os.path.isdir(parent_path + '/subcells'):
            os.makedirs(parent_path + '/subcells')
        
        try:
            subprocess.Popen([config.apps_path + '/create_project.py', newproject, newpdk]).wait()
            
            # Show subproject in project view
            if parent_pdk != '':
                self.update_project_views()
            
        except IOError as e:
            print('Error copying files: ' + str(e))
            return None
            
        except:
            print('Error making project.')
            return None
        
        return newname
        '''
        # Find what tools are compatible with the given PDK
        schemapps = self.list_valid_schematic_editors(newpdk + '/libs.tech')
        layoutapps = self.list_valid_layout_editors(newpdk + '/libs.tech')

        print('New project name will be ' + newname + '.')
        print('Associated project PDK is ' + newpdk + '.')
        try:
            os.makedirs(newproject)

            # Make standard folders
            if 'magic' in layoutapps:
                os.makedirs(newproject + '/mag')

            os.makedirs(newproject + '/spi')
            os.makedirs(newproject + '/spi/pex')
            os.makedirs(newproject + '/spi/lvs')
            if 'electric' in layoutapps or 'electric' in schemapps:
                os.makedirs(newproject + '/elec')
            if 'xcircuit' in schemapps:
                os.makedirs(newproject + '/xcirc')
            if 'klayout' in schemapps:
                os.makedirs(newproject + '/klayout')
            os.makedirs(newproject + '/ngspice')
            os.makedirs(newproject + '/ngspice/run')
            if 'electric' in schemapps:
                os.makedirs(newproject + '/ngspice/run/.allwaves')
            os.makedirs(newproject + '/testbench')
            os.makedirs(newproject + '/verilog')
            os.makedirs(newproject + '/verilog/source')
            os.makedirs(newproject + '/.ef-config')
            if 'xschem' in schemapps:
                os.makedirs(newproject + '/xschem')

            pdkname = os.path.split(newpdk)[1]

            # Symbolic links
            os.symlink(newpdk, newproject + '/.ef-config/techdir')

            # Copy preferences
            # deskel = '/ef/efabless/deskel'
            #
            # Copy examples (disabled;  this is too confusing to the end user.  Also, they
            # should not be in user space at all, as they are not user editable.
            #
            # for item in os.listdir(deskel + '/exlibs'):
            #     shutil.copytree(deskel + '/exlibs/' + item, newproject + '/elec/' + item)
            # for item in os.listdir(deskel + '/exmag'):
            #     if os.path.splitext(item)[1] == '.mag':
            #         shutil.copy(deskel + '/exmag/' + item, newproject + '/mag/' + item)

            # Put tool-specific startup files into the appropriate user directories.
            if 'electric' in layoutapps or 'electric' in schemapps:
                self.reinitElec(newproject)   # [re]install elec/.java, elec/LIBDIRS if needed, from pdk-specific if-any
                # Set up electric
                self.create_electric_header_file(newproject, newname)

            if 'magic' in layoutapps:
                shutil.copy(newpdk + '/libs.tech/magic/current/' + pdkname + '.magicrc', newproject + '/mag/.magicrc')

            if 'xcircuit' in schemapps:
                xcircrc = newpdk + '/libs.tech/xcircuit/' + pdkname + '.' + 'xcircuitrc'
                xcircrc2 = newpdk + '/libs.tech/xcircuit/xcircuitrc'
                if os.path.exists(xcircrc):
                    shutil.copy(xcircrc, newproject + '/xcirc/.xcircuitrc')
                elif os.path.exists(xcircrc2):
                    shutil.copy(xcircrc2, newproject + '/xcirc/.xcircuitrc')

            if 'xschem' in schemapps:
                xschemrc = newpdk + '/libs.tech/xschem/xschemrc'
                if os.path.exists(xschemrc):
                    shutil.copy(xschemrc, newproject + '/xschem/xschemrc')

        except IOError as e:
            print('Error copying files: ' + str(e))
            return None

        return newname
        '''
    #----------------------------------------------------------------------
    # Import a CloudV project from ~/cloudv/<project_name>
    #----------------------------------------------------------------------

    def cloudvimport(self, value):

        # Require existing project location
        clist = self.get_cloudv_project_list()
        if not clist:
            return 0		# No projects to import
        ppath = ExistingProjectDialog(self, clist, warning="Enter name of cloudV project to import:").result
        if not ppath:
            return 0		# Canceled in dialog, no action.
        pname = os.path.split(ppath)[1]
        print("Importing CloudV project " + pname)

        importnode = None
        stdcell = None
        netlistfile = None

        # Pull process and standard cell library from the YAML file created by
        # CloudV.  NOTE:  YAML file has multiple documents, so must use
        # yaml.load_all(), not yaml.load().  If there are refinements of this
        # process for individual build files, they will override (see further down).

        # To do:  Check entries for SoC builds.  If there are multiple SoC builds,
        # then create an additional drop-down selection to choose one, since only
        # one SoC build can exist as a single Open Galaxy project.  Get the name
        # of the top-level module for the SoC.  (NOTE:  It may not be intended
        # that there can be multiple SoC builds in the project, so for now retaining
        # the existing parsing assuming default names.)

        if os.path.exists(ppath + '/.ef-config/meta.yaml'):
            print("Reading YAML file:")
            ydicts = []
            with open(ppath + '/.ef-config/meta.yaml', 'r') as ifile:
                yalldata = yaml.load_all(ifile, Loader=yaml.Loader)
                for ydict in yalldata:
                    ydicts.append(ydict)

            for ydict in ydicts:
                for yentry in ydict.values():
                    if 'process' in yentry:
                        importnode = yentry['process']

        # If there is a file ().soc and a directory ().model, then pull the file
        # ().model/().model.v, which is a chip top-level netlist.

        ydicts = []
        has_soc = False
        save_vdir = None
        vdirs = glob.glob(ppath + '/*')
        for vdir in vdirs:
            vnameparts = vdir.split('.')
            if len(vnameparts) > 1 and vnameparts[-1] == 'soc' and os.path.isdir(vdir):
                has_soc = True
            if len(vnameparts) > 1 and vnameparts[-1] == 'model':
                save_vdir = vdir

        if has_soc:
            if save_vdir:
                vdir = save_vdir
                print("INFO:  CloudV project " + vdir + " is a full chip SoC project.")

                vroot = os.path.split(vdir)[1]
                netlistfile = vdir + '/' + vroot + '.v'
                if os.path.exists(netlistfile):
                    print("INFO:  CloudV chip top level verilog is " + netlistfile + ".")
            else:
                print("ERROR:  Expected SoC .model directory not found.")

        # Otherwise, if the project has a build/ directory and a netlist.v file,
        # then set the foundry node accordingly.

        elif os.path.exists(ppath + '/build'):
            vfiles = glob.glob(ppath + '/build/*.v')
            for vfile in vfiles:
                vroot = os.path.splitext(vfile)[0]
                if os.path.splitext(vroot)[1] == '.netlist':
                    netlistfile = ppath + '/build/' + vfile

                    # Pull process and standard cell library from the YAML file
                    # created by CloudV
                    # Use yaml.load_all(), not yaml.load() (see above)

                    if os.path.exists(ppath + '/.ef-config/meta.yaml'):
                        print("Reading YAML file:")
                        ydicts = []
                        with open(ppath + '/.ef-config/meta.yaml', 'r') as ifile:
                            yalldata = yaml.load_all(ifile, Loader=yaml.Loader)
                            for ydict in yalldata:
                                ydicts.append(ydict)

                        for ydict in ydicts:
                            for yentry in ydict.values():
                                if 'process' in yentry:
                                    importnode = yentry['process']
                                if 'stdcell' in yentry:
                                    stdcell = yentry['stdcell']
                    break

        if importnode:
            print("INFO:  Project targets foundry process " + importnode + ".")
        else:
            print("WARNING:  Project does not target any foundry process.")

        newname = self.createproject(value, seedname=pname, importnode=importnode)
        if not newname: return 0		# Canceled in dialog, no action.
        newpath = self.projectdir + '/' + newname

        result = self.install_from_cloudv(ppath, newpath, importnode, stdcell, ydicts)
        if result == None:
            print('Error during import.')
            return None
        elif result == 0:
            return 0    # Canceled
        else:
            return 1    # Success

    #----------------------------------------------------------------------
    # Make a copy of a project in the design folder.
    #----------------------------------------------------------------------

    def copyproject(self, value):
        if not value['values']:
            print('No project selected.')
            return
        # Require copy-to location and confirmation
        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        warning = 'Copy project ' + value['text'] + ' to new project.'
        print('Copy project directory ' + value['values'][0])
        newname = ''
        copylist = []
        elprefs = False
        spprefs = False
        while True:
            copylist = CopyProjectDialog(self, warning, seed=newname).result
            if not copylist:
                return		# Canceled, no action.
            else:
                newname = copylist[0]
                elprefs = copylist[1]
                spprefs = copylist[2]
            newproject = self.projectdir + '/' + newname
            if self.blacklisted(newname):
                warning = newname + ' is not allowed for a project name.'
            elif newname == "":
                warning = 'Please enter a project name.'
            elif badrex1.match(newname):
                warning = 'project name may not start with "."'
            elif badrex2.match(newname):
                warning = 'project name contains illegal characters or whitespace.'
            elif os.path.exists(newproject):
                warning = newname + ' is already a project name.'
            else:
                break

        oldpath = value['values'][0]
        oldname = os.path.split(oldpath)[1]
        patterns = [oldname + '.log']
        if not elprefs:
            patterns.append('.java')
        if not spprefs:
            patterns.append('ngspice')
            patterns.append('pv')

        print("New project name will be " + newname)
        try:
            if os.path.islink(oldpath):
                os.symlink(oldpath, newproject)
            else:
                shutil.copytree(oldpath, newproject, symlinks = True,
			    ignore = shutil.ignore_patterns(*patterns))
        except IOError as e:
            print('Error copying files: ' + str(e))
            return

        # NOTE:  Behavior is for project files to depend on "project_name".  Using
        # the project filename as a project name is a fallback behavior.  If
        # there is a info.yaml file, and it defines a project_name entry, then
        # there is no need to make changes within the project.  If there is
        # no info.yaml file, then create one and set the project_name entry to
        # the old project name, which avoids the need to make changes within
        # the project.

        else:
            # Check info.yaml
            yamlname = newproject + '/info.yaml'

            found = False
            if os.path.isfile(yamlname):
                # Pull the project_name into local store (may want to do this with the
                # datasheet as well)
                with open(yamlname, 'r') as f:
                    datatop = yaml.safe_load(f)                
                    if 'project_name' in datatop['project']:
                        found = True

            if not found:
                pdkdir = self.get_pdk_dir(newproject, path=True)
                yData = self.create_yaml(oldname, pdkdir)                               
                with open(newproject + '/info.yaml', 'w') as ofile:
                    print('---',file=ofile)
                    yaml.dump(yData, ofile)

        # If ngspice and electric prefs were not copied from the source
        # to the target, as recommended, then copy these from the
        # skeleton repository as is done when creating a new project.

        if not spprefs:
            try:
                os.makedirs(newproject + '/ngspice')
                os.makedirs(newproject + '/ngspice/run')
                os.makedirs(newproject + '/ngspice/run/.allwaves')
            except FileExistsError:
                pass
        '''
        if not elprefs:
            # Copy preferences
            deskel = '/ef/efabless/deskel'
            try:
                shutil.copytree(deskel + '/dotjava', newproject + '/elec/.java', symlinks = True)
            except IOError as e:
                print('Error copying files: ' + e)
        '''

#----------------------------------------------------------------------
    # Allow the user to choose the flow of the project
    #----------------------------------------------------------------------
    
    def startflow(self, value):
        projectpath = value['values'][0]
        flow = ''
        warning = 'Select a flow for '+value['text']
        is_subproject = False
        try:
            with open(os.path.expanduser(currdesign), 'r') as f:
                pdirCur = f.read().rstrip()
                if ('subcells' in pdirCur):
                    # subproject is selected
                    is_subproject = True      
        except:
            pass
        if not os.path.exists(projectpath + '/info.yaml'):
            project_pdkdir = self.get_pdk_dir(projectpath, path=True)
            data = self.create_yaml(os.path.split(projectpath)[1], project_pdkdir)
            with open(projectpath + '/info.yaml', 'w') as ofile:
                print('---',file=ofile)
                yaml.dump(data, ofile)
        
        # Read yaml file for the selected flow
        with open(projectpath + '/info.yaml','r') as f:
            data = yaml.safe_load(f)
            project = data['project']
            if 'flow' in project.keys() and project['flow']=='none' or 'flow' not in project.keys():
                while True:
                    try:
                        flow = SelectFlowDialog(self, warning, seed='', is_subproject = is_subproject).result
                    except TypeError:
                        # TypeError occurs when "Cancel" is pressed, just handle exception.
                        return None
                    if not flow:
                        return None	# Canceled, no action.
                    break
                project['flow']=flow
                data['project']=project
                with open(projectpath + '/info.yaml', 'w') as ofile:
                    print('---',file=ofile)
                    yaml.dump(data, ofile)
            else:
                flow = project['flow']
        
        print("Starting "+flow+" flow...")
        if flow.lower() == 'digital':
            self.synthesize()
        
 #----------------------------------------------------------------------
    # Change a project IP to a different name.
    #----------------------------------------------------------------------

    def renameproject(self, value):
        if not value['values']:
            print('No project selected.')
            return

        # Require new project name and confirmation
        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        projname = value['text']

        # Find the IP name for project projname.  If it has a YAML file, then
        # read it and pull the ip-name record.  If not, the fallback position
        # is to assume that the project filename is the project name.

        # Check info.yaml
        projectpath = self.projectdir + '/' + projname
        yamlname = projectpath + '/info.yaml'

        oldname = projname
        if os.path.isfile(yamlname):
            # Pull the ipname into local store (may want to do this with the
            # datasheet as well)
            with open(yamlname, 'r') as f:
                datatop = yaml.safe_load(f)   
                project_data = datatop['project']          
                if 'project_name' in project_data:
                    oldname = project_data['project_name']

        warning = 'Rename IP "' + oldname + '" for project ' + projname + ':'
        print(warning)
        newname = projname
        while True:
            try:
                newname = ProjectNameDialog(self, warning, seed=oldname + '_1').result
            except TypeError:
                # TypeError occurs when "Cancel" is pressed, just handle exception.
                return None
            if not newname:
                return None	# Canceled, no action.

            if self.blacklisted(newname):
                warning = newname + ' is not allowed for an IP name.'
            elif badrex1.match(newname):
                warning = 'IP name may not start with "."'
            elif badrex2.match(newname):
                warning = 'IP name contains illegal characters or whitespace.'
            else:
                break

        # Update everything, including schematic, symbol, layout, JSON file, etc.
        print('New project IP name will be ' + newname + '.')
        rename_project_all(projectpath, newname)

    # class vars: one-time compile of regulare expressions for life of the process
    projNameBadrex1 = re.compile("^[-.]")
    projNameBadrex2 = re.compile(".*[][{}()!/ \t\n\\\><#$\*\?\"'|`~]")
    importProjNameBadrex1 = re.compile(".*[.]bak$")

    # centralize legal projectName check.
    # TODO: Several code sections are not yet converted to use this.
    # TODO: Extend to explain to the user the reason why.
    def validProjectName(self, name):
        return not (self.blacklisted(name) or
                    self.projNameBadrex1.match(name) or
                    self.projNameBadrex2.match(name))

#----------------------------------------------------------------------
    # Import a project or subproject to the project manager
    #----------------------------------------------------------------------
    
    def importproject(self, value):
        warning = "Import project:"
        badrex1 = re.compile("^\.")
        badrex2 = re.compile(".*[/ \t\n\\\><\*\?].*")
        print(warning)
        
        # Find out whether the user wants to import a subproject or project based on what they selected in the treeview
        parent_pdk = ''
        parent_path = ''
        try:
            with open(os.path.expanduser(currdesign), 'r') as f:
                pdirCur = f.read().rstrip()
                if ('subcells' in pdirCur):
                    # subproject is selected
                    parent_path = os.path.split(os.path.split(pdirCur)[0])[0]
                    parent_pdkdir = self.get_pdk_dir(parent_path, path=True)
                    (foundry, foundry_name, node, desc, status) = self.pdkdir2fnd( parent_pdkdir )
                    parent_pdk = foundry + '/' + node
                    warning = 'Import a subproject to '+ parent_path + ':'
                elif (pdirCur[0] == '.'):
                    # the project's 'subproject' of itself is selected
                    parent_path = pdirCur[1:]
                    parent_pdkdir = self.get_pdk_dir(parent_path, path=True)
                    (foundry, foundry_name, node, desc, status) = self.pdkdir2fnd( parent_pdkdir )
                    parent_pdk = foundry + '/' + node
                    warning = 'Import a subproject to '+ parent_path + ':'
                
        except:
            pass
        
        while True:
            try:
                newname, project_pdkdir, projectpath, importoption = ImportDialog(self, warning, seed='', parent_pdk = parent_pdk, parent_path = parent_path, project_dir = self.projectdir).result
            except TypeError:
                # TypeError occurs when "Cancel" is pressed, just handle exception.
                return None
            if not newname:
                return None	# Canceled, no action.
            
            if parent_pdk == '':
                newproject = self.projectdir + '/' + newname
            else:
                newproject = parent_path + '/subcells/' + newname
            break
        
        def make_techdirs(projectpath, project_pdkdir):
            # Recursively create techdirs in project and subproject folders
            if not (os.path.exists(projectpath + '/.config') or os.path.exists(projectpath + '/.ef-config')):
                os.makedirs(projectpath + '/.config')
            if not os.path.exists(projectpath + self.config_path(projectpath) + '/techdir'):
                os.symlink(project_pdkdir, projectpath + self.config_path(projectpath) + '/techdir')
            if os.path.isdir(projectpath + '/subcells'):
                for subproject in os.listdir(projectpath + '/subcells'):
                    subproject_path = projectpath + '/subcells/' + subproject
                    make_techdirs(subproject_path, project_pdkdir)
                    
        make_techdirs(projectpath, project_pdkdir)
        
        # Make symbolic link/copy projects
        if parent_path=='':
            # Create a regular project
            if importoption == "link":
                os.symlink(projectpath, self.projectdir + '/' + newname)
            else:
                shutil.copytree(projectpath, self.projectdir + '/' + newname, symlinks = True)
            if not os.path.exists(projectpath + '/info.yaml'):
                yData = self.create_yaml(newname, project_pdkdir)                             
                with open(projectpath + '/info.yaml', 'w') as ofile:
                    print('---',file=ofile)
                    yaml.dump(yData, ofile)
        else:
            #Create a subproject
            if not os.path.exists(parent_path + '/subcells'):
                os.makedirs(parent_path + '/subcells')
            if importoption == "copy":
                shutil.copytree(projectpath, parent_path + '/subcells/' + newname, symlinks = True)
                if parent_pdkdir != project_pdkdir:
                    self.clean(parent_path + '/subcells/' + newname)
            else:
                os.symlink(projectpath, parent_path + '/subcells/' + newname)
            if not os.path.exists(parent_path + '/subcells/' + newname + '/info.yaml'):
                yData = self.create_yaml(newname, project_pdkdir)                             
                with open(parent_path + '/subcells/' + newname + '/info.yaml', 'w') as ofile:
                    print('---',file=ofile)
                    yaml.dump(yData, ofile)
            self.update_project_views() 
        #----------------------------------------------------------------------
    # "Import As" a dir in import/ as a project. based on renameproject().
    # addWarn is used to augment confirm-dialogue if redirected here via erroneous ImportInto
    #----------------------------------------------------------------------

    def import2project(self, importfile, addWarn=None):
        name = os.path.split(importfile)[1]
        projpath = self.projectdir + '/' + name

        bakname = name + '.bak'
        bakpath = self.projectdir + '/' + bakname
        warns = []
        if addWarn:
            warns += [ addWarn ]

        # Require new project name and confirmation
        confirmPrompt = None    # use default: I am sure I want to do this.
        if os.path.isdir(projpath):
            if warns:
                warns += [ '' ]  # blank line between addWarn and below two Warnings:
            if os.path.isdir(bakpath):
                warns += [ 'Warning: Replacing EXISTING: ' + name + ' AND ' + bakname + '!' ]
            else:
                warns += [ 'Warning: Replacing EXISTING: ' + name + '!' ]
            warns += [ 'Warning: Check for & exit any Electric,magic,qflow... for above project(s)!\n' ]
            confirmPrompt = 'I checked & exited apps and am sure I want to do this.'

        warns += [ 'Confirm import-as new project: ' + name + '?' ]
        warning = '\n'.join(warns)
        confirm = ProtectedConfirmDialog(self, warning, confirmPrompt=confirmPrompt).result
        if not confirm == 'okay':
            return

        print('New project name will be ' + name + '.')
        try:
            if os.path.isdir(projpath):
                if os.path.isdir(bakpath):
                    print('Deleting old project: ' + bakpath);
                    shutil.rmtree(bakpath)
                print('Moving old project ' + name + ' to ' + bakname)
                os.rename(                projpath,           bakpath)
            print("Importing as new project " + name)
            os.rename(importfile, projpath)
            return True
        except IOError as e:
            print("Error importing-as project: " + str(e))
            return None

    #----------------------------------------------------------------------
    # Helper subroutine:
    # Check if a project is a valid project.  Return the name of the
    # datasheet if the project has a valid one in the project top level
    # path.
    #----------------------------------------------------------------------

    def get_datasheet_name(self, dpath):
        if not os.path.isdir(dpath):
            print('Error:  Project is not a folder!')
            return
        # Check for valid datasheet name in the following order:
        # (1) project.json (Legacy)
        # (2) <name of directory>.json (Legacy)
        # (3) not "datasheet.json" or "datasheet_anno.json" 
        # (4) "datasheet.json"
        # (5) "datasheet_anno.json"

        dsname = os.path.split(dpath)[1]
        if os.path.isfile(dpath + '/project.json'):
            datasheet = dpath + '/project.json'
        elif os.path.isfile(dpath + '/' + dsname + '.json'):
            datasheet = dpath + '/' + dsname + '.json'
        else:
            has_generic = False
            has_generic_anno = False
            filelist = os.listdir(dpath)
            for file in filelist[:]:
                if os.path.splitext(file)[1] != '.json':
                    filelist.remove(file)
            if 'datasheet.json' in filelist:
                has_generic = True
                filelist.remove('datasheet.json')
            if 'datasheet_anno.json' in filelist:
                has_generic_anno = True
                filelist.remove('datasheet_anno.json')
            if len(filelist) == 1:
                print('Trying ' + dpath + '/' + filelist[0])
                datasheet = dpath + '/' + filelist[0]
            elif has_generic:
                datasheet + dpath + '/datasheet.json'
            elif has_generic_anno:
                datasheet + dpath + '/datasheet_anno.json'
            else:
                if len(filelist) > 1:
                    print('Error:  Path ' + dpath + ' has ' + str(len(filelist)) +
                            ' valid datasheets.')
                else:
                    print('Error:  Path ' + dpath + ' has no valid datasheets.')
                return None

        if not os.path.isfile(datasheet):
            print('Error:  File ' + datasheet + ' not found.')
            return None
        else:
            return datasheet

    #----------------------------------------------------------------------
    # Run the LVS manager
    #----------------------------------------------------------------------

    def run_lvs(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            designname = self.project_name
            print('Run LVS on design ' + designname + ' (' + design + ')')
            # use Popen, not run, so that application does not wait for it to exit.
            subprocess.Popen(['netgen','-gui',design, designname])
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the local characterization checker
    #----------------------------------------------------------------------

    def characterize(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            designname = self.project_name
            datasheet = self.get_datasheet_name(design)
            print('Characterize design ' + designname + ' (' + datasheet + ' )')
            if datasheet:
                # use Popen, not run, so that application does not wait for it to exit.
                dsheetroot = os.path.splitext(datasheet)[0]
                subprocess.Popen([config.apps_path + '/cace.py',
				datasheet])
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the local synthesis tool (qflow)
    #----------------------------------------------------------------------

    def synthesize(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0] # project path
            pdkdir = self.get_pdk_dir(design, path = True)
            qflowdir = pdkdir + 'libs.tech/qflow'
            # designname = value['text']
            designname = self.project_name
            development = self.prefs['devstdcells']
            if not designname:
                # A project without a datasheet has no designname (which comes from
                # the 'ip-name' record in the datasheet JSON) but can still be
                # synthesized.
                designname = design

            # Normally there is one digital design in a project.  However, full-chip
            # designs (in particular) may have multiple sub-projects that are
            # independently synthesized digital blocks.  Find all subdirectories of
            # the top level or subdirectories of qflow that contain a 'qflow_vars.sh'
            # file.  If there is more than one, then present a list.  If there is
            # only one but it is not in 'qflow/', then be sure to pass the actual
            # directory name to the qflow manager.
            qvlist = glob.glob(design + '/*/qflow_vars.sh')
            qvlist.extend(glob.glob(design + '/qflow/*/qflow_vars.sh'))
            if len(qvlist) > 1 or (len(qvlist) == 1 and not os.path.exists(design + '/qflow/qflow_vars.sh')):
                # Generate selection menu
                if len(qvlist) > 1:
                    clist = list(os.path.split(item)[0] for item in qvlist)
                    ppath = ExistingProjectDialog(self, clist, warning="Enter name of qflow project to open:").result
                    if not ppath:
                        return 0		# Canceled in dialog, no action.
                else:
                    ppath = os.path.split(qvlist[0])[0]

                # pname is everything in ppath after matching design:
                pname = ppath.replace(design + '/', '')

                print('Synthesize design in qflow project directory ' + pname)
                print('Loading digital flow manager...')
                #TODO: replace hard-coded path with function that gets the qflow manager path
                if development:
                    subprocess.Popen(['/usr/local/share/qflow/scripts/qflow_manager.py',
				qflowdir, design, '-development', '-subproject=' + pname])
                else:
                    subprocess.Popen(['/usr/local/share/qflow/scripts/qflow_manager.py',
				qflowdir, design, '-subproject=' + pname])
            else:
                print('Synthesize design ' + designname + ' (' + design + ')')
                print('Loading digital flow manager...')
                # use Popen, not run, so that application does not wait for it to exit.
                if development:
                    subprocess.Popen(['/usr/local/share/qflow/scripts/qflow_manager.py',
				qflowdir, design, designname, '-development'])
                else:
                    subprocess.Popen(['/usr/local/share/qflow/scripts/qflow_manager.py',
                qflowdir, design, designname])
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Switch between showing and hiding the import list (default hidden)
    #----------------------------------------------------------------------

    def import_toggle(self):
        import_state = self.toppane.import_frame.import_header3.cget('text')
        if import_state == '+':
            self.importselect.grid(row = 11, sticky = 'news')
            self.toppane.import_frame.import_header3.config(text='-')
        else:
            self.importselect.grid_forget()
            self.toppane.import_frame.import_header3.config(text='+')

    def import_open(self):
        self.importselect.grid(row = 11, sticky = 'news')
        self.toppane.import_frame.import_header3.config(text='-')

    #----------------------------------------------------------------------
    # Switch between showing and hiding the IP library list (default hidden)
    #----------------------------------------------------------------------

    def library_toggle(self):
        library_state = self.toppane.library_frame.library_header3.cget('text')
        if library_state == '+':
            self.ipselect.grid(row = 8, sticky = 'news')
            self.toppane.library_frame.library_header3.config(text='-')
        else:
            self.ipselect.grid_forget()
            self.toppane.library_frame.library_header3.config(text='+')

    def library_open(self):
        self.ipselect.grid(row = 8, sticky = 'news')
        self.toppane.library_frame.library_header3.config(text='-')

    #----------------------------------------------------------------------
    # Run padframe-calc (today internally invokes libreoffice, we only need cwd set to design project)
    #----------------------------------------------------------------------
    def padframe_calc(self):
        value = self.projectselect.selected()
        if value:
            designname = self.project_name
            self.padframe_calc_work(newname=designname)
        else:
            print("You must first select a project.", file=sys.stderr)

    #------------------------------------------------------------------------
    # Run padframe-calc (today internally invokes libreoffice, we set cwd to design project)
    # Modelled somewhat after 'def importvgl':
    #   Prompt for an existing electric lib.
    #   Prompt for a target cellname (for both mag and electric icon).
    # (The AS vs INTO behavior is incomplete as yet. Used so far with current-project as newname arg).
    #   newname : target project-name (INTO), or None (AS: i.e. prompt to create one).
    # Either newname is given: we PROMPT to pick an existing elecLib;
    # Else PROMPT for new projectName and CREATE it (and use elecLib of same name).
    #------------------------------------------------------------------------
    def padframe_calc_work(self, newname=None):
        elecLib = newname
        isnew = not newname
        if isnew:
            # Use create project code first to generate a valid project space.
            newname = self.createproject(None)
            if not newname: return 0		# Canceled in dialog, no action.
            # print("padframe-calc in new project " + newname + ".")
            elecLib = newname

        # For life of this projectManager process, store/recall last PadFrame Settings per project
        global project2pfd
        try:
            project2pfd
        except:
            project2pfd = {}
        if newname not in project2pfd:
            project2pfd[newname] = {"libEntry": None, "cellName": None}

        ppath = self.projectdir + '/' + newname
        choices = self.get_elecLib_list(newname)
        if not choices:
            print( "Aborted: No existing electric libraries found to write symbol into.")
            return 0
                
        elecLib = newname + '/elec/' + elecLib + '.delib'
        elecLib = project2pfd[newname]["libEntry"] or elecLib
        cellname = project2pfd[newname]["cellName"] or "padframe"
        libAndCell = ExistingElecLibCellDialog(self, None, title="PadFrame Settings", plist=choices, descPost="of icon&layout", seedLibNm=elecLib, seedCellNm=cellname).result
        if not libAndCell:
            return 0		# Canceled in dialog, no action.
            
        (elecLib, cellname) = libAndCell
        if not cellname:
            return 0		# empty cellname, no action.

        project2pfd[newname]["libEntry"] = elecLib
        project2pfd[newname]["cellName"] = cellname

        # Isolate just electric lib name without extension. ../a/b.delib -> b
        elecLib = os.path.splitext(os.path.split(elecLib)[-1])[0]
        print("padframe-calc in project: %s, elecLib: %s, cellName: %s" % (newname, elecLib, cellname))

        export = dict(os.environ)
        export['EF_DESIGNDIR'] = ppath
        subprocess.Popen(['/ef/apps/bin/padframe-calc', elecLib, cellname], cwd = ppath, env = export)

        # not yet any useful return value or reporting of results here in projectManager...
        return 1

    #----------------------------------------------------------------------
    # Run the schematic editor (tool as given by user preference)
    #----------------------------------------------------------------------

    def edit_schematic(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            
            pdktechdir = design + self.config_path(design)+'/techdir/libs.tech'
            
            applist = self.list_valid_schematic_editors(pdktechdir)

            if len(applist)==0:
                print("Unable to find a valid schematic editor.")
                return
                
            # If the preferred app is in the list, then use it.
            
            if self.prefs['schemeditor'] in applist:
                appused = self.prefs['schemeditor']
            else:
                appused = applist[0]

            if appused == 'xcircuit':
                return self.edit_schematic_with_xcircuit()
            elif appused == 'xschem':
                return self.edit_schematic_with_xschem()
            elif appused == 'electric':
                return self.edit_schematic_with_electric()
            else:
                print("Unknown/unsupported schematic editor " + appused + ".", file=sys.stderr)

        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the schematic editor (electric)
    #----------------------------------------------------------------------

    def edit_schematic_with_electric(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            # self.project_name set by setcurrent.  This is the true project
            # name, as opposed to the directory name.
            designname = self.project_name
            print('Edit schematic ' + designname + ' (' + design + ' )')
            # Collect libs on command-line;  electric opens these in Explorer
            libs = []
            ellibrex = re.compile(r'^(tech_.*|ef_examples)\.[dj]elib$', re.IGNORECASE)

            self.reinitElec(design)

            # /elec and /.java are prerequisites for running electric
            if not os.path.exists(design + '/elec'):
                print("No path to electric design folder.")
                return

            if not os.path.exists(design + '/elec/.java'):
                print("No path to electric .java folder.")
                return

            # Fix the LIBDIRS file if needed
            #fix_libdirs(design, create = True)

            # Check for legacy directory (missing .ef-config and/or .ef-config/techdir);
            # Handle as necessary.

            # don't sometimes yield pdkdir as some subdir of techdir
            pdkdir = design + self.config_path(design) + '/techdir/'
            if not os.path.exists(pdkdir):
                export = dict(os.environ)
                export['EF_DESIGNDIR'] = design
                '''
                p = subprocess.run(['/ef/efabless/bin/ef-config', '-sh', '-t'],
			stdout = subprocess.PIPE, env = export)
                config_out = p.stdout.splitlines()
                for line in config_out:
                    setline = line.decode('utf-8').split('=')
                    if setline[0] == 'EF_TECHDIR':
                        pdkdir = re.sub("[';]", "", setline[1])
                '''

            for subpath in ('libs.tech/elec/', 'libs.ref/elec/'):
                pdkelec = os.path.join(pdkdir, subpath)
                if os.path.exists(pdkelec) and os.path.isdir(pdkelec):
                    # don't use os.walk(), it is recursive, wastes time
                    for entry in os.scandir(pdkelec):
                        if ellibrex.match(entry.name):
                                libs.append(entry.path)

            # Locate most useful project-local elec-lib to open on electric cmd-line.
            designroot = os.path.split(design)[1]
            finalInDesDirLibAdded = False
            if os.path.exists(design + '/elec/' + designname + '.jelib'):
                libs.append(design + '/elec/' + designname + '.jelib')
                finalInDesDirLibAdded = True
            elif os.path.isdir(design + '/elec/' + designname + '.delib'):
                libs.append(design + '/elec/' + designname + '.delib')
                finalInDesDirLibAdded = True
            else:
                # Alternative path is the project name + .delib
                if os.path.isdir(design + '/elec/' + designroot + '.delib'):
                    libs.append(design + '/elec/' + designroot + '.delib')
                    finalInDesDirLibAdded = True

            # Finally, check for the one absolute requirement for a project,
            # which is that there must be a symbol designname + .ic in the
            # last directory.  If not, then do a search for it.
            if not finalInDesDirLibAdded or not os.path.isfile(libs[-1] + '/' + designname + '.ic'):
                delibdirs = os.listdir(design + '/elec')
                for delibdir in delibdirs:
                    if os.path.splitext(delibdir)[1] == '.delib':
                        iconfiles = os.listdir(design + '/elec/' + delibdir)
                        for iconfile in iconfiles:
                            if iconfile == designname + '.ic':
                                libs.append(design + '/elec/' + delibdir)
                                finalInDesDirLibAdded = True
                                break
            
            # Above project-local lib-adds are all conditional on finding some lib
            # with an expected name or content: all of which may fail.
            # Force last item ALWAYS to be 'a path' in the project's elec/ dir.
            # Usually it's a real library (found above). (If lib does not exist the messages
            # window does get an error message). But the purpose is for the universal side-effect:
            # To EVERY TIME reseed the File/OpenLibrary dialogue WorkDir to start in
            # project's elec/ dir; avoid it starting somewhere in the PDK, which
            # is what will happen if last actual cmd-line arg is a lib in the PDK, and
            # about which users have complained. (Optimal fix needs electric enhancement).
            if not finalInDesDirLibAdded:
                libs.append(design + '/elec/' + designroot + '.delib')

            # Pull last item from libs and make it a command-line argument.
            # All other libraries become part of the EOPENARGS environment variable,
            # and electric is called with the elecOpen.bsh script.
            indirectlibs = libs[:-1]
            export = dict(os.environ)
            arguments = []
            if indirectlibs:
                export['EOPENARGS'] = ' '.join(indirectlibs)
                arguments.append('-s')
                arguments.append('/ef/efabless/lib/elec/elecOpen.bsh')

            try:
                arguments.append(libs[-1])
            except IndexError:
                print('Error:  Electric project directories not set up correctly?')
            else:
                subprocess.Popen(['electric', *arguments], cwd = design + '/elec',
				env = export)
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the schematic editor (xcircuit)
    #----------------------------------------------------------------------

    def edit_schematic_with_xcircuit(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            # self.project_name set by setcurrent.  This is the true project
            # name, as opposed to the directory name.
            designname = self.project_name
            print('Edit schematic ' + designname + ' (' + design + ' )')
            xcircdirpath = design + '/xcirc'
            pdkdir = design + self.config_path(design) + '/techdir/libs.tech/xcircuit'

            # /xcirc directory is a prerequisite for running xcircuit.  If it doesn't
            # exist, create it and seed it with .xcircuitrc from the tech directory
            if not os.path.exists(xcircdirpath):
                os.makedirs(xcircdirpath)

            # Copy xcircuit startup file from tech directory
            hasxcircrcfile = os.path.exists(xcircdirpath + '/.xcircuitrc')
            if not hasxcircrcfile:
                if os.path.exists(pdkdir + '/xcircuitrc'):
                    shutil.copy(pdkdir + '/xcircuitrc', xcircdirpath + '/.xcircuitrc')

            # Command line argument is the project name
            arguments = [design + '/xcirc' + designname]
            subprocess.Popen(['xcircuit', *arguments])
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the schematic editor (xschem)
    #----------------------------------------------------------------------

    def edit_schematic_with_xschem(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # self.project_name set by setcurrent.  This is the true project
            # name, as opposed to the directory name.
            designname = self.project_name
            print('Edit schematic ' + designname + ' (' + design + ' )')
            xschemdirpath = design + '/xschem'
            
            pdkdir = design + self.config_path(design) + '/techdir/libs.tech/xschem'

            
            # /xschem directory is a prerequisite for running xschem.  If it doesn't
            # exist, create it and seed it with xschemrc from the tech directory
            if not os.path.exists(xschemdirpath):
                os.makedirs(xschemdirpath)

            # Copy xschem startup file from tech directory
            hasxschemrcfile = os.path.exists(xschemdirpath + '/xschemrc')
            if not hasxschemrcfile:
                if os.path.exists(pdkdir + '/xschemrc'):
                    shutil.copy(pdkdir + '/xschemrc', xschemdirpath + '/xschemrc')

            # Command line argument is the project name.  The "-r" option is recommended if there
            # is no stdin/stdout piping.
            
            arguments = ['-r', design + '/xschem/' + designname]
            subprocess.Popen(['xschem', *arguments])
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the layout editor (magic or klayout)
    #----------------------------------------------------------------------

    def edit_layout(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            pdktechdir = design + self.config_path(design) + '/techdir/libs.tech'
            
            applist = self.list_valid_layout_editors(pdktechdir)

            if len(applist)==0:
                print("Unable to find a valid layout editor.")
                return

            # If the preferred app is in the list, then use it.
            if self.prefs['layouteditor'] in applist:
                appused = self.prefs['layouteditor']
            else:
                appused = applist[0]

            if appused == 'magic':
                return self.edit_layout_with_magic()
            elif appused == 'klayout':
                return self.edit_layout_with_klayout()
            elif appused == 'electric':
                return self.edit_layout_with_electric()
            else:
                print("Unknown/unsupported layout editor " + appused + ".", file=sys.stderr)

        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the magic layout editor
    #----------------------------------------------------------------------

    def edit_layout_with_magic(self):
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            designname = self.project_name
            
            pdkdir = ''
            pdkname = ''
            
            if os.path.exists(design + '/.ef-config/techdir/libs.tech'):
                pdkdir = design + '/.ef-config/techdir/libs.tech/magic/current'
                pdkname = os.path.split(os.path.realpath(design + '/.ef-config/techdir'))[1]
            elif os.path.exists(design + '/.config/techdir/libs.tech'):
                pdkdir = design + '/.config/techdir/libs.tech/magic'
                pdkname = os.path.split(os.path.realpath(design + '/.config/techdir'))[1]
            

            # Check if the project has a /mag directory.  Create it and
            # put the correct .magicrc file in it, if it doesn't.
            magdirpath = design + '/mag'
            hasmagdir = os.path.exists(magdirpath)
            if not hasmagdir:
                os.makedirs(magdirpath)

            hasmagrcfile = os.path.exists(magdirpath + '/.magicrc')
            if not hasmagrcfile:
                shutil.copy(pdkdir + '/' + pdkname + '.magicrc', magdirpath + '/.magicrc')

            # Check if the .mag file exists for the project.  If not,
            # generate a dialog.
            magpath = design + '/mag/' + designname + '.mag'
            netpath = design + '/spi/' + designname + '.spi'
            # print("magpath is " + magpath)
            hasmag = os.path.exists(magpath)
            hasnet = os.path.exists(netpath)
            if hasmag:
                if hasnet:
                    statbuf1 = os.stat(magpath)
                    statbuf2 = os.stat(netpath)
                    # No specific action for out-of-date layout.  To be done:
                    # Check contents and determine if additional devices need to
                    # be added to the layout.  This may be more trouble than it's
                    # worth.
                    #
                    # if statbuf2.st_mtime > statbuf1.st_mtime:
                    #     hasmag = False

            if not hasmag:
                # Does the project have any .mag files at all?  If so, the project
                # layout may be under a name different than the project name.  If
                # so, present the user with a selectable list of layout names,
                # with the option to start a new layout or import from schematic.

                maglist = os.listdir(design + '/mag/')
                if len(maglist) > 1:
                    # Generate selection menu
                    warning = 'No layout matches IP name ' + designname + '.'
                    maglist = list(item for item in maglist if os.path.splitext(item)[1] == '.mag')
                    clist = list(os.path.splitext(item)[0] for item in maglist)
                    ppath = EditLayoutDialog(self, clist, ppath=design,
					pname=designname, warning=warning,
					hasnet=hasnet).result
                    if not ppath:
                        return 0		# Canceled in dialog, no action.
                    elif ppath != '(New layout)':
                        hasmag = True
                        designname = ppath
                elif len(maglist) == 1:
                    # Only one magic file, no selection, just bring it up.
                    designname = os.path.split(maglist[0])[1]
                    hasmag = True

            if not hasmag:
                populate = NewLayoutDialog(self, "No layout for project.").result
                if not populate:
                    return 0	# Canceled, no action.
                elif populate():
                    # Name of PDK deprecated.  The .magicrc file in the /mag directory
                    # will load the correct PDK and specify the proper library for the
                    # low-level device namespace, which may not be the same as techdir.
                    # NOTE:  netlist_to_layout script will attempt to generate a
                    # schematic netlist if one does not exist.

                    print('Running /ef/efabless/bin/netlist_to_layout.py ../spi/' + designname + '.spi')
                    try:
                        p = subprocess.run(['/ef/efabless/bin/netlist_to_layout.py',
					'../spi/' + designname + '.spi'],
					stdin = subprocess.PIPE, stdout = subprocess.PIPE,
					stderr = subprocess.PIPE, cwd = design + '/mag')
                        if p.stderr:
                            err_string = p.stderr.splitlines()[0].decode('utf-8')
                            # Print error messages to console
                            print(err_string)

                    except subprocess.CalledProcessError as e:
                        print('Error running netlist_to_layout.py: ' + e.output.decode('utf-8'))
                    else:
                        if os.path.exists(design + '/mag/create_script.tcl'):
                            with open(design + '/mag/create_script.tcl', 'r') as infile:
                                magproc = subprocess.run(['/ef/apps/bin/magic',
					'-dnull', '-noconsole', '-rcfile ',
					pdkdir + '/' + pdkname + '.magicrc', designname],
					stdin = infile, stdout = subprocess.PIPE,
					stderr = subprocess.PIPE, cwd = design + '/mag')
                            print("Populated layout cell")
                            # os.remove(design + '/mag/create_script.tcl')
                        else:
                            print("No device generating script was created.", file=sys.stderr)

            print('Edit layout ' + designname + ' (' + design + ' )')

            magiccommand = ['magic']
            # Select the graphics package used by magic from the profile settings.
            if 'magic-graphics' in self.prefs:
                magiccommand.extend(['-d', self.prefs['magic-graphics']])
            # Check if .magicrc predates the latest and warn if so.
            statbuf1 = os.stat(design + '/mag/.magicrc')
            statbuf2 = os.stat(pdkdir + '/' + pdkname + '.magicrc')
            if statbuf2.st_mtime > statbuf1.st_mtime:
                print('NOTE:  File .magicrc predates technology startup file.  Using default instead.')
                magiccommand.extend(['-rcfile', pdkdir + '/' + pdkname + '.magicrc'])
            magiccommand.append(designname)

            # Run magic and don't wait for it to finish
            subprocess.Popen(magiccommand, cwd = design + '/mag')
        else:
            print("You must first select a project.", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the klayout layout editor
    #----------------------------------------------------------------------

    def edit_layout_with_klayout(self):
        value = self.projectselect.selected()
        print("Klayout unsupported from project manager (work in progress);  run manually", file=sys.stderr)

    #----------------------------------------------------------------------
    # Run the electric layout editor
    #----------------------------------------------------------------------

    def edit_layout_with_electric(self):
        value = self.projectselect.selected()
        print("Electric layout editing unsupported from project manager (work in progress);  run manually", file=sys.stderr)

    #----------------------------------------------------------------------
    # Upload design to the marketplace
    # NOTE:  This is not being called by anything.  Use version in the
    # characterization script, which can check for local results before
    # approving (or forcing) an upload.
    #----------------------------------------------------------------------

    def upload(self):
        '''
        value = self.projectselect.selected()
        if value:
            design = value['values'][0]
            # designname = value['text']
            designname = self.project_name
            print('Upload design ' + designname + ' (' + design + ' )')
            subprocess.run(['/ef/apps/bin/withnet',
			config.apps_path + '/cace_design_upload.py',
			design, '-test'])
	'''

    #--------------------------------------------------------------------------
    # Upload a datasheet to the marketplace (Administrative use only, for now)
    #--------------------------------------------------------------------------

    # def make_challenge(self):
    #      importp = self.cur_import
    #      print("Make a Challenge from import " + importp + "!")
    #      # subprocess.run([config.apps_path + '/cace_import_upload.py', importp, '-test'])

    # Runs whenever a user selects a project
    def setcurrent(self, value):
        global currdesign
        treeview = value.widget
        selection = treeview.item(treeview.selection()) # dict with text, values, tags, etc. as keys
        pname = selection['text']
        pdir = treeview.selection()[0]  # iid of the selected project
        #print("setcurrent returned value " + pname)
        metapath = os.path.expanduser(currdesign)
        if not os.path.exists(metapath):
            os.makedirs(os.path.split(metapath)[0], exist_ok=True)
        with open(metapath, 'w') as f:
            f.write(pdir + '\n')

        # Pick up the PDK from "values", use it to find the PDK folder, determine
        # if it has a "magic" subfolder, and enable/disable the "Edit Layout"
        # button accordingly
        
        svalues = selection['values']
        #print("svalues :"+str(svalues))
        pdkitems = svalues[1].split()
        pdkdir = ''
        
        ef_style=False
        
        if os.path.exists(svalues[0] + '/.config'):
            pdkdir = svalues[0] + '/.config/techdir'
        elif os.path.exists(svalues[0] + '/.ef-config'):
            pdkdir = svalues[0] + '/.ef-config/techdir'
            ef_style=True
        
        if pdkdir == '':
            print('No pdkname found; layout editing disabled')
            self.toppane.appbar.layout_button.config(state='disabled')
        else:
            try:
                if ef_style:
                    subf = os.listdir(pdkdir + '/libs.tech/magic/current')
                else:
                    subf = os.listdir(pdkdir + '/libs.tech/magic')
            except:
                print('PDK ' + pdkname + ' has no layout setup; layout editing disabled')
                self.toppane.appbar.layout_button.config(state='disabled') 
        
        # If the selected project directory has a JSON file and netlists in the "spi"
        # and "testbench" folders, then enable the "Characterize" button;  else disable
        # it.
        # NOTE:  project.json is the preferred name for the datasheet
        # file.  However, the .spi file, .delib file, etc., all have the name of the
        # project from "project_name" in the info.yaml file, which is separate from the datasheet.

        found = False
        ppath = selection['values'][0]
        yamlname = ppath + '/info.yaml'
        
        if os.path.isfile(yamlname):
            # Pull the project_name into local store
            with open(yamlname, 'r') as f:
                datatop = yaml.safe_load(f)
                project_data = datatop['project']
                ipname = project_data['project_name']
                self.project_name = ipname
        else:
            print('Setting project ip-name from the project folder name.')
            self.project_name = pname
        jsonname = ppath + '/project.json'
        if os.path.isfile(jsonname):
            with open(jsonname, 'r') as f:
                datatop = json.load(f)
                dsheet = datatop['data-sheet']
                found = True
            # Do not specifically prohibit opening the characterization app if
            # there is no schematic or netlist.  Otherwise the user is prevented
            # even from seeing the electrical parameters.  Let the characterization
            # tool allow or prohibit simulation based on this.
            # if os.path.exists(ppath + '/spi'):
            #     if os.path.isfile(ppath + '/spi/' + ipname + '.spi'):
            #         found = True
            #
            # if found == False and os.path.exists(ppath + '/elec'):
            #     if os.path.isdir(ppath + '/elec/' + ipname + '.delib'):
            #         if os.path.isfile(ppath + '/elec/' + ipname + '.delib/' + ipname + '.sch'):
            #             found = True
        else:
            # Use 'pname' as the default project name.
            print('No characterization file ' + jsonname)

        # If datasheet has physical parameters but not electrical parameters, then it's okay
        # for it not to have a testbench directory;  it's still valid.  However, having
        # neither physical nor electrical parameters means there's nothing to characterize.
        if found and 'electrical-params' in dsheet and len(dsheet['electrical-params']) > 0:
            if not os.path.isdir(ppath + '/testbench'):
                print('No testbench directory for eletrical parameter simulation methods.', file=sys.stderr)
                found = False
        elif found and not 'physical-params' in dsheet:
            print('Characterization file defines no characterization tests.', file=sys.stderr)
            found = False
        elif found and 'physical-params' in dsheet and len(dsheet['physical-params']) == 0:
            print('Characterization file defines no characterization tests.', file=sys.stderr)
            found = False

        if found == True:
            self.toppane.appbar.char_button.config(state='enabled')
        else:
            self.toppane.appbar.char_button.config(state='disabled')

        # Warning: temporary hack (Tim, 1/9/2018)
        # Pad frame generator is currently limited to the XH035 cells, so if the
        # project PDK is not XH035, disable the pad frame button

        if len(pdkitems) > 1 and pdkitems[1] == 'EFXH035B':
            self.toppane.appbar.padframeCalc_button.config(state='enabled')
        else:
            self.toppane.appbar.padframeCalc_button.config(state='disabled')

# main app. fyi: there's a 2nd/earlier __main__ section for splashscreen
if __name__ == '__main__':
    ProjectManager(root)
    if deferLoad:
        # Without this, mainloop may find&run very short clock-delayed events BEFORE main form display.
        # With it 1st project-load can be scheduled using after-time=0 (needn't tune a delay like 100ms).
        root.update_idletasks()
    root.mainloop()
