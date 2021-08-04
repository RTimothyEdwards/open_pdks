#!/usr/bin/env python3
#
# Simple listbox with scrollbar and select button

import re
import tkinter
from tkinter import ttk

class ListBoxChoice(ttk.Frame):
    def __init__(self, parent, fontsize=11, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        s = ttk.Style()
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3, relief = 'raised')

    def populate(self, title, list=[]):
        self.value = None
        self.list = list[:]
        
        ttk.Label(self, text=title).pack(padx=5, pady=5)

        listFrame = ttk.Frame(self)
        listFrame.pack(side='top', padx=5, pady=5, fill='both', expand='true')
        
        scrollBar = ttk.Scrollbar(listFrame)
        scrollBar.pack(side='right', fill='y')
        self.listBox = tkinter.Listbox(listFrame, selectmode='single')
        self.listBox.pack(side='left', fill='x', expand='true')
        scrollBar.config(command=self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        self.list.sort(key=natsort_key)
        for item in self.list:
            self.listBox.insert('end', item)

        if len(self.list) == 0:
            self.listBox.insert('end', '(no items)')
        else:
            buttonFrame = ttk.Frame(self)
            buttonFrame.pack(side='bottom')

            selectButton = ttk.Button(buttonFrame, text="Select", command=self._select,
			style='normal.TButton')
            selectButton.pack(side='left', padx = 5)
            listFrame.bind("<Return>", self._select)

    def natsort_key(s, _nsre=re.compile('([0-9]+)')):
        # 'natural' sort function.  To make this alphabetical independently of
        # capitalization, use "else text.lower()" instead of "else text" below.
        return [int(text) if text.isdigit() else text for text in _nsre.split(s)]

    def _select(self, event=None):
        try:
            firstIndex = self.listBox.curselection()[0]
            self.value = self.list[int(firstIndex)]
        except IndexError:
            self.value = None

    def value(self):
        return self.value
