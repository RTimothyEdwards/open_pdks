#!/usr/bin/env python3
"""
cace_makeplot.py
Plot routines for CACE using matplotlib
"""

import re
import os
import matplotlib
from matplotlib.figure import Figure

# Warning: PIL Tk required, may not be in default install of python3.
# For Fedora, for example, need "yum install python-pillow-tk"

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_agg import FigureCanvasAgg

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def makeplot(plotrec, results, variables, parent = None):
    """
    Given a plot record from a spec sheet and a full set of results, generate
    a plot.  The name of the plot file and the vectors to plot, labels, legends,
    and so forth are all contained in the 'plotrec' dictionary.
    """

    binrex = re.compile(r'([0-9]*)\'([bodh])', re.IGNORECASE)
    # Organize data into plot lines according to formatting

    if 'type' in plotrec:
        plottype = plotrec['type']
    else:
        plottype = 'xyplot'

    # Find index of X data in results
    if plottype == 'histogram':
        xname = 'RESULT'
    else:
        xname = plotrec['xaxis']
    rlen = len(results[0])
    try:
        xidx = next(r for r in range(rlen) if results[0][r] == xname)
    except StopIteration:
        return None
                            
    # Find unique values of each variable (except results, traces, and iterations)
    steps = [[0]]
    traces = [0]
    bmatch = binrex.match(results[1][0])
    if bmatch:
        digits = bmatch.group(1)
        if digits == '':
            digits = len(results[2][0])
        else:
            digits = int(digits)
        cbase = bmatch.group(2)
        if cbase == 'b':
            base = 2
        elif cbase == 'o':
            base = 8
        elif cbase == 'd':
            base = 10
        else:
            base = 16
        binconv = [[base, digits]]
    else:
        binconv = [[]]

    for i in range(1, rlen):
        lsteps = []

        # results labeled 'ITERATIONS', 'RESULT', 'TRACE', or 'TIME' are treated as plot vectors
        isvector = False
        if results[0][i] == 'ITERATIONS':
            isvector = True
        elif results[0][i] == 'RESULT':
            isvector = True
        elif results[0][i] == 'TIME':
            isvector = True
        elif results[0][i].split(':')[0] == 'TRACE':
            isvector = True

        # results whose labels are in the 'variables' list are treated as plot vectors
        if isvector == False:
            if variables:
                try:
                    varrec = next(item for item in variables if item['condition'] == results[0][i])
                except StopIteration:
                    pass
                else:
                    isvector = True

        # those results that are not traces are stepped conditions (unless they are constant)
        if isvector == False:
            try:
                for item in list(a[i] for a in results[2:]):
                    if item not in lsteps:
                        lsteps.append(item)
            except IndexError:
                # Diagnostic
                print("Error: Failed to find " + str(i) + " items in result set")
                print("Results set has " + len(results[0]) + " entries")
                print(str(results[0]))
                for x in range(2, len(results)):
                    if len(results[x]) <= i:
                        print("Failed at entry " + str(x))
                        print(str(results[x]))
                        break

        # 'ITERATIONS' and 'TIME' are the x-axis variable, so don't add them to traces
        # (but maybe just check that xaxis name is not made into a trace?)
        elif results[0][i] != 'ITERATIONS' and results[0][i] != 'TIME':
            traces.append(i)
        steps.append(lsteps)

        # Mark which items need converting from digital.  Format is verilog-like.  Use
        # a format width that is larger than the actual number of digits to force
        # unsigned conversion.
        bmatch = binrex.match(results[1][i])
        if bmatch:
            digits = bmatch.group(1)
            if digits == '':
                digits = len(results[2][i])
            else:
                digits = int(digits)
            cbase = bmatch.group(2)
            if cbase == 'b':
                base = 2
            elif cbase == 'o':
                base = 8
            elif cbase == 'd':
                base = 10
            else:
                base = 16
            binconv.append([base, digits])
        else:
            binconv.append([])
        
    # Support older method of declaring a digital vector
    if xname.split(':')[0] == 'DIGITAL':
        binconv[xidx] = [2, len(results[2][0])]

    # Which stepped variables (ignoring X axis variable) have more than one value?
    watchsteps = list(i for i in range(1, rlen) if len(steps[i]) > 1 and i != xidx)

    # Diagnostic
    # print("Stepped conditions are: ")
    # for j in watchsteps:
    #      print(results[0][j] + '  (' + str(len(steps[j])) + ' steps)')

    # Collect results.  Make a separate record for each unique set of stepped conditions
    # encountered.  Record has (X, Y) vector and a list of conditions.
    pdata = {}
    for item in results[2:]:
        if xname.split(':')[0] == 'DIGITAL' or binconv[xidx] != []:
            base = binconv[xidx][0]
            digits = binconv[xidx][1]
            # Recast binary strings as integers
            # Watch for strings that have been cast to floats (need to find the source of this)
            if '.' in item[xidx]:
                item[xidx] = item[xidx].split('.')[0]
            a = int(item[xidx], base)
            b = twos_comp(a, digits)
            xvalue = b
        else:
            xvalue = item[xidx]

        slist = []
        for j in watchsteps:
             slist.append(item[j])
        istr = ','.join(slist)
        if istr not in pdata:
            stextlist = []
            for j in watchsteps:
                if results[1][j] == '':
                    stextlist.append(results[0][j] + '=' + item[j])
                else:
                    stextlist.append(results[0][j] + '=' + item[j] + ' ' + results[1][j])
            pdict = {}
            pdata[istr] = pdict
            pdict['xdata'] = []
            if stextlist:
                tracelegnd = False
            else:
                tracelegnd = True

            for i in traces:
                aname = 'ydata' + str(i)
                pdict[aname] = []
                alabel = 'ylabel' + str(i)
                tracename = results[0][i]
                if ':' in tracename:
                    tracename = tracename.split(':')[1]

                if results[1][i] != '' and not binrex.match(results[1][i]):
                    tracename += ' (' + results[1][i] + ')'

                pdict[alabel] = tracename

            pdict['sdata'] = ' '.join(stextlist)
        else:
            pdict = pdata[istr]
        pdict['xdata'].append(xvalue)

        for i in traces:
            # For each trace, convert the value from digital to integer if needed
            if binconv[i] != []:
                base = binconv[i][0]
                digits = binconv[i][1]
                a = int(item[i], base)
                b = twos_comp(a, digits)
                yvalue = b
            else:
                yvalue = item[i]

            aname = 'ydata' + str(i)
            pdict[aname].append(yvalue)

    fig = Figure()
    if parent == None:
        canvas = FigureCanvasAgg(fig)
    else:
        canvas = FigureCanvasTkAgg(fig, parent)

    # With no parent, just make one plot and put the legend off to the side.  The
    # 'extra artists' capability of print_figure will take care of the bounding box.
    # For display, prepare two subplots so that the legend takes up the space of the
    # second one.
    if parent == None:
        ax = fig.add_subplot(111)
    else:
        ax = fig.add_subplot(121)

    # fig.hold(True)
    for record in pdata:
        pdict = pdata[record]

        # Check if xdata is numeric
        try:
            test = float(pdict['xdata'][0])
        except ValueError:
            numeric = False
            xdata = [i for i in range(len(pdict['xdata']))]
        else:
            numeric = True
            xdata = list(map(float,pdict['xdata']))

        if plottype == 'histogram':
            ax.hist(xdata, histtype='barstacked', label=pdict['sdata'], stacked=True)
        else:
            for i in traces:
                aname = 'ydata' + str(i)
                alabl = 'ylabel' + str(i)
                ax.plot(xdata, pdict[aname], label=pdict[alabl] + ' ' + pdict['sdata'])
                # Diagnostic
                # print("Y values for " + aname + ": " + str(pdict[aname]))

        if not numeric:
            ax.set_xticks(xdata)
            ax.set_xticklabels(pdict['xdata'])

    if 'xlabel' in plotrec:
        if results[1][xidx] == '' or binrex.match(results[1][xidx]):
            ax.set_xlabel(plotrec['xlabel'])
        else:
            ax.set_xlabel(plotrec['xlabel'] + ' (' + results[1][xidx] + ')')
    else:
        # Automatically generate X axis label if not given alternate text
        xtext = results[0][xidx]
        if results[1][xidx] != '':
            xtext += ' (' + results[1][xidx] + ')'
        ax.set_xlabel(xtext)

    if 'ylabel' in plotrec:
        if results[1][0] == '' or binrex.match(results[1][0]):
            ax.set_ylabel(plotrec['ylabel'])
        else:
            ax.set_ylabel(plotrec['ylabel'] + ' (' + results[1][0] + ')')
    else:
        # Automatically generate Y axis label if not given alternate text
        ytext = results[0][0]
        if results[1][0] != '' or binrex.match(results[1][0]):
            ytext += ' (' + results[1][0] + ')'
        ax.set_ylabel(ytext)

    ax.grid(True)
    if watchsteps or tracelegnd:
        legnd = ax.legend(loc = 2, bbox_to_anchor = (1.05, 1), borderaxespad=0.)
    else:
        legnd = None

    if legnd:
        legnd.set_draggable(True)

    if parent == None:
        if not os.path.exists('ngspice/simulation_files'):
            os.makedirs('ngspice/simulation_files')

        filename = 'ngspice/simulation_files/' + plotrec['filename']
        # NOTE: print_figure only makes use of bbox_extra_artists if
        # bbox_inches is set to 'tight'.  This forces a two-pass method
        # that calculates the real maximum bounds of the figure.  Otherwise
        # the legend gets clipped.
        if legnd:
            canvas.print_figure(filename, bbox_inches = 'tight',
                        bbox_extra_artists = [legnd])
        else:
            canvas.print_figure(filename, bbox_inches = 'tight')

    return canvas
