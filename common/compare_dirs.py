#!/usr/bin/env python3
#
# compare_dirs.py <path>
#
#
# Compare the format subdirectories of <path> and report on which files do not appear
# in all of them.  If a directory has no files in it, then it is ignored.

import os
import sys

def compare_dirs(path, styles, formats, debug):
    do_cdl = True if 'cdl' in formats else False
    do_gds = True if 'gds' in formats else False
    do_lef = True if 'lef' in formats else False
    do_mag = True if 'mag' in formats else False
    do_maglef = True if 'maglef' in formats else False
    do_verilog = True if 'verilog' in formats else False

    try:
         d1 = os.listdir(path + '/cdl')
    except:
         d1 = []
    d1e = list(item for item in d1 if os.path.splitext(item)[1] == '.cdl')
    d1r = list(os.path.splitext(item)[0] for item in d1e)
    try:
        d2 = os.listdir(path + '/gds')
    except:
        d2 = []
    d2e = list(item for item in d2 if os.path.splitext(item)[1] == '.gds')
    d2r = list(os.path.splitext(item)[0] for item in d2e)
    try:
        d3 = os.listdir(path + '/lef')
    except:
        d3 = []
    d3e = list(item for item in d3 if os.path.splitext(item)[1] == '.lef')
    d3r = list(os.path.splitext(item)[0] for item in d3e)
    try:
        d4 = os.listdir(path + '/mag')
    except:
        d4 = []
    d4e = list(item for item in d4 if os.path.splitext(item)[1] == '.mag')
    d4r = list(os.path.splitext(item)[0] for item in d4e)
    try:
        d5 = os.listdir(path + '/maglef')
    except:
        d5 = []
    d5e = list(item for item in d5 if os.path.splitext(item)[1] == '.mag')
    d5r = list(os.path.splitext(item)[0] for item in d5e)
    try:
        d6 = os.listdir(path + '/verilog')
    except:
        d6 = []
    d6e = list(item for item in d6 if os.path.splitext(item)[1] == '.v')
    d6r = list(os.path.splitext(os.path.splitext(item)[0])[0] for item in d6e)
 
    d1r.sort()
    d2r.sort()
    d3r.sort()
    d4r.sort()
    d5r.sort()
    d6r.sort()

    d1_2 = list(item for item in d1r if item not in d2r)
    d1_3 = list(item for item in d1r if item not in d3r)
    d1_4 = list(item for item in d1r if item not in d4r)
    d1_5 = list(item for item in d1r if item not in d5r)
    d1_6 = list(item for item in d1r if item not in d6r)

    d2_1 = list(item for item in d2r if item not in d1r)
    d2_3 = list(item for item in d2r if item not in d3r)
    d2_4 = list(item for item in d2r if item not in d4r)
    d2_5 = list(item for item in d2r if item not in d5r)
    d2_6 = list(item for item in d2r if item not in d6r)

    d3_1 = list(item for item in d3r if item not in d1r)
    d3_2 = list(item for item in d3r if item not in d2r)
    d3_4 = list(item for item in d3r if item not in d4r)
    d3_5 = list(item for item in d3r if item not in d5r)
    d3_6 = list(item for item in d3r if item not in d6r)

    d4_1 = list(item for item in d4r if item not in d1r)
    d4_2 = list(item for item in d4r if item not in d2r)
    d4_3 = list(item for item in d4r if item not in d3r)
    d4_5 = list(item for item in d4r if item not in d5r)
    d4_6 = list(item for item in d4r if item not in d6r)

    d5_1 = list(item for item in d5r if item not in d1r)
    d5_2 = list(item for item in d5r if item not in d2r)
    d5_3 = list(item for item in d5r if item not in d3r)
    d5_4 = list(item for item in d5r if item not in d4r)
    d5_6 = list(item for item in d5r if item not in d6r)

    d6_1 = list(item for item in d6r if item not in d1r)
    d6_2 = list(item for item in d6r if item not in d2r)
    d6_3 = list(item for item in d6r if item not in d3r)
    d6_4 = list(item for item in d6r if item not in d4r)
    d6_5 = list(item for item in d6r if item not in d5r)

    d_complete = []
    if do_cdl:
        d_complete.extend(list(item for item in d1r if item not in d_complete))
    if do_gds:
        d_complete.extend(list(item for item in d2r if item not in d_complete))
    if do_lef:
        d_complete.extend(list(item for item in d3r if item not in d_complete))
    if do_mag:
        d_complete.extend(list(item for item in d4r if item not in d_complete))
    if do_maglef:
        d_complete.extend(list(item for item in d5r if item not in d_complete))
    if do_verilog:
        d_complete.extend(list(item for item in d6r if item not in d_complete))

    d_all = d_complete
    if do_cdl:
        d_all = list(item for item in d_all if item in d1r)
    if do_gds:
        d_all = list(item for item in d_all if item in d2r)
    if do_lef:
        d_all = list(item for item in d_all if item in d3r)
    if do_mag:
        d_all = list(item for item in d_all if item in d4r)
    if do_maglef:
        d_all = list(item for item in d_all if item in d5r)
    if do_verilog:
        d_all = list(item for item in d_all if item in d6r)

    d_notall = list(item for item in d_complete if item not in d_all)

    d_all.sort()
    d_complete.sort()
    d_notall.sort()
    
    if debug:
        print('Selected styles option: ' + ','.join(styles))
        print('Selected formats option: ' + ','.join(formats))
        print('\nd_complete = ' + ','.join(d_complete))
        print('\nd_notall = ' + ','.join(d_notall) + '\n')

    print('Library file type cross-correlation:' + '\n')

    if 'allgood' in styles:
        print('Cells appearing in all libraries:')
        for cell in d_all.sort():
           print(cell)

    if 'cross' in styles:
        # Print which cells appear in one format but not in another, for all format pairs
        if do_cdl:
            print('')
            if do_gds and len(d1_2) > 0:
                print('Cells appearing in cdl/ but not in gds/:')
                for cell in d1_2:
                    print(cell)
            if do_lef and len(d1_3) > 0:
                print('Cells appearing in cdl/ but not in lef/:')
                for cell in d1_3:
                    print(cell)
            if do_mag and len(d1_4) > 0:
                print('Cells appearing in cdl/ but not in mag/:')
                for cell in d1_4:
                    print(cell)
            if do_maglef and len(d1_5) > 0:
                print('Cells appearing in cdl/ but not in maglef/:')
                for cell in d1_5:
                    print(cell)
            if do_verilog and len(d1_6) > 0:
                print('Cells appearing in cdl/ but not in verilog/:')
                for cell in d1_6:
                    print(cell)

        if do_gds:
            print('')
            if do_cdl and len(d2_1) > 0:
                print('Cells appearing in gds/ but not in cdl/:')
                for cell in d2_1:
                    print(cell)
            if do_lef and len(d2_3) > 0:
                print('Cells appearing in gds/ but not in lef/:')
                for cell in d2_3:
                    print(cell)
            if do_mag and len(d2_4) > 0:
                print('Cells appearing in gds/ but not in mag/:')
                for cell in d2_4:
                    print(cell)
            if do_maglef and len(d2_5) > 0:
                print('Cells appearing in gds/ but not in maglef/:')
                for cell in d2_5:
                    print(cell)
            if do_verilog and len(d2_6) > 0:
                print('Cells appearing in gds/ but not in verilog/:')
                for cell in d2_6:
                    print(cell)

        if do_lef:
            print('')
            if do_cdl and len(d3_1) > 0:
                print('Cells appearing in lef/ but not in cdl/:')
                for cell in d3_1:
                    print(cell)
            if do_gds and len(d3_2) > 0:
                print('Cells appearing in lef/ but not in gds/:')
                for cell in d3_2:
                    print(cell)
            if do_mag and len(d3_4) > 0:
                print('Cells appearing in lef/ but not in mag/:')
                for cell in d3_4:
                    print(cell)
            if do_maglef and len(d3_5) > 0:
                print('Cells appearing in lef/ but not in maglef/:')
                for cell in d3_5:
                    print(cell)
            if do_verilog and len(d3_6) > 0:
                print('Cells appearing in lef/ but not in verilog/:')
                for cell in d3_6:
                    print(cell)

        if do_mag:
            print('')
            if do_cdl and len(d4_1) > 0:
                print('Cells appearing in mag/ but not in cdl/:')
                for cell in d4_1:
                    print(cell)
            if do_gds and len(d4_2) > 0:
                print('Cells appearing in mag/ but not in gds/:')
                for cell in d4_2:
                    print(cell)
            if do_lef and len(d4_3) > 0:
                print('Cells appearing in mag/ but not in lef/:')
                for cell in d4_3:
                    print(cell)
            if do_maglef and len(d4_5) > 0:
                print('Cells appearing in mag/ but not in maglef/:')
                for cell in d4_5:
                    print(cell)
            if do_verilog and len(d4_6) > 0:
                print('Cells appearing in mag/ but not in verilog/:')
                for cell in d4_6:
                    print(cell)

        if do_maglef:
            print('')
            if do_cdl and len(d5_1) > 0:
                print('Cells appearing in maglef/ but not in cdl/:')
                for cell in d5_1:
                    print(cell)
            if do_gds and len(d5_2) > 0:
                print('Cells appearing in maglef/ but not in gds/:')
                for cell in d5_2:
                    print(cell)
            if do_lef and len(d5_3) > 0:
                print('Cells appearing in maglef/ but not in lef/:')
                for cell in d5_3:
                    print(cell)
            if do_mag and len(d5_4) > 0:
                print('Cells appearing in maglef/ but not in mag/:')
                for cell in d5_4:
                    print(cell)
            if do_verilog and len(d5_6) > 0:
                print('Cells appearing in maglef/ but not in verilog/:')
                for cell in d5_6:
                    print(cell)
        
        if do_verilog:
            print('')
            if do_cdl and len(d6_1) > 0:
                print('Cells appearing in verilog/ but not in cdl/:')
                for cell in d6_1:
                    print(cell)
            if do_gds and len(d6_2) > 0:
                print('Cells appearing in verilog/ but not in gds/:')
                for cell in d6_2:
                    print(cell)
            if do_lef and len(d6_3) > 0:
                print('Cells appearing in verilog/ but not in lef/:')
                for cell in d6_3:
                    print(cell)
            if do_mag and len(d6_4) > 0:
                print('Cells appearing in verilog/ but not in mag/:')
                for cell in d6_4:
                    print(cell)
            if do_maglef and len(d6_5) > 0:
                print('Cells appearing in verilog/ but not in maglef/:')
                for cell in d6_5:
                    print(cell)

    if 'cell' in styles:
        # Print one cell per row, with list of formats per cell
        for cell in d_complete:
            informats = []
            if do_cdl and cell in d1r:
                informats.append('CDL')
            if do_gds and cell in d2r:
                informats.append('GDS')
            if do_lef and cell in d3r:
                informats.append('LEF')
            if do_mag and cell in d4r:
                informats.append('mag')
            if do_maglef and cell in d5r:
                informats.append('maglef')
            if do_verilog and cell in d6r:
                informats.append('verilog')
            print(cell + ': ' + ','.join(informats))

    if 'notcell' in styles:
        # Print one cell per row, with list of missing formats per cell
        for cell in d_complete:
            informats = []
            if do_cdl and cell not in d1r:
                informats.append('CDL')
            if do_gds and cell not in d2r:
                informats.append('GDS')
            if do_lef and cell not in d3r:
                informats.append('LEF')
            if do_mag and cell not in d4r:
                informats.append('mag')
            if do_maglef and cell not in d5r:
                informats.append('maglef')
            if do_verilog and cell not in d6r:
                informats.append('verilog')
            print(cell + ': ' + ','.join(informats))

    if 'table' in styles:
        cellnamelen = 0
        for cell in d_complete:
            if len(cell) > cellnamelen:
                cellnamelen = len(cell)

        # Print one cell per row, with list of formats per cell in tabular form
        outline = 'cell'
        outline += ' ' * (cellnamelen - 5)
        fmtspc = 0
        if do_cdl:
            outline += ' CDL'
            fmtspc += 4
        if do_gds:
            outline += ' GDS'
            fmtspc += 4
        if do_lef:
            outline += ' LEF'
            fmtspc += 4
        if do_mag:
            outline += ' mag'
            fmtspc += 4
        if do_maglef:
            outline += ' maglef'
            fmtspc += 7
        if do_verilog:
            outline += ' verilog'
            fmtspc += 8
        print(outline)
        print('-' * (cellnamelen + fmtspc))
        for cell in d_complete:
            informats = []
            outline = cell
            outline += ' ' * (cellnamelen - len(cell))
            if do_cdl:
                if cell in d1r:
                    outline += ' X  '
                else:
                    outline += '    '
            if do_gds:
                if cell in d2r:
                    outline += ' X  '
                else:
                    outline += '    '
            if do_lef:
                if cell in d3r:
                    outline += ' X  '
                else:
                    outline += '    '
            if do_mag:
                if cell in d4r:
                    outline += ' X  '
                else:
                    outline += '    '
            if do_maglef:
                if cell in d5r:
                    outline += ' X     '
                else:
                    outline += '       '
            if do_verilog:
                if cell in d6r:
                    outline += ' X'
                else:
                    outline += '  '
            print(outline)
        print('-' * (cellnamelen + fmtspc))

def usage():
    print('compare_dirs.py <path_to_dir> [-styles=<style_list>] [-debug] [-formats=<format_list>|"all"]')
    print('    <format_list>:  Comma-separated list of one or more of the following formats:')
    print('             cdl, gds, lef, verilog, mag, maglef')
    print('    <style_list>: Comma-separated list of one or more of the following styles:')
    print('             allgood, cross, cell, notcell, table')
    return 0

if __name__ == '__main__':

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    if len(arguments) < 1:
        print("Not enough options given to compare_dirs.py.")
        usage()
        sys.exit(0)

    debug = True if '-debug' in options else False

    allformats = ['cdl', 'gds', 'lef', 'mag', 'maglef', 'verilog']
    allstyles = ['allgood', 'cross', 'cell', 'notcell', 'table']

    formats = allformats
    styles = ['table']

    for option in options:
        if '=' in option:
            optpair = option.split('=')
            if optpair[0] == '-styles' or optpair[0] == '-style':
                if optpair[1] == 'all':
                    styles = allstyles
                else:
                    styles = optpair[1].split(',')
            elif optpair[0] == '-formats' or optpair[0] == '-format':
                if optpair[1] == 'all':
                    formats = allformats
                else:
                    formats = optpair[1].split(',')

    path = arguments[0]
    compare_dirs(path, styles, formats, debug)
    sys.exit(0)
