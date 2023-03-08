#!/usr/bin/env python3
#
#--------------------------------------------------------
# Project Manager GUI.
#
# This is a Python tkinter script that handles local
# project management.  Much of this involves the
# running of ng-spice for characterization, allowing
# the user to determine where a circuit is failing
# characterization;  and when the design passes local
# characterization, it may be submitted to the
# marketplace for official characterization.
#
#--------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# September 9, 2016
# Version 1.0
#--------------------------------------------------------

import io
import re
import os
import sys
import copy
import json
import time
import signal
import select
import datetime
import contextlib
import subprocess
import faulthandler

import tkinter
from tkinter import ttk
from tkinter import filedialog

import tksimpledialog
import tooltip
from consoletext import ConsoleText
from helpwindow import HelpWindow
from failreport import FailReport
from textreport import TextReport
from editparam import EditParam
from settings import Settings
from simhints import SimHints

# User preferences file (if it exists)
prefsfile = '~/design/.profile/prefs.json'

# Application path (path where this script is located)
apps_path = os.path.realpath(os.path.dirname(__file__))

#------------------------------------------------------
# Simple dialog for confirming quit or upload
#------------------------------------------------------

class ConfirmDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed):
        ttk.Label(master, text=warning, wraplength=500).grid(row = 0, columnspan = 2, sticky = 'wns')
        return self

    def apply(self):
        return 'okay'

#------------------------------------------------------
# Simple dialog with no "OK" button (can only cancel)
#------------------------------------------------------

class PuntDialog(tksimpledialog.Dialog):
    def body(self, master, warning, seed):
        if warning:
            ttk.Label(master, text=warning, wraplength=500).grid(row = 0, columnspan = 2, sticky = 'wns')
        return self

    def buttonbox(self):
        # Add button box with "Cancel" only.
        box = ttk.Frame(self.obox)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side='left', padx=5, pady=5)
        self.bind("<Escape>", self.cancel)
        box.pack(fill='x', expand='true')

    def apply(self):
        return 'okay'

#------------------------------------------------------
# Main class for this application
#------------------------------------------------------

class CACECharacterize(ttk.Frame):
    """local characterization GUI."""

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()
        parent.protocol("WM_DELETE_WINDOW", self.on_quit)

    def on_quit(self):
        """Exits program."""
        if not self.check_saved():
            warning = 'Warning:  Simulation results have not been saved.'
            confirm = ConfirmDialog(self, warning).result
            if not confirm == 'okay':
                print('Quit canceled.')
                return
        if self.logfile:
            self.logfile.close()
        quit()

    def on_mousewheel(self, event):
        if event.num == 5:
            self.datasheet_viewer.yview_scroll(1, "units")
        elif event.num == 4:
            self.datasheet_viewer.yview_scroll(-1, "units")

    def init_gui(self):
        """Builds GUI."""
        global prefsfile

        message = []
        fontsize = 11

        # Read user preferences file, get default font size from it.
        prefspath = os.path.expanduser(prefsfile)
        if os.path.exists(prefspath):
            with open(prefspath, 'r') as f:
                self.prefs = json.load(f)
            if 'fontsize' in self.prefs:
                fontsize = self.prefs['fontsize']
        else:
            self.prefs = {}

        s = ttk.Style()

        available_themes = s.theme_names()
        s.theme_use(available_themes[0])

        s.configure('bg.TFrame', background='gray40')
        s.configure('italic.TLabel', font=('Helvetica', fontsize, 'italic'))
        s.configure('title.TLabel', font=('Helvetica', fontsize, 'bold italic'),
			foreground = 'brown', anchor = 'center')
        s.configure('normal.TLabel', font=('Helvetica', fontsize))
        s.configure('red.TLabel', font=('Helvetica', fontsize), foreground = 'red')
        s.configure('green.TLabel', font=('Helvetica', fontsize), foreground = 'green3')
        s.configure('blue.TLabel', font=('Helvetica', fontsize), foreground = 'blue')
        s.configure('hlight.TLabel', font=('Helvetica', fontsize), background='gray93')
        s.configure('rhlight.TLabel', font=('Helvetica', fontsize), foreground = 'red',
			background='gray93')
        s.configure('ghlight.TLabel', font=('Helvetica', fontsize), foreground = 'green3',
			background='gray93')
        s.configure('blue.TLabel', font=('Helvetica', fontsize), foreground = 'blue')
        s.configure('blue.TMenubutton', font=('Helvetica', fontsize), foreground = 'blue',
			border = 3, relief = 'raised')
        s.configure('normal.TButton', font=('Helvetica', fontsize),
			border = 3, relief = 'raised')
        s.configure('red.TButton', font=('Helvetica', fontsize), foreground = 'red',
			border = 3, relief = 'raised')
        s.configure('green.TButton', font=('Helvetica', fontsize), foreground = 'green3',
			border = 3, relief = 'raised')
        s.configure('hlight.TButton', font=('Helvetica', fontsize),
			border = 3, relief = 'raised', background='gray93')
        s.configure('rhlight.TButton', font=('Helvetica', fontsize), foreground = 'red',
			border = 3, relief = 'raised', background='gray93')
        s.configure('ghlight.TButton', font=('Helvetica', fontsize), foreground = 'green3',
			border = 3, relief = 'raised', background='gray93')
        s.configure('blue.TButton', font=('Helvetica', fontsize), foreground = 'blue',
			border = 3, relief = 'raised')
        s.configure('redtitle.TButton', font=('Helvetica', fontsize, 'bold italic'),
			foreground = 'red', border = 3, relief = 'raised')
        s.configure('bluetitle.TButton', font=('Helvetica', fontsize, 'bold italic'),
			foreground = 'blue', border = 3, relief = 'raised')

        # Create the help window
        self.help = HelpWindow(self, fontsize = fontsize)

        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            self.help.add_pages_from_file(apps_path + '/characterize_help.txt')
            message = buf.getvalue()

        # Set the help display to the first page
        self.help.page(0)

        # Create the failure report window
        self.failreport = FailReport(self, fontsize = fontsize)

        # LVS results get a text window of results
        self.textreport = TextReport(self, fontsize = fontsize)

        # Create the settings window
        self.settings = Settings(self, fontsize = fontsize, callback = self.callback)

        # Create the simulation hints window
        self.simhints = SimHints(self, fontsize = fontsize)

        # Create the edit parameter window
        self.editparam = EditParam(self, fontsize = fontsize)

        # Variables used by option menus and other stuff
        self.origin = tkinter.StringVar(self)
        self.cur_project = tkinter.StringVar(self)
        self.cur_datasheet = "(no selection)"
        self.datatop = {}
        self.status = {}
        self.caceproc = None
        self.logfile = None

        # Root window title
        self.root.title('Characterization')
        self.root.option_add('*tearOff', 'FALSE')
        self.pack(side = 'top', fill = 'both', expand = 'true')

        pane = tkinter.PanedWindow(self, orient = 'vertical', sashrelief='groove', sashwidth=6)
        pane.pack(side = 'top', fill = 'both', expand = 'true')
        self.toppane = ttk.Frame(pane)
        self.botpane = ttk.Frame(pane)

        # Get username
        if 'username' in self.prefs:
            username = self.prefs['username']
        else:
            username = os.environ['USER']

        # Label with the user
        self.toppane.title_frame = ttk.Frame(self.toppane)
        self.toppane.title_frame.grid(column = 0, row=0, sticky = 'nswe')

        self.toppane.title_frame.title = ttk.Label(self.toppane.title_frame, text='User:', style = 'red.TLabel')
        self.toppane.title_frame.user = ttk.Label(self.toppane.title_frame, text=username, style = 'blue.TLabel')

        self.toppane.title_frame.title.grid(column=0, row=0, ipadx = 5)
        self.toppane.title_frame.user.grid(column=1, row=0, ipadx = 5)

        #---------------------------------------------
        ttk.Separator(self.toppane, orient='horizontal').grid(column = 0, row = 1, sticky = 'nswe')
        #---------------------------------------------

        self.toppane.title2_frame = ttk.Frame(self.toppane)
        self.toppane.title2_frame.grid(column = 0, row = 2, sticky = 'nswe')
        self.toppane.title2_frame.datasheet_label = ttk.Label(self.toppane.title2_frame, text="Datasheet:",
		style = 'normal.TLabel')
        self.toppane.title2_frame.datasheet_label.grid(column=0, row=0, ipadx = 5)

        # New datasheet select button
        self.toppane.title2_frame.datasheet_select = ttk.Button(self.toppane.title2_frame,
		text=self.cur_datasheet, style='normal.TButton', command=self.choose_datasheet)
        self.toppane.title2_frame.datasheet_select.grid(column=1, row=0, ipadx = 5)

        tooltip.ToolTip(self.toppane.title2_frame.datasheet_select,
			text = "Select new datasheet file")

        # Show path to datasheet
        self.toppane.title2_frame.path_label = ttk.Label(self.toppane.title2_frame, text=self.cur_datasheet,
		style = 'normal.TLabel')
        self.toppane.title2_frame.path_label.grid(column=2, row=0, ipadx = 5, padx = 10)

        # Spacer in middle moves selection button to right
        self.toppane.title2_frame.sep_label = ttk.Label(self.toppane.title2_frame, text=' ',
		style = 'normal.TLabel')
        self.toppane.title2_frame.sep_label.grid(column=3, row=0, ipadx = 5, padx = 10)
        self.toppane.title2_frame.columnconfigure(3, weight = 1)
        self.toppane.title2_frame.rowconfigure(0, weight=0)

        # Selection for origin of netlist
        self.toppane.title2_frame.origin_label = ttk.Label(self.toppane.title2_frame,
		text='Netlist from:', style = 'normal.TLabel')
        self.toppane.title2_frame.origin_label.grid(column=4, row=0, ipadx = 5, padx = 10)

        self.origin.set('Schematic Capture')
        self.toppane.title2_frame.origin_select = ttk.OptionMenu(self.toppane.title2_frame,
		self.origin, 'Schematic Capture', 'Schematic Capture', 'Layout Extracted',
		style='blue.TMenubutton', command=self.load_results)
        self.toppane.title2_frame.origin_select.grid(column=5, row=0, ipadx = 5)

        #---------------------------------------------
        ttk.Separator(self.toppane, orient='horizontal').grid(column = 0, row = 3, sticky = 'news')
        #---------------------------------------------

        # Datasheet information goes here when datasheet is loaded.
        self.mframe = ttk.Frame(self.toppane)
        self.mframe.grid(column = 0, row = 4, sticky = 'news')

        # Row 4 (mframe) is expandable, the other rows are not.
        self.toppane.rowconfigure(0, weight = 0)
        self.toppane.rowconfigure(1, weight = 0)
        self.toppane.rowconfigure(2, weight = 0)
        self.toppane.rowconfigure(3, weight = 0)
        self.toppane.rowconfigure(4, weight = 1)
        self.toppane.columnconfigure(0, weight = 1)

        #---------------------------------------------
        # ttk.Separator(self, orient='horizontal').grid(column=0, row=5, sticky='ew')
        #---------------------------------------------

        # Add a text window below the datasheet to capture output.  Redirect
        # print statements to it.

        self.botpane.console = ttk.Frame(self.botpane)
        self.botpane.console.pack(side = 'top', fill = 'both', expand = 'true')

        self.text_box = ConsoleText(self.botpane.console, wrap='word', height = 4)
        self.text_box.pack(side='left', fill='both', expand='true')
        console_scrollbar = ttk.Scrollbar(self.botpane.console)
        console_scrollbar.pack(side='right', fill='y')
        # attach console to scrollbar
        self.text_box.config(yscrollcommand = console_scrollbar.set)
        console_scrollbar.config(command = self.text_box.yview)

        # Add button bar at the bottom of the window
        self.bbar = ttk.Frame(self.botpane)
        self.bbar.pack(side = 'top', fill = 'x')
        # Progress bar expands with the window, buttons don't
        self.bbar.columnconfigure(6, weight = 1)

        # Define the "quit" button and action
        self.bbar.quit_button = ttk.Button(self.bbar, text='Close', command=self.on_quit,
		style = 'normal.TButton')
        self.bbar.quit_button.grid(column=0, row=0, padx = 5)

        # Define the save button
        self.bbar.save_button = ttk.Button(self.bbar, text='Save', command=self.save_results,
		style = 'normal.TButton')
        self.bbar.save_button.grid(column=1, row=0, padx = 5)

        # Define the save-as button
        self.bbar.saveas_button = ttk.Button(self.bbar, text='Save As', command=self.save_manual,
		style = 'normal.TButton')

	# Also a load button
        self.bbar.load_button = ttk.Button(self.bbar, text='Load', command=self.load_manual,
		style = 'normal.TButton')

        # Define help button
        self.bbar.help_button = ttk.Button(self.bbar, text='Help', command=self.help.open,
		style = 'normal.TButton')
        self.bbar.help_button.grid(column = 4, row = 0, padx = 5)

        # Define settings button
        self.bbar.settings_button = ttk.Button(self.bbar, text='Settings',
		command=self.settings.open, style = 'normal.TButton')
        self.bbar.settings_button.grid(column = 5, row = 0, padx = 5)

        # Define upload action
        self.bbar.upload_button = ttk.Button(self.bbar, text='Submit', state = 'enabled',
		command=self.upload_to_marketplace, style = 'normal.TButton')
        # "Submit" button remains unplaced;  upload may be done from the web side. . .
        # self.bbar.upload_button.grid(column = 8, row = 0, padx = 5, sticky = 'ens')

        tooltip.ToolTip(self.bbar.quit_button, text = "Exit characterization tool")
        tooltip.ToolTip(self.bbar.save_button, text = "Save current characterization state")
        tooltip.ToolTip(self.bbar.saveas_button, text = "Save current characterization state")
        tooltip.ToolTip(self.bbar.load_button, text = "Load characterization state from file")
        tooltip.ToolTip(self.bbar.help_button, text = "Start help tool")
        tooltip.ToolTip(self.bbar.settings_button, text = "Manage characterization tool settings")
        tooltip.ToolTip(self.bbar.upload_button, text = "Submit completed design to Marketplace")

        # Inside frame with main electrical parameter display and scrollbar
        # To make the frame scrollable, it must be a frame inside a canvas.
        self.datasheet_viewer = tkinter.Canvas(self.mframe)
        self.datasheet_viewer.grid(row = 0, column = 0, sticky = 'nsew')
        self.datasheet_viewer.dframe = ttk.Frame(self.datasheet_viewer,
			style='bg.TFrame')
        # Place the frame in the canvas
        self.datasheet_viewer.create_window((0,0),
			window=self.datasheet_viewer.dframe,
			anchor="nw", tags="self.frame")

        # Make sure the main window resizes, not the scrollbars.
        self.mframe.rowconfigure(0, weight = 1)
        self.mframe.columnconfigure(0, weight = 1)
        # X scrollbar for datasheet viewer
        main_xscrollbar = ttk.Scrollbar(self.mframe, orient = 'horizontal')
        main_xscrollbar.grid(row = 1, column = 0, sticky = 'nsew')
        # Y scrollbar for datasheet viewer
        main_yscrollbar = ttk.Scrollbar(self.mframe, orient = 'vertical')
        main_yscrollbar.grid(row = 0, column = 1, sticky = 'nsew')
        # Attach console to scrollbars
        self.datasheet_viewer.config(xscrollcommand = main_xscrollbar.set)
        main_xscrollbar.config(command = self.datasheet_viewer.xview)
        self.datasheet_viewer.config(yscrollcommand = main_yscrollbar.set)
        main_yscrollbar.config(command = self.datasheet_viewer.yview)

        # Make sure that scrollwheel pans window
        self.datasheet_viewer.bind_all("<Button-4>", self.on_mousewheel)
        self.datasheet_viewer.bind_all("<Button-5>", self.on_mousewheel)

        # Set up configure callback
        self.datasheet_viewer.dframe.bind("<Configure>", self.frame_configure)

        # Add the panes once the internal geometry is known
        pane.add(self.toppane)
        pane.add(self.botpane)
        pane.paneconfig(self.toppane, stretch='first')

        # Initialize variables
        self.sims_to_go = []

        # Capture time of start to compare against the annotated
        # output file timestamp.
        self.starttime = time.time()

        # Redirect stdout and stderr to the console as the last thing to do. . .
        # Otherwise errors in the GUI get sucked into the void.
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = ConsoleText.StdoutRedirector(self.text_box)
        sys.stderr = ConsoleText.StderrRedirector(self.text_box)

        if message:
            print(message)

    def frame_configure(self, event):
        self.update_idletasks()
        self.datasheet_viewer.configure(scrollregion=self.datasheet_viewer.bbox("all"))

    def logstart(self):
        # Start a logfile (or append to it, if it already exists)
        # Disabled by default, as it can get very large.
        # Can be enabled from Settings.
        if self.settings.get_log() == True:
            dataroot = os.path.splitext(self.cur_datasheet)[0]
            if not self.logfile:
                self.logfile = open(dataroot + '.log', 'a')

                # Print some initial information to the logfile.
                self.logprint('-------------------------')
                self.logprint('Starting new log file ' + datetime.datetime.now().strftime('%c'),
				doflush=True)

    def logstop(self):
        if self.logfile:
            self.logprint('-------------------------', doflush=True)
            self.logfile.close()
            self.logfile = []

    def logprint(self, message, doflush=False):
        if self.logfile:
            self.logfile.buffer.write(message.encode('utf-8'))
            self.logfile.buffer.write('\n'.encode('utf-8'))
            if doflush:
                self.logfile.flush()

    def set_datasheet(self, datasheet):
        if self.logfile:
            self.logprint('end of log.')
            self.logprint('-------------------------', doflush=True)
            self.logfile.close()
            self.logfile = None

        if not os.path.isfile(datasheet):
            print('Error:  File ' + datasheet + ' not found.')
            return

        [dspath, dsname] = os.path.split(datasheet)
        # Read the datasheet
        with open(datasheet) as ifile:
            try:
                datatop = json.load(ifile)
            except json.decoder.JSONDecodeError as e:
                print("Error:  Parse error reading JSON file " + datasheet + ':')
                print(str(e))
                return
            else:
                # 'request-hash' set to '.' for local simulation
                datatop['request-hash'] = '.'
        try:
            dsheet = datatop['data-sheet']
        except KeyError:
            print("Error:  JSON file is not a datasheet!\n")
        else:
            self.datatop = datatop
            self.cur_datasheet = datasheet
            self.create_datasheet_view()
            self.toppane.title2_frame.datasheet_select.configure(text=dsname)
            self.toppane.title2_frame.path_label.configure(text=datasheet)

            # Determine if there is a saved, annotated JSON file that is
            # more recent than the netlist used for simulation.
            self.load_results()

        # Attempt to set the datasheet viewer width to the interior width
        # but do not set it larger than the available desktop.
        self.update_idletasks()
        widthnow = self.datasheet_viewer.winfo_width()
        width = self.datasheet_viewer.dframe.winfo_width()
        screen_width = self.root.winfo_screenwidth()
        if width > widthnow:
            if width < screen_width - 10:
                self.datasheet_viewer.configure(width=width)
            else:
                self.datasheet_viewer.configure(width=screen_width - 10)
        elif widthnow > screen_width:
            self.datasheet_viewer.configure(width=screen_width - 10)
        elif widthnow > width:
            self.datasheet_viewer.configure(width=width)

        # Likewise for the height, up to 3/5 of the desktop height.
        height = self.datasheet_viewer.dframe.winfo_height()
        heightnow = self.datasheet_viewer.winfo_height()
        screen_height = self.root.winfo_screenheight()
        if height > heightnow:
            if height < screen_height * 0.6:
                self.datasheet_viewer.configure(height=height)
            else:
                self.datasheet_viewer.configure(height=screen_height * 0.6)
        elif heightnow > screen_height:
            self.datasheet_viewer.configure(height=screen_height - 10)
        elif heightnow > height:
            self.datasheet_viewer.configure(height=height)

    def choose_datasheet(self):
        datasheet = filedialog.askopenfilename(multiple = False,
			initialdir = os.path.expanduser('~/design'),
			filetypes = (("JSON File", "*.json"),("All Files","*.*")),
			title = "Find a datasheet.")
        if datasheet != '':
            self.set_datasheet(datasheet)

    def cancel_upload(self):
        # Post a cancelation message to CACE.  CACE responds by setting the
        # status to 'canceled'.  The watchprogress procedure is responsible for
        # returning the button to 'Submit' when the characterization finishes
        # or is canceled.
        dspath = os.path.split(self.cur_datasheet)[0]
        datasheet = os.path.split(self.cur_datasheet)[1]
        designname = os.path.splitext(datasheet)[0]
        print('Cancel characterization of ' + designname + ' (' + dspath + ' )')
        subprocess.run([apps_path + '/cace_design_upload.py', '-cancel',
                        dspath])
        self.removeprogress()
        self.bbar.upload_button.configure(text='Submit', state = 'enabled',
			command=self.upload_to_marketplace,
			style = 'normal.TButton')
        # Delete the remote status file.
        dsdir = dspath + '/ngspice/char'
        statusname = dsdir + '/remote_status.json'
        if os.path.exists(statusname):
            os.remove(statusname)

    def progress_bar_setup(self, dspath):
        # Create the progress bar at the bottom of the window to indicate
        # the status of a challenge submission.

        # Disable the Submit button
        self.bbar.upload_button.configure(state='disabled')

        # Start progress bar watchclock
        dsdir = dspath + '/ngspice/char'
        statusname = dsdir + '/remote_status.json'
        if os.path.exists(statusname):
            statbuf = os.stat(statusname)
            mtime = statbuf.st_mtime
        else:
            if os.path.exists(dsdir):
                # Write a simple status
                status = {'message': 'not started', 'total': '0', 'completed': '0'}
                with open(statusname, 'w') as f:
                    json.dump(status, f)
            mtime = 0
        # Create a TTK progress bar widget in the buttonbar.
        self.bbar.progress_label = ttk.Label(self.bbar, text="Characterization: ",
		style = 'normal.TLabel')
        self.bbar.progress_label.grid(column=4, row=0, ipadx = 5)

        self.bbar.progress_message = ttk.Label(self.bbar, text="(not started)",
		style = 'blue.TLabel')
        self.bbar.progress_message.grid(column=5, row=0, ipadx = 5)
        self.bbar.progress = ttk.Progressbar(self.bbar,
			orient='horizontal', mode='determinate')
        self.bbar.progress.grid(column = 6, row = 0, padx = 5, sticky = 'nsew')
        self.bbar.progress_text = ttk.Label(self.bbar, text="0/0",
		style = 'blue.TLabel')
        self.bbar.progress_text.grid(column=7, row=0, ipadx = 5)

        # Start the timer to watch the progress
        self.watchprogress(statusname, mtime, 1)

    def check_ongoing_upload(self):
        # Determine if an upload is ongoing when the characterization tool is
        # started.  If so, immediately go to the 'characterization running'
        # state with progress bar.
        dspath = os.path.split(self.cur_datasheet)[0]
        datasheet = os.path.split(self.cur_datasheet)[1]
        designname = os.path.splitext(datasheet)[0]
        dsdir = dspath + '/ngspice/char'
        statusname = dsdir + '/remote_status.json'
        if os.path.exists(statusname):
            with open(statusname, 'r') as f:
                status = json.load(f)
                if 'message' in status:
                    if status['message'] == 'in progress':
                        print('Design characterization in progress for ' + designname + ' (' + dspath + ' )')
                        self.progress_bar_setup(dspath)
                else:
                    print("No message in status file")

    def upload_to_marketplace(self):
        dspath = os.path.split(self.cur_datasheet)[0]
        datasheet = os.path.split(self.cur_datasheet)[1]
        dsheet = self.datatop['data-sheet']
        designname = dsheet['ip-name']

        # Make sure a netlist has been generated.
        if self.sim_param('check') == False:
            print('No netlist was generated, cannot submit!')
            return

        # For diagnostic purposes, place all of the characterization tool
        # settings into datatop['settings'] when uploading to remote CACE.
        runtime_settings = {}
        runtime_settings['force-regenerate'] = self.settings.get_force()
        runtime_settings['edit-all-params'] = self.settings.get_edit()
        runtime_settings['keep-files'] = self.settings.get_keep()
        runtime_settings['make-plots'] = self.settings.get_plot()
        runtime_settings['submit-test-mode'] = self.settings.get_test()
        runtime_settings['submit-as-schematic'] = self.settings.get_schem()
        runtime_settings['submit-failing'] = self.settings.get_submitfailed()
        runtime_settings['log-output'] = self.settings.get_log()

        # Write out runtime settings as a JSON file
        with open(dspath + '/settings.json', 'w') as file:
            json.dump(runtime_settings, file, indent = 4)

        warning = ''
        must_confirm = False
        if self.settings.get_schem() == True:
            # If a layout exists but "submit as schematic" was chosen, then
            # flag a warning and insist on confirmation.
            if os.path.exists(dspath + '/mag/' + designname + '.mag'):
                warning += 'Warning: layout exists but only schematic has been selected for submission'
                must_confirm = True
            else:
                print('No layout in ' + dspath + '/mag/' + designname + '.mag')
                print('Schematic only submission selection is not needed.')
        else:
            # Likewise, check if schematic netlist results are showing but a layout
            # exists, which means that the existing results are not the ones that are
            # going to be tested.
            if self.origin.get() == 'Schematic Capture':
                if os.path.exists(dspath + '/mag/' + designname + '.mag'):
                    warning += 'Warning: schematic results are shown but remote CACE will be run on layout results.'
                    must_confirm = True


        # Make a check to see if all simulations have been made and passed.  If so,
        # then just do the upload.  If not, then generate a warning dialog and
        # require the user to respond to force an upload in spite of an incomplete
        # simulation.  Give dire warnings if any simulation has failed.

        failures = 0
        missed = 0
        for param in dsheet['electrical-params']:
            if 'max' in param:
                pmax = param['max']
                if not 'value' in pmax:
                    missed += 1
                elif 'score' in pmax:
                    if pmax['score'] == 'fail':
                        failures += 1
            if 'min' in param:
                pmin = param['min']
                if not 'value' in pmin:
                    missed += 1
                elif 'score' in pmin:
                    if pmin['score'] == 'fail':
                        failures += 1

        if missed > 0:
            if must_confirm == True:
                warning += '\n'
            warning += 'Warning:  Not all critical parameters have been simulated.'
        if missed > 0 and failures > 0:
            warning += '\n'
        if failures > 0:
            warning += 'Dire Warning:  This design has errors on critical parameters!'

        # Require confirmation
        if missed > 0 or failures > 0:
            must_confirm = True

        if must_confirm:
            if self.settings.get_submitfailed() == True:
                confirm = ConfirmDialog(self, warning).result
            else:
                confirm = PuntDialog(self, warning).result
            if not confirm == 'okay':
                print('Upload canceled.')
                return
            print('Upload selected')

        # Save hints in file in spice/ directory.
        hintlist = []
        for eparam in dsheet['electrical-params']:
            if not 'editable' in eparam:
                if 'hints' in eparam:
                    hintlist.append(eparam['hints'])
                else:
                    # Must have a placeholder
                    hintlist.append({})
        if hintlist:
            hfilename = dspath + '/hints.json'
            with open(hfilename, 'w') as hfile:
                json.dump(hintlist, hfile, indent = 4)

        print('Uploading design ' + designname + ' (' + dspath + ' )')
        print('to marketplace and submitting for characterization.')
        if not self.settings.get_test():
            self.progress_bar_setup(dspath)
            self.update_idletasks()
        subprocess.run([apps_path + '/cace_design_upload.py', dspath])

        # Remove the settings file
        os.remove(dspath + '/settings.json')
        os.remove(dspath + '/hints.json')

    def removeprogress(self):
        # Remove the progress bar.  This is left up for a second after
        # completion or cancelation so that the final message has time
        # to be seen.
        try:
            self.bbar.progress_label.destroy()
            self.bbar.progress_message.destroy()
            self.bbar.progress.destroy()
            self.bbar.progress_text.destroy()
        except:
            pass

    def watchprogress(self, filename, filemtime, timeout):
        new_timeout = timeout + 1 if timeout > 0 else 0
        # 2 minute timeout for startup (note that all simulation files have to be
        # made during this period.
        if new_timeout == 120:
            self.cancel_upload()
            return

        # If file does not exist, then keep checking at 2 second intervals.
        if not os.path.exists(filename):
            self.after(2000, lambda: self.watchprogress(filename, filemtime, new_timeout))
            return

        # If filename file is modified, then update progress bar;
        # otherwise, restart the clock.
        statbuf = os.stat(filename)
        if statbuf.st_mtime > filemtime:
            self.after(250)	# Otherwise can catch file while it's incomplete. . .
            if self.update_progress(filename) == True:
                self.after(1000, lambda: self.watchprogress(filename, filemtime, 0))
            else:
                # Remove the progress bar when done, after letting the final
                # message display for a second.
                self.after(1500, self.removeprogress)
                # And return the button to "Submit" and in an enabled state.
                self.bbar.upload_button.configure(text='Submit', state = 'enabled',
				command=self.upload_to_marketplace,
				style = 'normal.TButton')
        else:
            self.after(1000, lambda: self.watchprogress(filename, filemtime, new_timeout))

    def update_progress(self, filename):
        # On first update, button changes from "Submit" to "Cancel"
        # This ensures that the 'remote_status.json' file has been sent
        # from the CACE with the hash value needed for the CACE to identify
        # the right simulation and cancel it.
        if self.bbar.upload_button.configure('text')[-1] == 'Submit':
            self.bbar.upload_button.configure(text='Cancel', state = 'enabled',
			command=self.cancel_upload, style = 'red.TButton')

        if not os.path.exists(filename):
            return False

        # Update the progress bar during an CACE simulation run.
        # Read the status file
        try:
            with open(filename, 'r') as f:
                status = json.load(f)
        except (PermissionError, FileNotFoundError):
            # For a very short time the user does not have ownership of
            # the file and the read will fail.  This is a rare case, so
            # just punt until the next cycle.
            return True

        if 'message' in status:
            self.bbar.progress_message.configure(text = status['message'])

        try:
            total = int(status['total'])
        except:
            total = 0
        else:
            self.bbar.progress.configure(maximum = total)
        
        try:
            completed = int(status['completed'])
        except:
            completed = 0
        else:
            self.bbar.progress.configure(value = completed)

        self.bbar.progress_text.configure(text = str(completed) + '/' + str(total))
        if completed > 0 and completed == total:
            print('Notice:  Design completed.')
            print('The CACE server has finished characterizing the design.')
            print('Go to the efabless marketplace to view submission.')
            return False
        elif status['message'] == 'canceled':
            print('Notice:  Design characterization was canceled.')
            return False
        else:
            return True

    def topfilter(self, line):
        # Check output for ubiquitous "Reference value" lines and remove them.
        # This happens before logging both to the file and to the console.
        refrex = re.compile('Reference value')
        rmatch = refrex.match(line)
        if not rmatch:
            return line
        else:
            return None

    def spicefilter(self, line):
        # Check for the alarmist 'tran simulation interrupted' message and remove it.
        # Check for error or warning and print as stderr or stdout accordingly.
        intrex = re.compile('tran simulation interrupted')
        warnrex = re.compile('.*warning', re.IGNORECASE)
        errrex = re.compile('.*error', re.IGNORECASE)

        imatch = intrex.match(line)
        if not imatch:
            ematch = errrex.match(line)
            wmatch = warnrex.match(line)
            if ematch or wmatch:
                print(line, file=sys.stderr)
            else:
                print(line, file=sys.stdout)

    def printwarn(self, output):
        # Check output for warning or error
        if not output:
            return 0

        warnrex = re.compile('.*warning', re.IGNORECASE)
        errrex = re.compile('.*error', re.IGNORECASE)

        errors = 0
        outlines = output.splitlines()
        for line in outlines:
            try:
                wmatch = warnrex.match(line)
            except TypeError:
                line = line.decode('utf-8')
                wmatch = warnrex.match(line)
            ematch = errrex.match(line)
            if ematch:
                errors += 1
            if ematch or wmatch:
                print(line)
        return errors

    def sim_all(self):
        if self.caceproc:
            # Failsafe
            if self.caceproc.poll() != None:
                self.caceproc = None
            else:
                print('Simulation in progress must finish first.')
                return

        # Create netlist if necessary, check for valid result
        if self.sim_param('check') == False:
            return

        # Simulate all of the electrical parameters in turn
        self.sims_to_go = []
        for puniq in self.status:
            self.sims_to_go.append(puniq)

        # Start first sim
        if len(self.sims_to_go) > 0:
            puniq = self.sims_to_go[0]
            self.sims_to_go = self.sims_to_go[1:]
            self.sim_param(puniq)

        # Button now stops the simulations
        self.allsimbutton.configure(style = 'redtitle.TButton', text='Stop Simulations',
		command=self.stop_sims)

    def stop_sims(self):
        # Make sure there will be no more simulations
        self.sims_to_go = []
        if not self.caceproc:
            print("No simulation running.")
            return
        self.caceproc.terminate()
        # Use communicate(), not wait() , on piped processes to avoid deadlock.
        try:
            self.caceproc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            self.caceproc.kill()
            self.caceproc.communicate()
            print("CACE process killed.")
        else:
            print("CACE process exited.")
        # Let watchdog timer see that caceproc is gone and reset the button.

    def edit_param(self, param):
        # Edit the conditions under which the parameter is tested.
        if ('editable' in param and param['editable'] == True) or self.settings.get_edit() == True:
            self.editparam.populate(param)
            self.editparam.open()
        else:
            print('Parameter is not editable')

    def copy_param(self, param):
        # Make a copy of the parameter (for editing)
        newparam = param.copy()
        # Make the copied parameter editable
        newparam['editable'] = True
        # Append this to the electrical parameter list after the item being copied
        if 'display' in param:
            newparam['display'] = param['display'] + ' (copy)'
        datatop = self.datatop
        dsheet = datatop['data-sheet']
        eparams = dsheet['electrical-params']
        eidx = eparams.index(param)
        eparams.insert(eidx + 1, newparam)
        self.create_datasheet_view()

    def delete_param(self, param):
        # Remove an electrical parameter from the datasheet.  This is only
        # allowed if the parameter has been copied from another and so does
        # not belong to the original set of parameters.
        datatop = self.datatop
        dsheet = datatop['data-sheet']
        eparams = dsheet['electrical-params']
        eidx = eparams.index(param)
        eparams.pop(eidx)
        self.create_datasheet_view()

    def add_hints(self, param, simbutton):
        # Raise hints window and configure appropriately for the parameter.
        # Fill in any existing hints.
        self.simhints.populate(param, simbutton)
        self.simhints.open()

    def sim_param(self, method):
        if self.caceproc:
            # Failsafe
            if self.caceproc.poll() != None:
                self.caceproc = None
            else:
                print('Simulation in progress, queued for simulation.')
                if not method in self.sims_to_go:
                    self.sims_to_go.append(method)
                return False

        # Get basic values for datasheet and ip-name

        dspath = os.path.split(self.cur_datasheet)[0]
        dsheet = self.datatop['data-sheet']
        dname = dsheet['ip-name']

        # Open log file, if specified
        self.logstart()

        # Check for whether the netlist is specified to come from schematic
        # or layout.  Add a record to the datasheet depending on whether
        # the netlist is from layout or extracted.  The settings window has
        # a checkbox to force submitting as a schematic even if layout exists.

        if self.origin.get() == 'Schematic Capture':
            dsheet['netlist-source'] = 'schematic'
        else:
            dsheet['netlist-source'] = 'layout'

        if self.settings.get_force() == True:
            dsheet['regenerate'] = 'force'

        basemethod = method.split('.')[0]
        if basemethod == 'check':	# used by submit to ensure netlist exists
            return True
  
        if basemethod == 'physical':
            print('Checking ' + method.split('.')[1])
        else:
            print('Simulating method = ' + basemethod)
        self.stat_label = self.status[method]
        self.stat_label.configure(text='(in progress)', style='blue.TLabel')
        # Update status now
        self.update_idletasks()

        if dspath == '':
            dspath = '.'

        print('Datasheet directory is = ' + dspath + '\n')

        # Instead of using the original datasheet, use the one in memory so that
        # it accumulates results.  A "save" button will update the original.
        if not os.path.isdir(dspath + '/ngspice'):
            os.makedirs(dspath + '/ngspice')
        dsdir = dspath + '/ngspice'
        if not os.path.isdir(dsdir):
            os.makedirs(dsdir)
        with open(dsdir + '/datasheet.json', 'w') as file:
            json.dump(self.datatop, file, indent = 4)
        # As soon as we call CACE, we will be watching the status of file
        # datasheet_anno.  So create it if it does not exist, else attempting
        # to stat a nonexistant file will cause the 1st simulation to fail.
        if not os.path.exists(dsdir + '/datasheet_anno.json'):
            open(dsdir + '/datasheet_anno.json', 'a').close()
        # Call cace_gensim with full set of options
        # First argument is the root directory
        # (Diagnostic)
        design_path = dspath + '/spice'

        print('Calling cace_gensim.py ' + dspath + 
			' -local -method=' + method)

        modetext = ['-local']
        if self.settings.get_keep() == True:
            print(' -keep ')
            modetext.append('-keep')

        if self.settings.get_plot() == True:
            print(' -plot ')
            modetext.append('-plot')

        print(' -simdir=' + dsdir + ' -datasheetdir=' + dsdir + ' -designdir=' + design_path)
        print(' -layoutdir=' + dspath + '/mag' + ' -testbenchdir=' + dspath + '/testbench')
        print(' -datasheet=datasheet.json')
        
        self.caceproc = subprocess.Popen([apps_path + '/cace_gensim.py', dspath,
			*modetext,
			'-method=' + method,  # Call local mode w/method
			'-simdir=' + dsdir,
			'-datasheetdir=' + dsdir,
			'-designdir=' + design_path,
			'-layoutdir=' + dspath + '/mag',
			'-testbenchdir=' + dspath + '/testbench',
			'-datasheet=datasheet.json'],
          		stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        # Simulation finishes on its own time.  Use watchdog to handle.
        # Note that python "watchdog" is threaded, and tkinter is not thread-safe.
        # So watchdog is done with a simple timer loop.
        statbuf = os.stat(dsdir + '/datasheet.json')
        checktime = statbuf.st_mtime

        filename = dsdir + '/datasheet_anno.json'
        statbuf = os.stat(filename)
        self.watchclock(filename, statbuf.st_mtime, checktime)

    def watchclock(self, filename, filemtime, checktime):
        # In case simulations cleared while watchclock was pending
        if self.caceproc == None:
            return
        # Poll cace_gensim to see if it finished
        cace_status = self.caceproc.poll()
        if cace_status != None:
            try:
                output = self.caceproc.communicate(timeout=1)
            except ValueError:
                print("CACE gensim forced stop, status " + str(cace_status))
            else: 
                outlines = output[0]
                errlines = output[1]
                for line in outlines.splitlines():
                    print(line.decode('utf-8'))
                for line in errlines.splitlines():
                    print(line.decode('utf-8'))
                print("CACE gensim exited with status " + str(cace_status))
        else:
            n = 0
            while True:
                self.update_idletasks()
                # Attempt to avoid infinite loop, unsure of the cause.
                n += 1
                if n > 100:
                    n = 0
                    cace_status = self.caceproc.poll()
                    if cace_status != None:
                        break
                    self.logprint("100 lines of output", doflush=True)
                    # Something went wrong.  Kill the process.
                    # self.stop_sims()
                sresult = select.select([self.caceproc.stdout, self.caceproc.stderr], [], [], 0)[0]
                if self.caceproc.stdout in sresult:
                    outstring = self.caceproc.stdout.readline().decode().strip()
                    self.logprint(outstring, doflush=True)
                    print(outstring)
                elif self.caceproc.stderr in sresult:
                    # ngspice passes back simulation time on stderr.  This ends in \r but no
                    # newline.  '\r' ends the transmission, so return.
                    # errstring = self.topfilter(self.caceproc.stderr.readline().decode().strip())
                    # if errstring:
                    #     self.logprint(errstring, doflush=True)
                    #     # Recast everything that isn't an error back into stdout.
                    #     self.spicefilter(errstring)
                    ochar = str(self.caceproc.stderr.read(1).decode())
                    if ochar == '\r':
                        print('')
                        break
                    else:
                        print(ochar, end='')
                else:
                    break

        # If filename file is modified, then call annotate;  otherwise, restart the clock.
        statbuf = os.stat(filename)
        if (statbuf.st_mtime > filemtime) or (cace_status != None):
            if cace_status != None:
                self.caceproc = None
            else:
                # Re-run to catch last output.
                self.after(500, lambda: self.watchclock(filename, statbuf.st_mtime, checktime))
                return
            if cace_status != 0:
                print('Errors encountered in simulation.')
                self.logprint('Errors in simulation, CACE status = ' + str(cace_status), doflush=True)
            self.annotate('anno', checktime)
            if len(self.sims_to_go) > 0:
                puniq = self.sims_to_go[0]
                self.sims_to_go = self.sims_to_go[1:]
                self.sim_param(puniq)
            else:
                # Button goes back to original text and command
                self.allsimbutton.configure(style = 'bluetitle.TButton',
				text='Simulate All', command = self.sim_all)
        elif not self.caceproc:
            # Process terminated by "stop"
            # Button goes back to original text and command
            self.allsimbutton.configure(style = 'bluetitle.TButton',
			text='Simulate All', command = self.sim_all)
            # Just redraw everthing so that the "(in progress)" message goes away.
            self.annotate('anno', checktime)
        else:
            self.after(500, lambda: self.watchclock(filename, filemtime, checktime))

    def clear_results(self, dsheet):
        # Remove results from the window by clearing parameter results
        paramstodo = []
        if 'electrical-params' in dsheet:
            paramstodo.extend(dsheet['electrical-params'])
        if 'physical-params' in dsheet:
            paramstodo.extend(dsheet['physical-params'])

        for param in paramstodo:
            # Fill frame with electrical parameter information
            if 'max' in param:
                maxrec = param['max']
                if 'value' in maxrec:
                    maxrec.pop('value')
                if 'score' in maxrec:
                    maxrec.pop('score')
            if 'typ' in param:
                typrec = param['typ']
                if 'value' in typrec:
                    typrec.pop('value')
                if 'score' in typrec:
                    typrec.pop('score')
            if 'min' in param:
                minrec = param['min']
                if 'value' in minrec:
                    minrec.pop('value')
                if 'score' in minrec:
                    minrec.pop('score')
            if 'results' in param:
                param.pop('results')

            if 'plot' in param:
                plotrec = param['plot']
                if 'status' in plotrec:
                    plotrec.pop('status')

        # Regenerate datasheet view
        self.create_datasheet_view()

    def annotate(self, suffix, checktime):
        # Pull results back from datasheet_anno.json.  Do NOT load this
        # file if it predates the unannotated datasheet (that indicates
        # simulator failure, and no results).
        dspath = os.path.split(self.cur_datasheet)[0]
        if dspath == '':
            dspath = '.'
        dsdir = dspath + '/ngspice'
        anno = dsdir + '/datasheet_' + suffix + '.json'
        unanno = dsdir + '/datasheet.json'

        if os.path.exists(anno):
            statbuf = os.stat(anno)
            mtimea = statbuf.st_mtime
            if checktime >= mtimea:
                # print('original = ' + str(checktime) + ' annotated = ' + str(mtimea))
                print('Error in simulation, no update to results.', file=sys.stderr)
            elif statbuf.st_size == 0:
                print('Error in simulation, no results.', file=sys.stderr)
            else:
                with open(anno, 'r') as file:
                    self.datatop = json.load(file)
        else:
            print('Error in simulation, no update to results.', file=sys.stderr)

        # Regenerate datasheet view
        self.create_datasheet_view()

        # Close log file, if it was enabled in the settings
        self.logstop()

    def save_results(self):
        # Write datasheet_save with all the locally processed results.
        dspath = os.path.split(self.cur_datasheet)[0]
        dsdir = dspath + '/ngspice'

        if self.origin.get() == 'Layout Extracted':
            jsonfile = dsdir + '/datasheet_lsave.json'
        else:
            jsonfile = dsdir + '/datasheet_save.json'

        with open(jsonfile, 'w') as ofile:
            json.dump(self.datatop, ofile, indent = 4)
        self.last_save = os.path.getmtime(jsonfile)

        # Create copy of datasheet without result data.  This is
        # the file appropriate to insert into the IP catalog
        # metadata JSON file.

        datacopy = copy.copy(self.datatop)
        dsheet = datacopy['data-sheet']
        if 'electrical-params' in dsheet:
            for eparam in dsheet['electrical-params']:
                if 'results' in eparam:
                    eparam.pop('results')

        datacopy.pop('request-hash')
        jsonfile = dsdir + '/datasheet_compact.json'
        with open(jsonfile, 'w') as ofile:
            json.dump(datacopy, ofile, indent = 4)

        print('Characterization results saved.')

    def check_saved(self):
        # Check if there is a file 'datasheet_save' and if it is more
        # recent than 'datasheet_anno'.  If so, return True, else False.

        [dspath, dsname] = os.path.split(self.cur_datasheet)
        dsdir = dspath + '/ngspice'

        if self.origin.get() == 'Layout Extracted':
            savefile = dsdir + '/datasheet_lsave.json'
        else:
            savefile = dsdir + '/datasheet_save.json'

        annofile = dsdir + '/datasheet_anno.json'
        if os.path.exists(annofile):
            annotime = os.path.getmtime(annofile)

            # If nothing has been updated since the characterization
            # tool was started, then there is no new information to save.
            if annotime < self.starttime:
                return True

            if os.path.exists(savefile):
                savetime = os.path.getmtime(savefile)
                # return True if (savetime > annotime) else False
                if savetime > annotime:
                    print("Save is more recent than sim, so no need to save.")
                    return True
                else:
                    print("Sim is more recent than save, so need to save.")
                    return False
            else:
                # There is a datasheet_anno file but no datasheet_save,
	        # so there are necessarily unsaved results.
                print("no datasheet_save, so any results have not been saved.")
                return False
        else:
            # There is no datasheet_anno file, so datasheet_save
            # is either current or there have been no simulations.
            print("no datasheet_anno, so there are no results to save.")
            return True

    def callback(self):
        # Check for manual load/save-as status from settings window (callback
        # when the settings window is closed).
        if self.settings.get_loadsave() == True:
            self.bbar.saveas_button.grid(column=2, row=0, padx = 5)
            self.bbar.load_button.grid(column=3, row=0, padx = 5)
        else:
            self.bbar.saveas_button.grid_forget()
            self.bbar.load_button.grid_forget()

    def save_manual(self, value={}):
        dspath = self.cur_datasheet
        # Set initialdir to the project where cur_datasheet is located
        dsparent = os.path.split(dspath)[0]

        datasheet = filedialog.asksaveasfilename(multiple = False,
			initialdir = dsparent,
			confirmoverwrite = True,
			defaultextension = ".json",
			filetypes = (("JSON File", "*.json"),("All Files","*.*")),
			title = "Select filename for saved datasheet.")
        with open(datasheet, 'w') as ofile:
            json.dump(self.datatop, ofile, indent = 4)

    def load_manual(self, value={}):
        dspath = self.cur_datasheet
        # Set initialdir to the project where cur_datasheet is located
        dsparent = os.path.split(dspath)[0]

        datasheet = filedialog.askopenfilename(multiple = False,
			initialdir = dsparent,
			filetypes = (("JSON File", "*.json"),("All Files","*.*")),
			title = "Find a datasheet.")
        if datasheet != '':
            try:
                with open(datasheet, 'r') as file:
                    self.datatop = json.load(file)
            except:
                print('Error in file, no update to results.', file=sys.stderr)

            else:
                # Regenerate datasheet view
                self.create_datasheet_view()

    def load_results(self, value={}):
        # Check if datasheet_save exists and is more recent than the
        # latest design netlist.  If so, load it;  otherwise, not.
        # NOTE:  Name of .spice file comes from the project 'ip-name'
        # in the datasheet.

        [dspath, dsname] = os.path.split(self.cur_datasheet)
        try:
            dsheet = self.datatop['data-sheet']
        except KeyError:
            return

        if dspath == '':
            dspath = '.'

        dsroot = dsheet['ip-name']

        # Remove any existing results from the datasheet records
        self.clear_results(dsheet)

        # Also must be more recent than datasheet
        jtime = os.path.getmtime(self.cur_datasheet)

        # dsroot = os.path.splitext(dsname)[0]

        dsdir = dspath + '/spice'

        if not os.path.exists(dsdir):
            print('Error:  Cannot find directory spice/ in path ' + dspath)

        if self.origin.get() == 'Layout Extracted':
            spifile = dsdir + '/pex/' + dsroot + '.spice'
            savesuffix = 'lsave'
        else:
            spifile = dsdir + '/' + dsroot + '.spice'
            savesuffix = 'save'

        dsdir = dspath + '/ngspice'
        savefile = dsdir + '/datasheet_' + savesuffix + '.json'

        if os.path.exists(savefile):
            savetime = os.path.getmtime(savefile)

        if os.path.exists(spifile):
            spitime = os.path.getmtime(spifile)

            if os.path.exists(savefile):
                if (savetime > spitime and savetime > jtime):
                    self.annotate(savesuffix, 0)
                    print('Characterization results loaded.')
                    # print('(' + savefile + ' timestamp = ' + str(savetime) + '; ' + self.cur_datasheet + ' timestamp = ' + str(jtime))
                else:
                    print('Saved datasheet is out-of-date, not loading')
            else:
                print('Datasheet file ' + savefile)
                print('No saved datasheet file, nothing to pre-load')
        else:
            print('No netlist file ' + spifile + '!')

        # Remove outdated datasheet.json and datasheet_anno.json to prevent
        # them from overwriting characterization document entries

        if os.path.exists(savefile):
            if savetime < jtime:
                print('Removing outdated save file ' + savefile)
                os.remove(savefile)

        savefile = dsdir + '/datasheet_anno.json'
        if os.path.exists(savefile):
            savetime = os.path.getmtime(savefile)
            if savetime < jtime:
                print('Removing outdated results file ' + savefile)
                os.remove(savefile)

        savefile = dsdir + '/datasheet.json'
        if os.path.exists(savefile):
            savetime = os.path.getmtime(savefile)
            if savetime < jtime:
                print('Removing outdated results file ' + savefile)
                os.remove(savefile)

    def create_datasheet_view(self):
        dframe = self.datasheet_viewer.dframe
 
        # Destroy the existing datasheet frame contents (if any)
        for widget in dframe.winfo_children():
            widget.destroy()
        self.status = {}	# Clear dictionary

        dsheet = self.datatop['data-sheet']
        if 'global-conditions' in dsheet:
            globcond = dsheet['global-conditions']
        else:
            globcond = []

        # Add basic information at the top

        n = 0
        dframe.cframe = ttk.Frame(dframe)
        dframe.cframe.grid(column = 0, row = n, sticky='ewns', columnspan = 10)

        dframe.cframe.plabel = ttk.Label(dframe.cframe, text = 'Project IP name:',
			style = 'italic.TLabel')
        dframe.cframe.plabel.grid(column = 0, row = n, sticky='ewns', ipadx = 5)
        dframe.cframe.pname = ttk.Label(dframe.cframe, text = dsheet['ip-name'],
			style = 'normal.TLabel')
        dframe.cframe.pname.grid(column = 1, row = n, sticky='ewns', ipadx = 5)
        dframe.cframe.fname = ttk.Label(dframe.cframe, text = dsheet['foundry'],
			style = 'normal.TLabel')
        dframe.cframe.fname.grid(column = 2, row = n, sticky='ewns', ipadx = 5)
        dframe.cframe.fname = ttk.Label(dframe.cframe, text = dsheet['node'],
			style = 'normal.TLabel')
        dframe.cframe.fname.grid(column = 3, row = n, sticky='ewns', ipadx = 5)
        if 'decription' in dsheet:
            dframe.cframe.pdesc = ttk.Label(dframe.cframe, text = dsheet['description'],
			style = 'normal.TLabel')
            dframe.cframe.pdesc.grid(column = 4, row = n, sticky='ewns', ipadx = 5)

        if 'UID' in self.datatop:
            n += 1
            dframe.cframe.ulabel = ttk.Label(dframe.cframe, text = 'UID:',
			style = 'italic.TLabel')
            dframe.cframe.ulabel.grid(column = 0, row = n, sticky='ewns', ipadx = 5)
            dframe.cframe.uname = ttk.Label(dframe.cframe, text = self.datatop['UID'],
			style = 'normal.TLabel')
            dframe.cframe.uname.grid(column = 1, row = n, columnspan = 5, sticky='ewns', ipadx = 5)

        n = 1
        ttk.Separator(dframe, orient='horizontal').grid(column=0, row=n, sticky='ewns', columnspan=10)

        # Title block
        n += 1
        dframe.desc_title = ttk.Label(dframe, text = 'Parameter', style = 'title.TLabel')
        dframe.desc_title.grid(column = 0, row = n, sticky='ewns')
        dframe.method_title = ttk.Label(dframe, text = 'Method', style = 'title.TLabel')
        dframe.method_title.grid(column = 1, row = n, sticky='ewns')
        dframe.min_title = ttk.Label(dframe, text = 'Min', style = 'title.TLabel')
        dframe.min_title.grid(column = 2, row = n, sticky='ewns', columnspan = 2)
        dframe.typ_title = ttk.Label(dframe, text = 'Typ', style = 'title.TLabel')
        dframe.typ_title.grid(column = 4, row = n, sticky='ewns', columnspan = 2)
        dframe.max_title = ttk.Label(dframe, text = 'Max', style = 'title.TLabel')
        dframe.max_title.grid(column = 6, row = n, sticky='ewns', columnspan = 2)
        dframe.stat_title = ttk.Label(dframe, text = 'Status', style = 'title.TLabel')
        dframe.stat_title.grid(column = 8, row = n, sticky='ewns')

        if not self.sims_to_go:
            self.allsimbutton = ttk.Button(dframe, text='Simulate All',
			style = 'bluetitle.TButton', command = self.sim_all)
        else:
            self.allsimbutton = ttk.Button(dframe, text='Stop Simulations',
			style = 'redtitle.TButton', command = self.stop_sims)
        self.allsimbutton.grid(column = 9, row=n, sticky='ewns')

        tooltip.ToolTip(self.allsimbutton, text = "Simulate all electrical parameters")

        # Make all columns equally expandable
        for i in range(10):
            dframe.columnconfigure(i, weight = 1)

        # Parse the file for electrical parameters
        n += 1
        binrex = re.compile(r'([0-9]*)\'([bodh])', re.IGNORECASE)
        paramstodo = []
        if 'electrical-params' in dsheet:
            paramstodo.extend(dsheet['electrical-params'])
        if 'physical-params' in dsheet:
            paramstodo.extend(dsheet['physical-params'])

        if self.origin.get() == 'Schematic Capture':
            isschem = True
        else:
            isschem = False

        for param in paramstodo:
            # Fill frame with electrical parameter information
            if 'method' in param:
                p = param['method']
                puniq = p + '.0'
                if puniq in self.status:
                    # This method was used before, so give it a unique identifier
                    j = 1
                    while True:
                        puniq = p + '.' + str(j)
                        if puniq not in self.status:
                            break
                        else:
                            j += 1
                else:
                    j = 0
                paramtype = 'electrical'
            else:
                paramtype = 'physical'
                p = param['condition']
                puniq = paramtype + '.' + p
                j = 0

            if 'editable' in param and param['editable'] == True:
                normlabel   = 'hlight.TLabel'
                redlabel    = 'rhlight.TLabel'
                greenlabel  = 'ghlight.TLabel'
                normbutton  = 'hlight.TButton'
                redbutton   = 'rhlight.TButton'
                greenbutton = 'ghlight.TButton'
            else:
                normlabel   = 'normal.TLabel'
                redlabel    = 'red.TLabel'
                greenlabel  = 'green.TLabel'
                normbutton  = 'normal.TButton'
                redbutton   = 'red.TButton'
                greenbutton = 'green.TButton'

            if 'display' in param:
                dtext = param['display']
            else:
                dtext = p

            # Special handling:  Change LVS_errors to "device check" when using
            # schematic netlist.
            if paramtype == 'physical':
                if isschem:
                    if p == 'LVS_errors':
                        dtext = 'Invalid device check'

            dframe.description = ttk.Label(dframe, text = dtext, style = normlabel)

            dframe.description.grid(column = 0, row=n, sticky='ewns')
            dframe.method = ttk.Label(dframe, text = p, style = normlabel)
            dframe.method.grid(column = 1, row=n, sticky='ewns')
            if 'plot' in param:
                status_style = normlabel
                dframe.plots = ttk.Frame(dframe)
                dframe.plots.grid(column = 2, row=n, columnspan = 6, sticky='ewns')
                plotrec = param['plot']
                if 'status' in plotrec:
                    status_value = plotrec['status']
                else:
                    status_value = '(not checked)'
                dframe_plot = ttk.Label(dframe.plots, text=plotrec['filename'],
				style = normlabel)
                dframe_plot.grid(column = j, row = n, sticky='ewns')
            else:
                # For schematic capture, mark physical parameters that can't and won't be
                # checked as "not applicable".
                status_value = '(not checked)'
                if paramtype == 'physical':
                    if isschem:
                       if p == 'area' or p == 'width' or p == 'height' or p == 'DRC_errors':
                           status_value = '(N/A)'

                if 'min' in param:
                    status_style = normlabel
                    pmin = param['min']
                    if 'target' in pmin:
                        if 'unit' in param and not binrex.match(param['unit']):
                            targettext = pmin['target'] + ' ' + param['unit']
                        else:
                            targettext = pmin['target']
                        # Hack for use of min to change method of scoring
                        if not 'penalty' in pmin or pmin['penalty'] != '0':
                            dframe.min = ttk.Label(dframe, text=targettext, style = normlabel)
                        else:
                            dframe.min = ttk.Label(dframe, text='(no limit)', style = normlabel)
                    else:
                        dframe.min = ttk.Label(dframe, text='(no limit)', style = normlabel)
                    if 'score' in pmin:
                        if pmin['score'] != 'fail':
                            status_style = greenlabel
                            if status_value != 'fail':
                                status_value = 'pass'
                        else:
                            status_style = redlabel
                            status_value = 'fail'
                    if 'value' in pmin:
                        if 'unit' in param and not binrex.match(param['unit']):
                            valuetext = pmin['value'] + ' ' + param['unit']
                        else:
                            valuetext = pmin['value']
                        dframe.value = ttk.Label(dframe, text=valuetext, style=status_style)
                        dframe.value.grid(column = 3, row=n, sticky='ewns')
                else:
                    dframe.min = ttk.Label(dframe, text='(no limit)', style = normlabel)
                dframe.min.grid(column = 2, row=n, sticky='ewns')
                if 'typ' in param:
                    status_style = normlabel
                    ptyp = param['typ']
                    if 'target' in ptyp:
                        if 'unit' in param and not binrex.match(param['unit']):
                            targettext = ptyp['target'] + ' ' + param['unit']
                        else:
                            targettext = ptyp['target']
                        dframe.typ = ttk.Label(dframe, text=targettext, style = normlabel)
                    else:
                        dframe.typ = ttk.Label(dframe, text='(no target)', style = normlabel)
                    if 'score' in ptyp:
                        # Note:  You can't fail a "typ" score, but there is only one "Status",
                        # so if it is a "fail", it must remain a "fail".
                        if ptyp['score'] != 'fail':
                            status_style = greenlabel
                            if status_value != 'fail':
                                status_value = 'pass'
                        else:
                            status_style = redlabel
                            status_value = 'fail'
                    if 'value' in ptyp:
                        if 'unit' in param and not binrex.match(param['unit']):
                            valuetext = ptyp['value'] + ' ' + param['unit']
                        else:
                            valuetext = ptyp['value']
                        dframe.value = ttk.Label(dframe, text=valuetext, style=status_style)
                        dframe.value.grid(column = 5, row=n, sticky='ewns')
                else:
                    dframe.typ = ttk.Label(dframe, text='(no target)', style = normlabel)
                dframe.typ.grid(column = 4, row=n, sticky='ewns')
                if 'max' in param:
                    status_style = normlabel
                    pmax = param['max']
                    if 'target' in pmax:
                        if 'unit' in param and not binrex.match(param['unit']):
                            targettext = pmax['target'] + ' ' + param['unit']
                        else:
                            targettext = pmax['target']
                        # Hack for use of max to change method of scoring
                        if not 'penalty' in pmax or pmax['penalty'] != '0':
                            dframe.max = ttk.Label(dframe, text=targettext, style = normlabel)
                        else:
                            dframe.max = ttk.Label(dframe, text='(no limit)', style = normlabel)
                    else:
                        dframe.max = ttk.Label(dframe, text='(no limit)', style = normlabel)
                    if 'score' in pmax:
                        if pmax['score'] != 'fail':
                            status_style = greenlabel
                            if status_value != 'fail':
                                status_value = 'pass'
                        else:
                            status_style = redlabel
                            status_value = 'fail'
                    if 'value' in pmax:
                        if 'unit' in param and not binrex.match(param['unit']):
                            valuetext = pmax['value'] + ' ' + param['unit']
                        else:
                            valuetext = pmax['value']
                        dframe.value = ttk.Label(dframe, text=valuetext, style=status_style)
                        dframe.value.grid(column = 7, row=n, sticky='ewns')
                else:
                    dframe.max = ttk.Label(dframe, text='(no limit)', style = normlabel)
                dframe.max.grid(column = 6, row=n, sticky='ewns')

            if paramtype == 'electrical':
                if 'hints' in param:
                    simtext = '\u2022Simulate'
                else:
                    simtext = 'Simulate'
            else:
                simtext = 'Check'

            simbutton = ttk.Menubutton(dframe, text=simtext, style = normbutton)

            # Generate pull-down menu on Simulate button.  Most items apply
            # only to electrical parameters (at least for now)
            simmenu = tkinter.Menu(simbutton)
            simmenu.add_command(label='Run',
			command = lambda puniq=puniq: self.sim_param(puniq))
            simmenu.add_command(label='Stop', command = self.stop_sims)
            if paramtype == 'electrical':
                simmenu.add_command(label='Hints',
			command = lambda param=param, simbutton=simbutton: self.add_hints(param, simbutton))
                simmenu.add_command(label='Edit',
			command = lambda param=param: self.edit_param(param))
                simmenu.add_command(label='Copy',
			command = lambda param=param: self.copy_param(param))
                if 'editable' in param and param['editable'] == True:
                    simmenu.add_command(label='Delete',
				command = lambda param=param: self.delete_param(param))

            # Attach the menu to the button
            simbutton.config(menu=simmenu)

            # simbutton = ttk.Button(dframe, text=simtext, style = normbutton)
            #		command = lambda puniq=puniq: self.sim_param(puniq))

            simbutton.grid(column = 9, row=n, sticky='ewns')

            if paramtype == 'electrical':
                tooltip.ToolTip(simbutton, text = "Simulate one electrical parameter")
            else:
                tooltip.ToolTip(simbutton, text = "Check one physical parameter")

            # If 'pass', then just display message.  If 'fail', then create a button that
            # opens and configures the failure report window.
            if status_value == '(not checked)':
                bstyle=normbutton
                stat_label = ttk.Label(dframe, text=status_value, style=bstyle)
            else:
                if status_value == 'fail':
                    bstyle=redbutton
                else:
                    bstyle=greenbutton
                if paramtype == 'electrical':
                    stat_label = ttk.Button(dframe, text=status_value, style=bstyle,
				command = lambda param=param, globcond=globcond:
				self.failreport.display(param, globcond,
				self.cur_datasheet))
                elif p == 'LVS_errors':
                    dspath = os.path.split(self.cur_datasheet)[0]
                    datasheet = os.path.split(self.cur_datasheet)[1]
                    dsheet = self.datatop['data-sheet']
                    designname = dsheet['ip-name']
                    if self.origin.get() == 'Schematic Capture':
                        lvs_file = dspath + '/mag/precheck.log'
                    else:
                        lvs_file = dspath + '/mag/comp.out'
                    if not os.path.exists(lvs_file):
                        if os.path.exists(dspath + '/mag/precheck.log'):
                            lvs_file = dspath + '/mag/precheck.log'
                        elif os.path.exists(dspath + '/mag/comp.out'):
                            lvs_file = dspath + '/mag/comp.out'

                    stat_label = ttk.Button(dframe, text=status_value, style=bstyle,
				command = lambda lvs_file=lvs_file: self.textreport.display(lvs_file))
                else:
                    stat_label = ttk.Label(dframe, text=status_value, style=bstyle)
                tooltip.ToolTip(stat_label,
			text = "Show detail view of simulation conditions and results")
            stat_label.grid(column = 8, row=n, sticky='ewns')
            self.status[puniq] = stat_label
            n += 1

        for child in dframe.winfo_children():
            child.grid_configure(ipadx = 5, ipady = 1, padx = 2, pady = 2)

        # Check if a design submission and characterization may be in progress.
        # If so, add the progress bar at the bottom.
        self.check_ongoing_upload()

if __name__ == '__main__':
    faulthandler.register(signal.SIGUSR2)
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    root = tkinter.Tk()
    app = CACECharacterize(root)
    if arguments:
        print('Calling set_datasheet with argument ' + arguments[0])
        app.set_datasheet(arguments[0])

    root.mainloop()
