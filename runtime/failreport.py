#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Characterization Report Window for the project manager
#
#--------------------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# September 12, 2016
# Version 0.1
#----------------------------------------------------------

import os
import base64
import subprocess

import tkinter
from tkinter import ttk

import tooltip
import cace_makeplot

class FailReport(tkinter.Toplevel):
    """failure report window."""

    def __init__(self, parent=None, fontsize=11, *args, **kwargs):
        '''See the __init__ for Tkinter.Toplevel.'''
        tkinter.Toplevel.__init__(self, parent, *args, **kwargs)

        s = ttk.Style()
        s.configure('bg.TFrame', background='gray40')
        s.configure('italic.TLabel', font=('Helvetica', fontsize, 'italic'), anchor = 'west')
        s.configure('title.TLabel', font=('Helvetica', fontsize, 'bold italic'),
                        foreground = 'brown', anchor = 'center')
        s.configure('normal.TLabel', font=('Helvetica', fontsize))
        s.configure('red.TLabel', font=('Helvetica', fontsize), foreground = 'red')
        s.configure('green.TLabel', font=('Helvetica', fontsize), foreground = 'green4')
        s.configure('blue.TLabel', font=('Helvetica', fontsize), foreground = 'blue')
        s.configure('brown.TLabel', font=('Helvetica', fontsize, 'italic'),
			foreground = 'brown', anchor = 'center')
        s.configure('normal.TButton', font=('Helvetica', fontsize), border = 3,
			relief = 'raised')
        s.configure('red.TButton', font=('Helvetica', fontsize), foreground = 'red',
			border = 3, relief = 'raised')
        s.configure('green.TButton', font=('Helvetica', fontsize), foreground = 'green4',
			border = 3, relief = 'raised')
        s.configure('title.TButton', font=('Helvetica', fontsize, 'bold italic'),
                        foreground = 'brown', border = 0, relief = 'groove')

        self.withdraw()
        self.title('Local Characterization Report')
        self.root = parent.root
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        # Scrolled frame:  Need frame, then canvas and scrollbars;  finally, the
        # actual grid of results gets placed in the canvas.
        self.failframe = ttk.Frame(self)
        self.failframe.grid(column = 0, row = 0, sticky = 'nsew')
        self.mainarea = tkinter.Canvas(self.failframe)
        self.mainarea.grid(row = 0, column = 0, sticky = 'nsew')

        self.mainarea.faildisplay = ttk.Frame(self.mainarea)
        self.mainarea.create_window((0,0), window=self.mainarea.faildisplay,
			anchor="nw", tags="self.frame")

        # Create a frame for displaying plots, but don't put it in the grid.
        # Make it resizeable.
        self.plotframe = ttk.Frame(self)
        self.plotframe.rowconfigure(0, weight = 1)
        self.plotframe.columnconfigure(0, weight = 1)

        # Main window resizes, not the scrollbars
        self.failframe.rowconfigure(0, weight = 1)
        self.failframe.columnconfigure(0, weight = 1)
        # Add scrollbars
        xscrollbar = ttk.Scrollbar(self.failframe, orient = 'horizontal')
        xscrollbar.grid(row = 1, column = 0, sticky = 'nsew')
        yscrollbar = ttk.Scrollbar(self.failframe, orient = 'vertical')
        yscrollbar.grid(row = 0, column = 1, sticky = 'nsew')
        # Attach viewing area to scrollbars
        self.mainarea.config(xscrollcommand = xscrollbar.set)
        xscrollbar.config(command = self.mainarea.xview)
        self.mainarea.config(yscrollcommand = yscrollbar.set)
        yscrollbar.config(command = self.mainarea.yview)
        # Set up configure callback
        self.mainarea.faildisplay.bind("<Configure>", self.frame_configure)

        self.bbar = ttk.Frame(self)
        self.bbar.grid(column = 0, row = 1, sticky = "news")
        self.bbar.close_button = ttk.Button(self.bbar, text='Close',
		command=self.close, style = 'normal.TButton')
        self.bbar.close_button.grid(column=0, row=0, padx = 5)
        # Table button returns to table view but is only displayed for plots.
        self.bbar.table_button = ttk.Button(self.bbar, text='Table', style = 'normal.TButton')

        self.protocol("WM_DELETE_WINDOW", self.close)
        tooltip.ToolTip(self.bbar.close_button,
			text='Close detail view of conditions and results')

        self.sortdir = False
        self.data = []

    def grid_configure(self, padx, pady):
        pass

    def frame_configure(self, event):
        self.update_idletasks()
        self.mainarea.configure(scrollregion=self.mainarea.bbox("all"))

    def check_failure(self, record, calc, value):
        if not 'target' in record:
            return None
        else:
            target = record['target']

        if calc == 'min':
            targval = float(target)
            if value < targval:
                return True
        elif calc == 'max':
            targval = float(target)
            if value > targval:
                return True
        else:
            return None

    # Given an electrical parameter 'param' and a condition name 'condname', find
    # the units of that condition.  If the condition isn't found in the local
    # parameters, then it is searched for in 'globcond'.

    def findunit(self, condname, param, globcond):
        unit = ''
        try:
            loccond = next(item for item in param['conditions'] if item['condition'] == condname)
        except StopIteration:
            try:
                globitem = next(item for item in globcond if item['condition'] == condname)
            except (TypeError, StopIteration):
                unit = ''	# No units
            else:
                if 'unit' in globitem:
                    unit = globitem['unit']
                else:
                    unit = ''	# No units
        else:
            if 'unit' in loccond:
                unit = loccond['unit']
            else:
                unit = ''	# No units
        return unit

    def size_plotreport(self):
        self.update_idletasks()
        width = self.plotframe.winfo_width()
        height = self.plotframe.winfo_height()
        if width < 3 * height:
            self.plotframe.configure(width=height * 3)

    def size_failreport(self):
        # Attempt to set the datasheet viewer width to the interior width
        # but do not set it larger than the available desktop.

        self.update_idletasks()
        width = self.mainarea.faildisplay.winfo_width()
        screen_width = self.root.winfo_screenwidth()
        if width > screen_width - 20:
            self.mainarea.configure(width=screen_width - 20)
        else:
            self.mainarea.configure(width=width)

        # Likewise for the height, up to the desktop height.  Note that this
        # needs to account for both the button bar at the bottom of the GUI
        # window plus the bar at the bottom of the desktop.
        height = self.mainarea.faildisplay.winfo_height()
        screen_height = self.root.winfo_screenheight()
        if height > screen_height - 120:
            self.mainarea.configure(height=screen_height - 120)
        else:
            self.mainarea.configure(height=height)

    def table_to_histogram(self, globcond, filename):
        # Switch from a table view to a histogram plot view, using the
        # result as the X axis variable and count for the Y axis.

        # Destroy existing contents.
        for widget in self.plotframe.winfo_children():
            widget.destroy()

        param = self.data
        plotrec = {}
        plotrec['xaxis'] = param['method']
        plotrec['xlabel'] = param['method']
        plotrec['ylabel'] = 'COUNT'
        plotrec['type'] = 'histogram'
        if 'unit' in param:
            plotrec['xlabel'] += ' (' + param['unit'] + ')'

        results = param['results']

        if 'variables' in param:
            variables = param['variables']
        else:
            variables = []
        # faild = self.mainarea.faildisplay	# definition for convenience
        self.failframe.grid_forget()
        self.plotframe.grid(row = 0, column = 0, sticky = 'nsew')
        canvas = cace_makeplot.makeplot(plotrec, results, variables, parent = self.plotframe)
        if 'display' in param:
            ttk.Label(self.plotframe, text=param['display'], style='title.TLabel').grid(row=1, column=0)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky = 'nsew')
        # Finally, open the window if it was not already open.
        self.open()

    def table_to_plot(self, condition, globcond, filename):
        # Switch from a table view to a plot view, using the condname as
        # the X axis variable.

        # Destroy existing contents.
        for widget in self.plotframe.winfo_children():
            widget.destroy()

        param = self.data
        plotrec = {}
        plotrec['xaxis'] = condition
        plotrec['xlabel'] = condition
        # Note: cace_makeplot adds text for units, if available
        plotrec['ylabel'] = param['method']
        plotrec['type'] = 'xyplot'

        results = param['results']

        if 'variables' in param:
            variables = param['variables']
        else:
            variables = []

        # faild = self.mainarea.faildisplay	# definition for convenience
        self.failframe.grid_forget()
        self.plotframe.grid(row = 0, column = 0, sticky = 'nsew')
        canvas = cace_makeplot.makeplot(plotrec, results, variables, parent = self.plotframe)
        if 'display' in param:
            ttk.Label(self.plotframe, text=param['display'], style='title.TLabel').grid(row=1, column=0)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky = 'nsew')
        # Display the button to return to the table view
        # except for transient and Monte Carlo simulations which are too large to tabulate.
        if not condition == 'TIME':
            self.bbar.table_button.grid(column=1, row=0, padx = 5)
            self.bbar.table_button.configure(command=lambda param=param, globcond=globcond,
			filename=filename: self.display(param, globcond, filename))

        # Finally, open the window if it was not already open.
        self.open()

    def display(self, param=None, globcond=None, filename=None):
        # (Diagnostic)
        # print('failure report:  passed parameter ' + str(param))

        # Destroy existing contents.
        for widget in self.mainarea.faildisplay.winfo_children():
            widget.destroy()

        if not param:
            param = self.data

        # 'param' is a dictionary pulled in from the annotate datasheet.
        # If the failure display was called, then 'param' should contain
        # record called 'results'.  If the parameter has no results, then
        # there is nothing to do.

        if filename and 'plot' in param:
            simfiles = os.path.split(filename)[0] + '/ngspice/char/simulation_files/'
            self.failframe.grid_forget()
            self.plotframe.grid(row = 0, column = 0, sticky = 'nsew')

            # Clear the plotframe and remake
            for widget in self.plotframe.winfo_children():
                widget.destroy()

            plotrec = param['plot']
            results = param['results']
            if 'variables' in param:
                variables = param['variables']
            else:
                variables = []
            canvas = cace_makeplot.makeplot(plotrec, results, variables, parent = self.plotframe)
            if 'display' in param:
                ttk.Label(self.plotframe, text=param['display'],
				style='title.TLabel').grid(row=1, column=0)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky = 'nsew')
            self.data = param
            # Display the button to return to the table view
            self.bbar.table_button.grid(column=1, row=0, padx = 5)
            self.bbar.table_button.configure(command=lambda param=param, globcond=globcond,
			filename=filename: self.display(param, globcond, filename))

        elif not 'results' in param:
            print("No results to build a report with.")
            return

        else:
            self.data = param
            self.plotframe.grid_forget()
            self.failframe.grid(column = 0, row = 0, sticky = 'nsew')
            faild = self.mainarea.faildisplay	# definition for convenience
            results = param['results']
            names = results[0]
            units = results[1]
            results = results[2:]

            # Check for transient simulation
            if 'TIME' in names:
                # Transient data are (usually) too numerous to tabulate, so go straight to plot
                self.table_to_plot('TIME', globcond, filename)
                return

            # Check for Monte Carlo simulation
            if 'ITERATIONS' in names:
                # Monte Carlo data are too numerous to tabulate, so go straight to plot
                self.table_to_histogram(globcond, filename)
                return

            # Numerically sort by result (to be done:  sort according to up/down
            # criteria, which will be retained per header entry)
            results.sort(key = lambda row: float(row[0]), reverse = self.sortdir)

            # To get ranges, transpose the results matrix, then make unique
            ranges = list(map(list, zip(*results)))
            for r, vrange in enumerate(ranges):
                try:
                    vmin = min(float(v) for v in vrange)
                    vmax = max(float(v) for v in vrange)
                    if vmin == vmax:
                        ranges[r] = [str(vmin)]
                    else:
                        ranges[r] = [str(vmin), str(vmax)]
                except ValueError:
                    ranges[r] = list(set(vrange))
                    pass

            faild.titlebar = ttk.Frame(faild)
            faild.titlebar.grid(row = 0, column = 0, sticky = 'ewns')

            faild.titlebar.label1 = ttk.Label(faild.titlebar, text = 'Electrical Parameter: ',
			style = 'italic.TLabel')
            faild.titlebar.label1.pack(side = 'left', padx = 6, ipadx = 3)
            if 'display' in param:
                faild.titlebar.label2 = ttk.Label(faild.titlebar, text = param['display'],
			style = 'normal.TLabel')
                faild.titlebar.label2.pack(side = 'left', padx = 6, ipadx = 3)
                faild.titlebar.label3 = ttk.Label(faild.titlebar, text = '  Method: ',
			style = 'italic.TLabel')
                faild.titlebar.label3.pack(side = 'left', padx = 6, ipadx = 3)
            faild.titlebar.label4 = ttk.Label(faild.titlebar, text = param['method'],
			style = 'normal.TLabel')
            faild.titlebar.label4.pack(side = 'left', padx = 6, ipadx = 3)

            if 'min' in param:
                if 'target' in param['min']:
                    faild.titlebar.label7 = ttk.Label(faild.titlebar, text = '  Min Limit: ',
			style = 'italic.TLabel')
                    faild.titlebar.label7.pack(side = 'left', padx = 3, ipadx = 3)
                    faild.titlebar.label8 = ttk.Label(faild.titlebar, text = param['min']['target'],
    			style = 'normal.TLabel')
                    faild.titlebar.label8.pack(side = 'left', padx = 6, ipadx = 3)
                    if 'unit' in param:
                        faild.titlebar.label9 = ttk.Label(faild.titlebar, text = param['unit'],
				style = 'italic.TLabel')
                        faild.titlebar.label9.pack(side = 'left', padx = 3, ipadx = 3)
            if 'max' in param:
                if 'target' in param['max']:
                    faild.titlebar.label10 = ttk.Label(faild.titlebar, text = '  Max Limit: ',
			style = 'italic.TLabel')
                    faild.titlebar.label10.pack(side = 'left', padx = 6, ipadx = 3)
                    faild.titlebar.label11 = ttk.Label(faild.titlebar, text = param['max']['target'],
    			style = 'normal.TLabel')
                    faild.titlebar.label11.pack(side = 'left', padx = 6, ipadx = 3)
                    if 'unit' in param:
                        faild.titlebar.label12 = ttk.Label(faild.titlebar, text = param['unit'],
	    			style = 'italic.TLabel')
                        faild.titlebar.label12.pack(side = 'left', padx = 3, ipadx = 3)

            # Simplify view by removing constant values from the table and just listing them
            # on the second line.

            faild.constants = ttk.Frame(faild)
            faild.constants.grid(row = 1, column = 0, sticky = 'ewns')
            faild.constants.title = ttk.Label(faild.constants, text = 'Constant Conditions: ',
			style = 'italic.TLabel')
            faild.constants.title.grid(row = 0, column = 0, padx = 6, ipadx = 3)
            j = 0
            for condname, unit, range in zip(names, units, ranges):
                if len(range) == 1:
                    labtext = condname
                    # unit = self.findunit(condname, param, globcond)
                    labtext += ' = ' + range[0] + ' ' + unit + ' '
                    row = int(j / 3)
                    col = 1 + (j % 3)
                    ttk.Label(faild.constants, text = labtext,
				style = 'blue.TLabel').grid(row = row,
				column = col, padx = 6, sticky = 'nsew')
                    j += 1

            body = ttk.Frame(faild, style = 'bg.TFrame')
            body.grid(row = 2, column = 0, sticky = 'ewns')

            # Print out names
            j = 0
            for condname, unit, range in zip(names, units, ranges):
                # Now find the range for each entry from the global and local conditions.
                # Use local conditions if specified, otherwise default to global condition.
                # Each result is a list of three numbers for min, typ, and max.  List
                # entries may be left unfilled.

                if len(range) == 1:
                    continue
    
                labtext = condname
                plottext = condname
                if j == 0:
                    # Add unicode arrow up/down depending on sort direction
                    labtext += ' \u21e9' if self.sortdir else ' \u21e7'
                    header = ttk.Button(body, text=labtext, style = 'title.TButton',
				command = self.changesort)
                    tooltip.ToolTip(header, text='Reverse order of results')
                else:
                    header = ttk.Button(body, text=labtext, style = 'title.TLabel',
				command = lambda plottext=plottext, globcond=globcond,
				filename=filename: self.table_to_plot(plottext, globcond, filename))
                    tooltip.ToolTip(header, text='Plot results with this condition on the X axis')
                header.grid(row = 0, column = j, sticky = 'ewns')

                # Second row is the measurement unit
                # if j == 0:
                #     # Measurement unit of result in first column
                #     if 'unit' in param:
                #         unit = param['unit']
                #     else:
                #         unit = ''    # No units
                # else:
                #     # Measurement unit of condition in other columns
                #     # Find condition in local conditions else global conditions
                #     unit = self.findunit(condname, param, globcond)

                unitlabel = ttk.Label(body, text=unit, style = 'brown.TLabel')
                unitlabel.grid(row = 1, column = j, sticky = 'ewns')

                # (Pick up limits when all entries have been processed---see below)
                j += 1

            # Now list entries for each failure record.  These should all be in the
            # same order.
            m = 2
            for result in results:
                m += 1
                j = 0
                condition = result[0]
                lstyle = 'normal.TLabel'
                value = float(condition)
                if 'min' in param:
                    minrec = param['min']
                    if 'calc' in minrec:
                        calc = minrec['calc']
                    else:
                        calc = 'min'
                    if self.check_failure(minrec, calc, value):
                        lstyle = 'red.TLabel'
                if 'max' in param:
                    maxrec = param['max']
                    if 'calc' in maxrec:
                        calc = maxrec['calc']
                    else:
                        calc = 'max'
                    if self.check_failure(maxrec, calc, value):
                        lstyle = 'red.TLabel'

                for condition, range in zip(result, ranges):
                    if len(range) > 1:
                        pname = ttk.Label(body, text=condition, style = lstyle)
                        pname.grid(row = m, column = j, sticky = 'ewns')
                        j += 1

            # Row 2 contains the ranges of each column
            j = 1
            k = 1
            for vrange in ranges[1:]:
                if len(vrange) > 1:

                    condlimits = '( '
                
                    # This is a bit of a hack;  results are assumed floating-point
                    # unless they can't be resolved as a number.  So numerical values
                    # that should be treated as integers or strings must be handled
                    # here according to the condition type.
                    if names[k].split(':')[0] == 'DIGITAL':
                        for l in vrange:
                            condlimits += str(int(float(l))) + ' '
                    else:
                        for l in vrange:
                            condlimits += l + ' '
                    condlimits += ')'
                    header = ttk.Label(body, text=condlimits, style = 'blue.TLabel')
                    header.grid(row = 2, column = j, sticky = 'ewns')
                    j += 1
                k += 1

            # Add padding around widgets in the body of the failure report, so that
            # the frame background comes through, making a grid.
            for child in body.winfo_children():
                child.grid_configure(ipadx = 5, ipady = 1, padx = 2, pady = 2)

            # Resize the window to fit in the display, if necessary.
            self.size_failreport()

        # Don't put the button at the bottom to return to table view.
        self.bbar.table_button.grid_forget()
        # Finally, open the window if it was not already open.
        self.open()

    def changesort(self):
        self.sortdir = False if self.sortdir == True else True
        self.display(param=None)

    def close(self):
        # pop down failure report window
        self.withdraw()

    def open(self):
        # pop up failure report window
        self.deiconify()
        self.lift()
