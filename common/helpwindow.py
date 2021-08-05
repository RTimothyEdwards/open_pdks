#!/usr/bin/env python3
#
#--------------------------------------------------------
# Help Window for the Project manager
#
#--------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# September 12, 2016
# Version 0.1
#--------------------------------------------------------

import re
import tkinter
from tkinter import ttk

class HelpWindow(tkinter.Toplevel):
    """help window"""

    def __init__(self, parent=None, fontsize = 11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)

        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.withdraw()
        self.title('Help')

        self.helptitle = ttk.Label(self, style='title.TLabel', text = '(no text)')
        self.helptitle.grid(column = 0, row = 0, sticky = "news")
        self.helpbar = ttk.Separator(self, orient='horizontal')
        self.helpbar.grid(column = 0, row = 1, sticky = "news")

        self.hframe = tkinter.Frame(self)
        self.hframe.grid(column = 0, row = 2, sticky = "news")
        self.hframe.helpdisplay = ttk.Frame(self.hframe)
        self.hframe.helpdisplay.pack(side = 'left', fill = 'both', expand = 'true')

        self.hframe.helpdisplay.helptext = tkinter.Text(self.hframe.helpdisplay, wrap='word')
        self.hframe.helpdisplay.helptext.pack(side = 'top', fill = 'both', expand = 'true')
        # Add scrollbar to help window
        self.hframe.scrollbar = ttk.Scrollbar(self.hframe)
        self.hframe.scrollbar.pack(side='right', fill='y')
        # attach help window to scrollbar
        self.hframe.helpdisplay.helptext.config(yscrollcommand = self.hframe.scrollbar.set)
        self.hframe.scrollbar.config(command = self.hframe.helpdisplay.helptext.yview)

        self.hframe.toc = ttk.Treeview(self.hframe, selectmode='browse')
        self.hframe.toc.bind('<<TreeviewSelect>>', self.toc_to_page)
        self.hframe.toc.bind('<<TreeviewOpen>>', self.toc_toggle)
        self.hframe.toc.bind('<<TreeviewClose>>', self.toc_toggle)
        self.hframe.toc.tag_configure('title', font=('Helvetica', fontsize, 'bold italic'),
                        foreground = 'brown', anchor = 'center')
        self.hframe.toc.heading('#0', text = "Table of Contents")

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 3, sticky = "news")
        self.bbar.close_button = ttk.Button(self.bbar, text='Close',
		command=self.close, style = 'normal.TButton')
        self.bbar.close_button.grid(column=0, row=0, padx = 5)

        self.bbar.prev_button = ttk.Button(self.bbar, text='Prev',
		command=self.prevpage, style = 'normal.TButton')
        self.bbar.prev_button.grid(column=1, row=0, padx = 5)

        self.bbar.next_button = ttk.Button(self.bbar, text='Next',
		command=self.nextpage, style = 'normal.TButton')
        self.bbar.next_button.grid(column=2, row=0, padx = 5)

        self.bbar.contents_button = ttk.Button(self.bbar, text='Table of Contents',
		command=self.page_to_toc, style = 'normal.TButton')
        self.bbar.contents_button.grid(column=3, row=0, padx = 5)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
        self.columnconfigure(0, weight=1)

        # Help pages
        self.pages = []
        self.pageno = -1		# No page
        self.toggle = False

    def grid_configure(self, padx, pady):
        pass

    def redisplay(self):
        # remove contents
        if self.pageno >= 0 and self.pageno < len(self.pages):
            self.hframe.helpdisplay.helptext.delete('1.0', 'end')
            self.hframe.helpdisplay.helptext.insert('end', self.pages[self.pageno]['text'])
            self.helptitle.configure(text = self.pages[self.pageno]['title'])

    def toc_toggle(self, event):
        self.toggle = True

    def toc_to_page(self, event):
        treeview = event.widget
        selection = treeview.item(treeview.selection())

        # Make sure any open/close callback is handled first!
        self.update_idletasks()
        if self.toggle:
            # Item was opened or closed, so consider this a 'false select' and
            # do not go to the page.
            self.toggle = False
            return

        if 'values' in selection:
            pagenum = selection['values'][0]
        else:
            print('Unknown page selected.')
            pagenum = 0

        # Display a page after displaying the table of contents
        self.hframe.toc.pack_forget()
        self.hframe.scrollbar.pack_forget()
        self.hframe.helpdisplay.pack(side='left', fill='both', expand = 'true')
        self.hframe.scrollbar.pack(side='right', fill='y')
        self.hframe.scrollbar.config(command = self.hframe.helpdisplay.helptext.yview)
        # Enable Prev and Next buttons
        self.bbar.prev_button.configure(state='enabled')
        self.bbar.next_button.configure(state='enabled')
        # Redisplay
        self.page(pagenum)

    def page_to_toc(self):
        # Display the table of contents after displaying a page
        self.hframe.scrollbar.pack_forget()
        self.hframe.helpdisplay.pack_forget()
        self.hframe.toc.pack(side='left', fill='both', expand = 'true')
        self.hframe.scrollbar.pack(side='right', fill='y')
        self.hframe.scrollbar.config(command = self.hframe.toc.yview)
        # Disable Prev and Next buttons
        self.bbar.prev_button.configure(state='disabled')
        self.bbar.next_button.configure(state='disabled')

    # Simple add page with a single block of plain text
    def add_page(self, toc_text, text_block):
        newdict = {}
        newdict['text'] = text_block
        newdict['title'] = toc_text
        self.pages.append(newdict)
        newpageno = len(self.pages)
        self.hframe.toc.insert('', 'end', text=str(newpageno) + '.  ' + toc_text,
		tag='title', value = newpageno - 1)
        if self.pageno < 0:
            self.pageno = 0	# First page

    # Fill the help text from a file.  The format of the file is:
    # <page_num>
    # <title>
    # <text>
    # '.'
    # Text is multi-line and ends when '.' is encountered by itself

    def add_pages_from_file(self, filename):
        endpagerex = re.compile('^\.$')
        newpagerex = re.compile('^[0-9\.]+$')
        commentrex = re.compile('^[\-]+$')
        hierarchy = ''
        print('Loading help text from file ' + filename)
        with open(filename, 'r') as f:
            toc_text = []
            page_text = []
            for line in f:
                if newpagerex.match(line) or endpagerex.match(line):
                    if toc_text and page_text:
                        newdict = {}
                        self.pages.append(newdict)
                        newpageno = len(self.pages)
                        if '.' in hierarchy:
                            pageinfo = hierarchy.rsplit('.', 1)
                            if pageinfo[1] == '':
                                parentid = ''
                                pageid = pageinfo[0]
                            else:
                                parentid = pageinfo[0]
                                pageid = pageinfo[1]
                        else:
                            parentid = ''
                            pageid = hierarchy
                        if parentid:
                            pageid = parentid + '.' + pageid
                        newdict['text'] = page_text
                        newdict['title'] = pageid + '.  ' + toc_text
                        self.hframe.toc.insert(parentid, 'end',
				text=newdict['title'], tag='title',
				value = newpageno - 1, iid = pageid)
                    if newpagerex.match(line):
                        hierarchy = line.rstrip()
                        toc_text = []
                elif not toc_text:
                    toc_text = line.rstrip()
                    page_text = []
                elif not commentrex.match(line):
                    if not page_text:
                        page_text = line
                    else:
                        page_text += line

    def nextpage(self):
        # Go to next page
        if self.pageno < len(self.pages) - 1:
            self.pageno += 1
            self.redisplay()

    def prevpage(self):
        # Go to previous page
        if self.pageno > 0:
            self.pageno -= 1
            self.redisplay()

    def page(self, pagenum):
        # Go to indicated page
        if pagenum >= 0 and pagenum < len(self.pages):
            self.pageno = pagenum 
            self.redisplay()

    def close(self):
        # pop down help window
        self.withdraw()

    def open(self):
        # pop up help window
        self.deiconify()
        self.lift()
