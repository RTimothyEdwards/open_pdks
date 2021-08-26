#!/usr/bin/env python3
#
# Simple ttk treeview with split view, scrollbar, and
# row of callback buttons

import os
import re
import itertools

import tkinter
from tkinter import ttk

#------------------------------------------------------
# Tree view used as a multi-column list box
#------------------------------------------------------

class TreeViewSplit(ttk.Frame):
    def __init__(self, parent, fontsize=11, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        s = ttk.Style()
        s.configure('normal.TLabel', font=('Helvetica', fontsize))
        s.configure('title.TLabel', font=('Helvetica', fontsize, 'bold'))
        s.configure('normal.TButton', font=('Helvetica', fontsize),
			border = 3, relief = 'raised')
        s.configure('Treeview.Heading', font=('Helvetica', fontsize, 'bold'))
        s.configure('Treeview.Column', font=('Helvetica', fontsize))
        self.fontsize = fontsize

    # Last item is a list of 2-item lists, each containing the name of a button
    # to place along the button bar at the bottom, and a callback function to
    # run when the button is pressed.

    def populate(self, title1="", item1list=[], title2="", item2list=[], buttons=[], height=10):
        self.item1list = item1list[:]
        self.item2list = item2list[:]
        columns = [0, 1]
        
        treeFrame = ttk.Frame(self)
        treeFrame.pack(side='top', padx=5, pady=5, fill='both', expand='true')
        
        scrollBar = ttk.Scrollbar(treeFrame)
        scrollBar.pack(side='right', fill='y')
        self.treeView = ttk.Treeview(treeFrame, selectmode='browse', columns=columns, height=height)
        self.treeView.pack(side='left', fill='both', expand='true')
        scrollBar.config(command=self.treeView.yview)
        self.treeView.config(yscrollcommand=scrollBar.set)
        self.treeView.column('#0', width=120, stretch='false')
        self.treeView.heading(0, text=title1, anchor='w')
        self.treeView.heading(1, text=title2, anchor='w')
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(side='bottom', fill='x')

        self.treeView.tag_configure('select',background='darkslategray',foreground='white')

        # Test type tags
        self.treeView.tag_configure('error', font=('Helvetica', self.fontsize - 1), foreground = 'red')
        self.treeView.tag_configure('clean', font=('Helvetica', self.fontsize - 1), foreground = 'green3')
        self.treeView.tag_configure('normal', font=('Helvetica', self.fontsize - 1), foreground = 'black')
        self.treeView.tag_configure('prep', font=('Helvetica', self.fontsize, 'bold italic'),
                        foreground = 'black', anchor = 'center')
        self.treeView.tag_configure('header1', font=('Helvetica', self.fontsize, 'bold italic'),
                        foreground = 'brown', anchor = 'center')
        self.treeView.tag_configure('header2', font=('Helvetica', self.fontsize - 1, 'bold'),
                        foreground = 'blue', anchor = 'center')
        self.treeView.tag_configure('header3', font=('Helvetica', self.fontsize - 1, 'bold'),
                        foreground = 'green2', anchor = 'center')
        self.treeView.tag_configure('header4', font=('Helvetica', self.fontsize - 1),
                        foreground = 'purple', anchor = 'center')


        self.func_buttons = []
        for button in buttons:
            func = button[2]
            # Each func_buttons entry is a list of two items;  first is the
            # button widget, and the second is a boolean that is True if the
            # button is to be present always, False if the button is only
            # present when there are entries in the itemlists.
            self.func_buttons.append([ttk.Button(buttonFrame, text=button[0],
			style = 'normal.TButton',
			command = lambda func=func: self.func_callback(func)),
			button[1]])

        self.selectcallback = None
        self.lastselected = None
        self.lasttag = None
        self.repopulate(item1list, item2list)

    def get_button(self, index):
        if index >= 0 and index < len(self.func_buttons):
            return self.func_buttons[index][0]
        else:
            return None

    def set_title(self, title):
        self.treeView.heading('#0', text=title, anchor='w')

    def repopulate(self, item1list=[], item2list=[]):

        # Remove all children of treeview
        self.treeView.delete(*self.treeView.get_children())

        self.item1list = item1list[:]
        self.item2list = item2list[:]
        lines = max(len(self.item1list), len(self.item2list))

        # Parse the information coming from comp.out.  This is preferably
        # handled from inside netgen, but that requires development in netgen.
        # Note:  A top-level group is denoted by an empty string.

        nested = ['']
        if lines > 0:
            # print("Create item ID 0 parent = ''")
            self.treeView.insert(nested[-1], 'end', text='-', iid='0',
			value=['Initialize', 'Initialize'], tags=['prep'])
            nested.append('0')
            tagstyle = 'header1'

        emptyrec = re.compile('^[\t ]*$')
        subrex = re.compile('Subcircuit summary')
        cktrex = re.compile('Circuit[\t ]+[12]:[\t ]+([^ \t]+)')
        netrex = re.compile('NET mismatches')
        devrex = re.compile('DEVICE mismatches')
        seprex = re.compile('-----')
        sumrex = re.compile('Netlists ')
        matchrex = re.compile('.*\*\*Mismatch\*\*')
        incircuit = False
        watchgroup = False
        groupnum = 0

        for item1, item2, index in zip(self.item1list, self.item2list, range(lines)):
            # Remove blank lines from the display
            lmatch = emptyrec.match(item1)
            if lmatch:
                lmatch = emptyrec.match(item2)
                if lmatch:
                    continue
            index = str(index + 1)
            # Parse text to determine how to structure and display it.
            tagstyle = 'normal'
            nextnest = None
            lmatch = subrex.match(item1)
            if lmatch:
                nested = ['']		# pop back to topmost level
                nextnest = index
                tagstyle = 'header1'
                incircuit = False
                watchgroup = False
                groupnum = 0
                item1 = 'Layout compare'
                item2 = 'Schematic compare'
                cname1 = 'Layout'		# Placeholder
                cname2 = 'Schematic'		# Placeholder
            else:
                lmatch = cktrex.match(item1)
                if lmatch and not incircuit:
                    # Pick up circuit names and replace them in the title, then use them
                    # for all following titles.
                    cname1 = lmatch.group(1)
                    lmatch = cktrex.match(item2)
                    cname2 = lmatch.group(1)
                    print("Circuit names " + cname1 + " " + cname2)
                    # Rewrite title
                    cktitem = self.treeView.item(nested[-1], values=[cname1 + ' compare',
				cname2 + ' compare'])
                    nextnest = index
                    tagstyle = 'header2'
                    incircuit = True
                    item1 = cname1 + ' Summary'
                    item2 = cname2 + ' Summary'
                elif lmatch:
                    continue
                else:
                    lmatch = netrex.match(item1)
                    if lmatch:
                        if watchgroup:
                            nested = nested[0:-1]
                        nested = nested[0:-1]
                        nextnest = index
                        tagstyle = 'header2'
                        groupnum = 1
                        watchgroup = True
                        item1 = cname1 + ' Net mismatches'
                        item2 = cname2 + ' Net mismatches'
                    else:
                        lmatch = devrex.match(item1)
                        if lmatch:
                            if watchgroup:
                                nested = nested[0:-1]
                            nested = nested[0:-1]
                            nextnest = index
                            tagstyle = 'header2'
                            groupnum = 1
                            watchgroup = True
                            item1 = cname1 + ' Device mismatches'
                            item2 = cname2 + ' Device mismatches'
                        else:
                            lmatch = seprex.match(item1)
                            if lmatch:
                                if watchgroup:
                                    tagstyle = 'header3'
                                    item1 = 'Group ' + str(groupnum)
                                    item2 = 'Group ' + str(groupnum)
                                    if groupnum > 1:
                                        nested = nested[0:-1]
                                    groupnum += 1 
                                    nextnest = index
                                    watchgroup = False
                                else:
                                    if groupnum > 0:
                                        watchgroup = True
                                    continue
                            else:
                                lmatch = sumrex.match(item1)
                                if lmatch:
                                    if watchgroup:
                                        nested = nested[0:-1]
                                    nested = nested[0:-1]
                                    watchgroup = False
                                    tagstyle = 'header2'
                                    groupnum = 0

            lmatch1 = matchrex.match(item1)
            lmatch2 = matchrex.match(item2)
            if lmatch1 or lmatch2:
                tagstyle='error'
            
            # print("Create item ID " + str(index) + " parent = " + str(nested[-1]))
            self.treeView.insert(nested[-1], 'end', text=index, iid=index, value=[item1, item2],
			tags=[tagstyle])

            if nextnest:
                nested.append(nextnest)

        for button in self.func_buttons:
            button[0].pack_forget()

        if lines == 0:
            self.treeView.insert('', 'end', text='-', value=['(no items)', '(no items)'])
            for button in self.func_buttons:
                if button[1]:
                    button[0].pack(side='left', padx = 5)
        else:
            for button in self.func_buttons:
                button[0].pack(side='left', padx = 5)

    # Special routine to pull in the JSON file data produced by netgen-1.5.72
    def json_repopulate(self, lvsdata):

        # Remove all children of treeview
        self.treeView.delete(*self.treeView.get_children())

        # Parse the information coming from comp.out.  This is preferably
        # handled from inside netgen, but that requires development in netgen.
        # Note:  A top-level group is denoted by an empty string.

        index = 0
        errtotal = {}
        errtotal['net'] = 0
        errtotal['netmatch'] = 0
        errtotal['device'] = 0
        errtotal['devmatch'] = 0
        errtotal['property'] = 0
        errtotal['pin'] = 0
        ncells = len(lvsdata)
        for c in range(0, ncells):
            cellrec = lvsdata[c]
            if c == ncells - 1:
                topcell = True
            else:
                topcell = False

            errcell = {}
            errcell['net'] = 0
            errcell['netmatch'] = 0
            errcell['device'] = 0
            errcell['devmatch'] = 0
            errcell['property'] = 0
            errcell['pin'] = 0;

	    # cellrec is a dictionary.  Parse the cell summary, then failing nets,
	    # devices, and properties, and finally pins.

            if 'name' in cellrec:
                names = cellrec['name']
                cname1 = names[0]
                cname2 = names[1]

                item1 = cname1
                item2 = cname2
                tagstyle = 'header1'
                index += 1
                nest0 = index
                self.treeView.insert('', 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])
            else:
                # Some cells have pin comparison but are missing names (needs to be
                # fixed in netgen.  Regardless, if there's no name, then ignore.
                continue

            if 'devices' in cellrec or 'nets' in cellrec:
                item1 = cname1 + " Summary"
                item2 = cname2 + " Summary"
                tagstyle = 'header2'
                index += 1
                nest1 = index
                self.treeView.insert(nest0, 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

            if 'devices' in cellrec:
                item1 = cname1 + " Devices"
                item2 = cname2 + " Devices"
                tagstyle = 'header3'
                index += 1
                nest2 = index
                self.treeView.insert(nest1, 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

                devices = cellrec['devices']
                devlist = [val for pair in zip(devices[0], devices[1]) for val in pair]
                devpair = list(devlist[p:p + 2] for p in range(0, len(devlist), 2))
                for dev in devpair:
                    c1dev = dev[0]
                    c2dev = dev[1]

                    item1 = c1dev[0] + "(" + str(c1dev[1]) + ")"
                    item2 = c2dev[0] + "(" + str(c2dev[1]) + ")"

                    diffdevs = abs(c1dev[1] - c2dev[1])
                    if diffdevs == 0:
                        tagstyle = 'normal'
                    else:
                        tagstyle = 'error'
                        errcell['device'] += diffdevs
                        if topcell:
                            errtotal['device'] += diffdevs
                    index += 1
                    nest2 = index
                    self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

            if 'nets' in cellrec:
                item1 = cname1 + " Nets"
                item2 = cname2 + " Nets"
                tagstyle = 'header3'
                index += 1
                nest2 = index
                self.treeView.insert(nest1, 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

                nets = cellrec['nets']

                item1 = nets[0]
                item2 = nets[1]
                diffnets = abs(nets[0] - nets[1])
                if diffnets == 0:
                    tagstyle = 'normal'
                else:
                    tagstyle = 'error'
                    errcell['net'] = diffnets
                    if topcell:
                        errtotal['net'] += diffnets
                index += 1
                nest2 = index
                self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

            if 'badnets' in cellrec:
                badnets = cellrec['badnets']

                if len(badnets) > 0:
                    item1 = cname1 + " Net Mismatches"
                    item2 = cname2 + " Net Mismatches"
                    tagstyle = 'header2'
                    index += 1
                    nest1 = index
                    self.treeView.insert(nest0, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

                groupnum = 0
                for group in badnets:
                    groupc1 = group[0]
                    groupc2 = group[1]
                    nnets = len(groupc1)

                    groupnum += 1
                    tagstyle = 'header3'
                    index += 1
                    nest2 = index
                    item1 = "Group " + str(groupnum) + ' (' + str(nnets) + ' nets)'
                    self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item1], tags=[tagstyle])

                    tagstyle = 'error'
                    errcell['netmatch'] += nnets
                    if topcell:
                        errtotal['netmatch'] += nnets

                    for netnum in range(0, nnets):
                        if netnum > 0:
                            item1 = ""
                            index += 1
                            nest3 = index
                            self.treeView.insert(nest2, 'end', text=index, iid=index,
					value=[item1, item1], tags=[tagstyle])

                        net1 = groupc1[netnum]
                        net2 = groupc2[netnum]
                        tagstyle = 'header4'
                        item1 = net1[0]
                        item2 = net2[0]
                        index += 1
                        nest3 = index
                        self.treeView.insert(nest2, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

                        # Pad shorter device list to the length of the longer one
                        netdevs = list(itertools.zip_longest(net1[1], net2[1]))
                        for devpair in netdevs:
                            devc1 = devpair[0]
                            devc2 = devpair[1]
                            tagstyle = 'normal'
                            if devc1 and devc1[0] != "":
                                item1 = devc1[0] + '/' + devc1[1] + ' = ' + str(devc1[2])
                            else:
                                item1 = ""
                            if devc2 and devc2[0] != "":
                                item2 = devc2[0] + '/' + devc2[1] + ' = ' + str(devc2[2])
                            else:
                                item2 = ""
                            index += 1
                            nest3 = index
                            self.treeView.insert(nest2, 'end', text=index, iid=index,
					value=[item1, item2], tags=[tagstyle])

            if 'badelements' in cellrec:
                badelements = cellrec['badelements']

                if len(badelements) > 0:
                    item1 = cname1 + " Device Mismatches"
                    item2 = cname2 + " Device Mismatches"
                    tagstyle = 'header2'
                    index += 1
                    nest1 = index
                    self.treeView.insert(nest0, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

                groupnum = 0
                for group in badelements:
                    groupc1 = group[0]
                    groupc2 = group[1]
                    ndevs = len(groupc1)

                    groupnum += 1
                    tagstyle = 'header3'
                    index += 1
                    nest2 = index
                    item1 = "Group " + str(groupnum) + ' (' + str(ndevs) + ' devices)'
                    self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item1], tags=[tagstyle])

                    tagstyle = 'error'
                    errcell['devmatch'] += ndevs
                    if topcell:
                        errtotal['devmatch'] += ndevs

                    for elemnum in range(0, ndevs):
                        if elemnum > 0:
                            item1 = ""
                            index += 1
                            nest3 = index
                            self.treeView.insert(nest2, 'end', text=index, iid=index,
					value=[item1, item1], tags=[tagstyle])

                        elem1 = groupc1[elemnum]
                        elem2 = groupc2[elemnum]
                        tagstyle = 'header4'
                        item1 = elem1[0]
                        item2 = elem2[0]
                        index += 1
                        nest3 = index
                        self.treeView.insert(nest2, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

                        # Pad shorter pin list to the length of the longer one
                        elempins = list(itertools.zip_longest(elem1[1], elem2[1]))
                        for pinpair in elempins:
                            pinc1 = pinpair[0]
                            pinc2 = pinpair[1]
                            tagstyle = 'normal'
                            if pinc1 and pinc1[0] != "":
                                item1 = pinc1[0] + ' = ' + str(pinc1[1])
                            else:
                                item1 = ""
                            if pinc2 and pinc2[0] != "":
                                item2 = pinc2[0] + ' = ' + str(pinc2[1])
                            else:
                                item2 = ""
                            index += 1
                            nest3 = index
                            self.treeView.insert(nest2, 'end', text=index, iid=index,
					value=[item1, item2], tags=[tagstyle])

            if 'properties' in cellrec:
                properties = cellrec['properties']
                numproperr = len(properties)
                if numproperr > 0:
                    item1 = cname1 + " Properties"
                    item2 = cname2 + " Properties"
                    tagstyle = 'header2'
                    index += 1
                    nest1 = index
                    self.treeView.insert(nest0, 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])
                    errcell['property'] = numproperr
                    errtotal['property'] += numproperr

                for prop in properties:

                    if prop != properties[0]:
                        item1 = ""
                        index += 1
                        nest2 = index
                        self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item1], tags=[tagstyle])

                    propc1 = prop[0]
                    propc2 = prop[1]

                    tagstyle = 'header3'
                    item1 = propc1[0]
                    item2 = propc2[0]
                    index += 1
                    nest2 = index
                    self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

                   # Pad shorter property list to the length of the longer one
                    elemprops = list(itertools.zip_longest(propc1[1], propc2[1]))
                    for proppair in elemprops:
                        perrc1 = proppair[0]
                        perrc2 = proppair[1]
                        tagstyle = 'normal'
                        if perrc1 and perrc1[0] != "":
                            item1 = perrc1[0] + ' = ' + str(perrc1[1])
                        else:
                            item1 = ""
                        if perrc2 and perrc2[0] != "":
                            item2 = perrc2[0] + ' = ' + str(perrc2[1])
                        else:
                            item2 = ""
                        index += 1
                        nest2 = index
                        self.treeView.insert(nest1, 'end', text=index, iid=index,
					value=[item1, item2], tags=[tagstyle])

            if 'pins' in cellrec:
                item1 = cname1 + " Pins"
                item2 = cname2 + " Pins"
                tagstyle = 'header2'
                index += 1
                nest1 = index
                self.treeView.insert(nest0, 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

                pins = cellrec['pins']
                pinlist = [val for pair in zip(pins[0], pins[1]) for val in pair]
                pinpair = list(pinlist[p:p + 2] for p in range(0, len(pinlist), 2))
                for pin in pinpair:
                    item1 = re.sub('!$', '', pin[0].lower())
                    item2 = re.sub('!$', '', pin[1].lower())
                    if item1 == item2:
                        tagstyle = 'header4'
                    else:
                        tagstyle = 'error'
                        errcell['pin'] += 1
                        if topcell:
                            errtotal['pin'] += 1
                    index += 1
                    nest2 = index
                    self.treeView.insert(nest1, 'end', text=index, iid=index,
				value=[item1, item2], tags=[tagstyle])

            allcellerror = errcell['net'] + errcell['device'] + errcell['property'] + errcell['pin'] + errcell['netmatch'] + errcell['devmatch']
            if allcellerror > 0:
                item1 = 'Errors:  Net = ' + str(errcell['net']) + ', Device = ' + str(errcell['device']) + ', Property = ' + str(errcell['property']) + ', Pin = ' + str(errcell['pin']) + ', Net match = ' + str(errcell['netmatch']) + ', Device match = ' + str(errcell['devmatch'])
                tagstyle = 'error'
            else:
                item1 = 'LVS Clean'
                tagstyle = 'clean'

            item2 = ""
            index += 1
            nest0 = index
            self.treeView.insert('', 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

        item1 = "Final LVS result:"
        item2 = ""
        tagstyle = 'header1'
        index += 1
        nest0 = index
        self.treeView.insert('', 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

        allerror = errtotal['net'] + errtotal['device'] + errtotal['property'] + errtotal['pin'] + errtotal['netmatch'] + errtotal['devmatch']
        if allerror > 0:
            item1 = 'Errors:  Net = ' + str(errtotal['net']) + ', Device = ' + str(errtotal['device']) + ', Property = ' + str(errtotal['property']) + ', Pin = ' + str(errtotal['pin']) + ', Net match = ' + str(errtotal['netmatch']) + ', Device match = ' + str(errtotal['devmatch'])
            tagstyle = 'error'
        else:
            item1 = 'LVS Clean'
            tagstyle = 'clean'

        item2 = ""
        index += 1
        nest0 = index
        self.treeView.insert('', 'end', text=index, iid=index, value=[item1, item2],
				tags=[tagstyle])

        for button in self.func_buttons:
            button[0].pack_forget()

        if index == 0:
            self.treeView.insert('', 'end', text='-', value=['(no items)', '(no items)'])
            for button in self.func_buttons:
                if button[1]:
                    button[0].pack(side='left', padx = 5)
        else:
            for button in self.func_buttons:
                button[0].pack(side='left', padx = 5)

    # Return values from the treeview
    def getlist(self):
        return self.treeView.get_children()

    def func_callback(self, callback, event=None):
        callback(self.treeView.item(self.treeView.selection()))

    def bindselect(self, callback):
        self.selectcallback = callback

    def setselect(self, value):
        self.treeView.selection_set(value)

    def selected(self):
        value = self.treeView.item(self.treeView.selection())
        if value['values']:
            return value
        else:
            return None
