#!/usr/bin/env python3
"""
cdl2spi.py : netlist processor
Copyright (c) 2016, 2020 efabless Corporation.
All rights reserved.

usage: cdl2spi.py <inCDLfile> [<outSPCfile>] [options...]
Writes to .spi to outSPCfile, or stdout if no output argument given. Sets exit
status if there were non-zero errors.  Most errors/warnings are annotated in-line
in the stdout each before the relevant line.
"""

import sys, getopt
import os
import re
import textwrap

# Convert linear scale to area scale suffix 
# (e.g., if linear scale is 1e-6 ('u') then area scales as 1e-12 ('p'))

def getAreaScale(dscale):
    ascale = ''
    if dscale == 'm':
        ascale = 'u'
    elif dscale == 'u':
        ascale = 'p'
    elif dscale == 'n':
        ascale = 'a'
    return ascale

# Check nm (instanceName) in the context of sub (subckt): is it used yet?
# If not used yet, mark it used, and return as-is.
# Else generate a unique suffixed version, and mark it used, return it.
# If 1M suffixes don't generate a unique name, throw exception.
#   hasInm : global hash, key of hash is (subckt, iname)

hasInm = {}
def uniqInm(sub, nm):
    subl=sub.lower()
    nml=nm.lower()
    if not (subl, nml) in hasInm:
        hasInm[ (subl, nml) ] = 1
        return nm
    for i in range(1000000):
        nm2 = nm + "_q" + str(i)
        nm2l = nm2.lower()
        if not (subl, nm2l) in hasInm:
            hasInm[ (subl, nm2l) ] = 1
            return nm2
    # not caught anywhere, and gives (intended) non-zero exit status
    raise AssertionError("uniqInm: range overflow for (%s,%s)" % (sub, nm))

# Map illegal characters in an nm (instanceName) in context of sub (subckt).
# For ngspice, '/' is illegal in instanceNames. Replace it with '|', BUT
# then make sure the new name is still unique: does not collide with a name
# used so far or another already derived unique name.

inmBadChars='/'
inmRplChars='|'
inmBadCharREX=re.compile( "["+ inmBadChars+"]" )

def mapInm(sub, nm):
    nm2 = inmBadCharREX.sub(inmRplChars, nm)
    return uniqInm(sub, nm2)

# Process subckt line (array of tokens). Return new array of tokens.
# There might be a ' /' in the line that needs to be deleted. It may be standalone ' / ', or
# butting against the next token. It may be before all pins, after all pins, or between pins.
# Do not touch / in a parameter assignment expression.
# Do not touch / embedded in a pinName.
# May touch / butting front of very first parameter assignment expression.
# .subckt NM / p1 p2 p3 x=y g=h
# .subckt NM /p1 p2 p3 x=y g=h
# .subckt NM p1 p2 / p3 x=y g=h
# .subckt NM p1 p2 /p3 x=y g=h
# .subckt NM p1 p2 p3 / x=y g=h
# .subckt NM p1 p2 p3 /x=y g=h
# .subckt NM p1 p2 p3 x=y g=(a/b)     (don't touch this /)
# .subckt NM p1 p2/3/4 p3 x=y g=(a/b) (don't touch these /)

def mapSubcktDef(tok):
    # find index of one-past first token (beyond ".subckt NM") containing an =, if any
    param0 = len(tok)
    for i in range(2, len(tok)):
        if '=' in tok[i]:
            param0 = i+1
            break
    # find first token before or including that 1st-param, starting with /:
    #   strip the slash.
    for i in range(2, param0):
        if tok[i][0] == '/':
            tok[i] = tok[i][1:]
            if tok[i] == "":
                del tok[i]
            break
    return tok

def test_mapSubcktInst1():
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3".split())))
    print( " ".join(mapSubcktDef( ".subckt abc / p1 p2 p3".split())))
    print( " ".join(mapSubcktDef( ".subckt abc /p1 p2 p3".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 /p3".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 / p3".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3 x=4 /y=5".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3 x=4/2 y=5".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3 / x=4/2 y=5".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3 x=4/2 /y=5".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1 p2 p3 /x=4/2 y=5".split())))
    print( " ".join(mapSubcktDef( ".subckt abc p1/2/3 p2 p3 /x=4/2 y=5".split())))

# Process subckt instance line (array of tokens). Return new array of tokens.
# (This function does not map possible illegal-chars in instanceName).
# There might be a ' /' in the line that needs to be deleted. It may be standalone ' / ', or
# butting against the next token. It can only be after pins, before or butting subcktName.
#
# Do not touch / in, butting, or after 1st parameter assignment expression.
# Do not touch / embedded in a netName.
# Do not touch / embedded in instanceName (they are handled separately elsewhere).
# xa/b/c p1 p2 p3 / NM x=y g=h
# xa/b/c p1 p2 p3 /NM x=y g=h
# xabc p1 p2/3/4 p3 /NM x=(a/b) g=h
# xabc p1 p2/3/4 p3 / NM x=(a/b) g=h
# xabc p1 p2/3/4 p3 NM x=(a/b) / g=h    (don't touch; perhaps needs to be an error trapped somewhere)
# xabc p1 p2/3/4 p3 NM / x=(a/b) g=h    (don't touch; perhaps needs to be an error trapped somewhere)
# xa/b/c p1 p2/3/4 p3 NM x=(a/b) g=h    (don't touch these /)

def mapSubcktInst(tok):
    # find index of first token (beyond "x<iname>") containing an =, if any
    param0 = tlen = len(tok)
    for i in range(1, tlen):
        if '=' in tok[i]:
            param0 = i
            break
    # Determine modelName index. Either just prior to 1st-param (if any) else last token.
    modndx = tlen - 1
    if param0 < tlen:
        modndx = param0 - 1;
    # If modndx now points to a standalone /, that can't be (would yield missing/empty modelName).
    # Actual modelName must be before it. We need to check, possibly strip / on/before actual modelName.
    # (Even though standlone / after model are most likely an independent error: we don't touch 'em).
    while modndx > 1 and tok[modndx] == "/":
        modndx-=1
    # Check for standalone / before modelName. Else for modelName starting with /.
    slashndx = modndx - 1
    if slashndx > 0 and tok[slashndx] == "/":
        del tok[slashndx]
    else:
        if modndx > 0 and tok[modndx].startswith("/"):
            tok[modndx] = tok[modndx][1:]
    return tok

def test_mapSubcktInst2():
    print( " ".join(mapSubcktInst( "xa/b/c p1 p2 p3 / NM x=y g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c p1 p2 p3 /NM x=y g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 /NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 / NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 NM x=(a/b) / g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 NM / x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 /NM / x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xabc p1 p2/3/4 p3 / NM / x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c p1 p2/3/4 p3 NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c / NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c /NM x=(a/b) g=h".split())))
    print( " ".join(mapSubcktInst( "xa/b/c /NM".split())))

# Primitives with M=<n> need to add additional par1=<n>.
# Process token list, return new token list.
# note: line at this point may be like: m... p1 p2 p3 p4 NMOS M=1 $blah W=... L=...
# meaning M=1 is not necessarily in a block of all parameter-assignments at EOL.
# But by processing the line from end backwards, we pick up LAST M= if there are
# multiple (which condition really should  get flagged as an error).
# And M= is more likely towards end of the line than front of line (thus faster).
# If "M=" with no value, do nothing (should also be a flagged error).

def mapMfactor(tok, options={}):
    # find index of M=* if any, starting from end.
    # "addinm" is an additional parameter that takes the same argument as M
    addinm = options['addinm'] if 'addinm' in options else []
    mndx = 0
    val = ""
    for i in range(len(tok)-1, 0, -1):
        if tok[i].lower().startswith("m="):
            mndx = i
            break
    if mndx > 0:
        val = tok[i][2:]
    if val != "":
        for p in addinm:
            tok += [ addinm + val]
    return tok

def test_mapMfactor():
    print( " ".join(mapMfactor( "m1 p1 p2 p3 p4 NM M=joe".split())))
    print( " ".join(mapMfactor( "m1 p1 p2 p3 p4 NM M= $SUB=agnd".split())))
    print( " ".join(mapMfactor( "m1 p1 p2 p3 p4 NM M=2 $SUB=agnd WM=4".split())))
    print( " ".join(mapMfactor( "m1 p1 p2 p3 p4 NM".split())))

# From $nm=... strip the $. Preserve order on the line. No attempt to
# detect any resultant collisions. "W=5 $W=10" becomes "W=5 W=10".
# Don't touch $SUB=... or $[...] or $.model=... or $blah (no assigment).

def mapCDLparam(tok):
    for i in range(1, len(tok)):
        if not tok[i].startswith("$"):
            continue
        eqi = tok[i].find("=")
        if eqi > 1:
            pnm = tok[i][1:eqi]
            pnml = pnm.lower()
            if pnml in ("sub",".model"):
                continue
            tok[i] = tok[i][1:]
    return tok

def test_CDLparam():
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M=joe".split())))
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M= $SUB=agnd $.model=NM3 $LDD".split())))
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M= $SUB=agnd $[NM3]".split())))
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M=joe $X=y".split())))
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M= $SUB=agnd $.model=NM3 $Z=4 $Z=5".split())))
    print( " ".join(mapCDLparam( "m1 p1 p2 p3 p4 NM M= W=1 $W=2 W=3 $SUB=agnd $[NM3]".split())))

# Extract $SUB=<tname>. and $[mnm] (or $.model=<mnm>) from tokens.
# Return array of three items: [ <tname>, <mnm>, tok ] where tok is remainder.
# Absent $SUB= or model directives give "".
# Since we delete tokens, process tokens in reverse order.

def mapCDLtermModel(tok):
    cdlTerm=""
    cdlModel=""
    for i in range(len(tok)-1, 0, -1):
        if not tok[i].startswith("$"):
            if '=' in tok[i]:
                continue
            elif cdlModel == '':
                cdlModel = tok[i]
                del tok[i]
                break
        tokl = tok[i].lower()
        if tokl.startswith("$sub="):
            if cdlTerm == "":
                cdlTerm = tok[i][5:]
            del tok[i]
            continue
        if tokl.startswith("$.model="):
            if cdlModel == "":
                cdlModel = tok[i][8:]
            del tok[i]
            continue
        if tokl.startswith("$[") and tokl.endswith("]"):
            if cdlModel == "":
                cdlModel = tok[i][2:-1]
            del tok[i]
            continue
    return [ cdlTerm, cdlModel, tok ]

def test_CDLtermModel():
    print( mapCDLtermModel( "m1 p1 p2 p3 p4 NM M=joe".split()))
    print( mapCDLtermModel( "m1 p1 p2 p3 p4 NM $SUB=agnd".split()))
    print( mapCDLtermModel( "m1 p1 p2 p3 p4 NM $SUB= $[PMOS] M=joe".split()))
    print( mapCDLtermModel( "m1 p1 p2 p3 p4 NM $sUb=vssa $.MoDeL=PM4 M=joe".split()))

# Determine if a single word looks like a plain numeric spice value.
# It means a real-number with optional scale suffix, and optional unit suffix.
# Only unit-suffix we support is m (meters) (because CDL-std describes it).
# Only scale factors supported are: t,g,meg,k,mil,m,u,n,p,f
# This does not arithmetically compute anything.
# Just returns True or False.
# 220p 10nm -40g 2milm .34e+3 3.1e-4 .34e+3pm 3.1e-4meg
# (Arguable we should strip a unit-suffix)?
# def isPlainNumeric(word):

# Segregate any remaining $* items from input tokens.
# Return [ assignments, directives, remaining ] where each are lists.
# Those that look like assigments $nm=... are separated from $blah.

def mapDiscard(tok):
    tlen = len(tok)
    assign=[]
    directive=[]
    for i in range(len(tok)-1, 0, -1):
        if not tok[i].startswith("$"):
            continue
        if "=" in tok[i]:
            assign += [ tok[i] ]
            del tok[i]
            continue
        directive += [ tok[i] ]
        del tok[i]
    return [ assign, directive, tok ]

def test_mapDiscard():
    print( mapDiscard( "m1 p1 p2 p3 p4 NM $X=4 $LDD M=joe $SUB=agnd ".split()))
    print( mapDiscard( "m1 p1 p2 p3 p4 NM $X $LDD M=joe $SUB=agnd ".split()))
    print( mapDiscard( "m1 p1 p2 p3 p4 NM M=joe SUB=agnd ".split()))

# From a token-slice, partition into assignments and non-assignments.
# Return [ assigns, nonAssigns] where each are lists.

def mapPartAssign(tok):
    tlen = len(tok)
    assign=[]
    nona=[]
    for i in range(len(tok)):
        if "=" in tok[i]:
            assign += [ tok[i] ]
            continue
        nona += [ tok[i] ]
    return [ assign, nona ]

def test_mapPartAssign():
    print( mapPartAssign( "NM X=4 220nm -1.2e-5g LDD M=joe".split()))
    print( mapPartAssign( "X=4 M=joe".split()))
    print( mapPartAssign( "NM 220nm -1.2e-5g LDD".split()))
    print( mapPartAssign( "".split()))

# Find an assignment to nm in the token list (nm=val).
# Return [val, tok]. If edit is True, the nm=val is removed from return tok.
# If multiple nm=... the last one is used. If del is True, all nm=... are removed.

def mapLookup(tok, nm, edit):
    tlen = len(tok)
    val=""
    nmeq = nm.lower() + "="
    nmeqlen = len(nmeq)
    for i in range(len(tok)-1, 0, -1):
        if not tok[i].lower().startswith(nmeq):
            continue
        if val == "":
            val = tok[i][nmeqlen:]
        if edit:
            del tok[i]
    return [ val, tok ]

def test_mapLookup():
    print( mapLookup( "cnm t1 t2 area=220p PERimeter=100u M=joe par1=1".split(), "periMETER", True))
    print( mapLookup( "m1 p1 p2 p3 p4 NM $X=4 $LDD M=joe $SUB=agnd ".split(), "x", True))
    print( mapLookup( "m1 p1 p2 p3 p4 NM X=4 $LDD M=joe $SUB=agnd ".split(), "x", True))
    print( mapLookup( "m1 p1 p2 p3 p4 NM x=4 $LDD M=joe $SUB=agnd ".split(), "x", True))
    print( mapLookup( "m1 p1 p2 p3 p4 NM x=4 X=5 xy=6 $LDD M=joe $SUB=agnd ".split(), "x", True))
    print( mapLookup( "m1 p1 p2 p3 p4 NM x=4 X=5 xy=6 $LDD M=joe $SUB=agnd ".split(), "x", False))

# Format a diode. cdlTerm and cdlModel are passed in but ignored/unused.
# Processes tok and returns a final token list to be output.
# If after "dnm t1 t2 modelName ", there are plain numerics (index 4,5), take them as area and peri,
# (override other area= peri= parameters), format them as area=... peri=...
# (Caller already error checked the 1st minimum FOUR fields are there).

def mapDiode(cdlTerm, cdlModel, tok, options={}):
    ignore = options['ignore'] if 'ignore' in options else []
    # strip remaining $* directives
    [ ign, ign, tok ] = mapDiscard(tok)
    # Find explicit area= peri=, remove from tok.
    [area,  tok] = mapLookup(tok, "area",  True)
    [peri, tok] = mapLookup(tok, "peri", True)
    for p in ignore:
        [ign, tok] = mapLookup(tok, p, True)
    # For just token-slice after modelName, partition into assignments and non-assigns.
    [assign, nona] = mapPartAssign(tok[4:])
    tok = tok[0:4]
    # TODO: If we have more than two non-assignments it should be an error?
    # Override area/peri with 1st/2nd non-assigment values.
    if len(nona) > 0:
        area = nona.pop(0)
    if len(nona) > 0:
        peri = nona.pop(0)
    if area != "":
        tok += [ "area=" + area ]
    if peri != "":
        tok += [ "peri=" + peri ]
    tok += nona
    tok += assign
    return tok

def test_mapDiode():
    print( mapDiode( "", "", "dnm t1 t2 DN 220p 100u M=joe par1=1".split()))
    print( mapDiode( "", "", "dnm t1 t2 DN peri=100u area=220p M=joe par1=1".split()))
    print( mapDiode( "", "", "dnm t1 t2 DN  M=joe par1=1".split()))

# Format a mosfet. cdlTerm and cdlModel are passed in but ignored/unused.
# Processes tok and returns a final token list to be output.
# If after "mnm t1 t2 t3 t4 modelName ", there are plain numerics (index 6,7), take them as W and L,
# (override other W= L= parameters), format them as W=... L=...
# (Caller already error checked the 1st minimum SIX fields are there).

def mapMos(cdlTerm, cdlModel, tok, options={}):
    ignore = options['ignore'] if 'ignore' in options else []
    # strip remaining $* directives
    [ ign, ign, tok ] = mapDiscard(tok)
    # Find explicit W= L=, remove from tok.
    [w, tok] = mapLookup(tok, "w",  True)
    [l, tok] = mapLookup(tok, "l", True)
    for p in ignore:
        [ign, tok] = mapLookup(tok, p, True)
    # For scaling, find AS, PS, AD, PD, SA, SB, SC, and SD
    [sarea, tok] = mapLookup(tok, "as",  True)
    [darea, tok] = mapLookup(tok, "ad",  True)
    [sperim, tok] = mapLookup(tok, "ps",  True)
    [dperim, tok] = mapLookup(tok, "pd",  True)
    [sa, tok] = mapLookup(tok, "sa",  True)
    [sb, tok] = mapLookup(tok, "sb",  True)
    [sd, tok] = mapLookup(tok, "sd",  True)

    dscale = options['dscale'] if 'dscale' in options else ''
    ascale = getAreaScale(dscale)

    # For just token-slice after modelName, partition into assignments and non-assigns.
    [assign, nona] = mapPartAssign(tok[6:])
    tok = tok[0:6]
    # TODO: If we have more than two non-assignments it should be an error?
    # Override W/L with 1st/2nd non-assigment values.
    if len(nona) > 0:
        w = nona.pop(0)
    if len(nona) > 0:
        l = nona.pop(0)
    if w != "":
        tok += ["W=" + w + dscale]
    if l != "":
        tok += ["L=" + l + dscale]
    if darea != "":
        tok += ["AD=" + darea + ascale]
    if sarea != "":
        tok += ["AS=" + sarea + ascale]
    if dperim != "":
        tok += ["PD=" + dperim + dscale]
    if sperim != "":
        tok += ["PS=" + sperim + dscale]
    if sa != "":
        tok += ["SA=" + sa + dscale]
    if sb != "":
        tok += ["SB=" + sb + dscale]
    if sd != "":
        tok += ["SD=" + sd + dscale]
    tok += nona
    tok += assign
    return tok

def test_mapMos():
    print( mapMos( "", "", "mnm t1 t2 t3 t4 NM 220p 100u M=joe par1=1".split()))
    print( mapMos( "", "", "mnm t1 t2 t3 t4 NM L=100u W=220p M=joe par1=1".split()))
    print( mapMos( "", "", "mnm t1 t2 t3 t4 PM M=joe par1=1".split()))

# Format a cap.
# Processes tok and returns a final token list to be output.
# Optional cdlTerm adds a 3rd terminal.
# If after "cnm t1 t2 ", there is plain numeric or C=numeric they are DISCARDED.
# area/peri/perimeter assignments are respected. Both peri/perimeter assign to perm=
# in the output. No perimeter= appears in the output.
# (Caller already error checked the 1st minimum 3 fields are there; plus cdlModel is non-null).

def mapCap(cdlTerm, cdlModel, tok, options={}):
    ignore = options['ignore'] if 'ignore' in options else []
    # strip remaining $* directives
    [ ign, ign, tok ] = mapDiscard(tok)
    # Find explicit area= peri= perimeter=, remove from tok. peri overwrites perimeter,
    # both assign to perim. Lookup/discard a C=.
    [area,  tok] = mapLookup(tok, "area",  True)
    [perim,  tok] = mapLookup(tok, "perimeter", True)
    [length,  tok] = mapLookup(tok, "l",  True)
    [width,  tok] = mapLookup(tok, "w",  True)
    [peri, tok] = mapLookup(tok, "peri", True)
    if peri == "":
        peri = perim
    [ign, tok] = mapLookup(tok, "c", True)
    for p in ignore:
        [ign, tok] = mapLookup(tok, p, True)
    # For just token-slice after modelName, partition into assignments and non-assigns.
    # We ignore the nonassignments. Need remaining assignments for M= par1=.
    [assign, nona] = mapPartAssign(tok[3:])
    dscale = options['dscale'] if 'dscale' in options else ''
    ascale = getAreaScale(dscale)
    tok = tok[0:3]
    if cdlTerm != "":
        tok += [ cdlTerm ]
    if cdlModel != "":
        tok += [ cdlModel ]
    if area != "":
        tok += [ "area=" + area + ascale]
    if peri != "":
        tok += [ "peri=" + peri + dscale]
    if length != "":
        tok += [ "L=" + length + dscale]
    if width != "":
        tok += [ "W=" + width + dscale]
    tok += assign
    return tok

def test_mapCap():
    print( mapCap( "", "CPP", "cnm t1 t2 area=220p peri=100u M=joe par1=1".split()))
    print( mapCap( "", "CPP", "cnm t1 t2 area=220p perimeter=100u M=joe par1=1".split()))
    print( mapCap( "", "CPP", "cnm t1 t2 area=220p peri=199u perimeter=100u M=joe par1=1".split()))
    print( mapCap( "", "CPP", "cnm t1 t2 M=joe par1=1".split()))
    print( mapCap( "", "CPP", "cnm t1 t2 C=444 area=220p peri=199u perimeter=100u M=joe par1=1".split()))
    print( mapCap( "", "CPP", "cnm t1 t2 444 M=joe par1=1".split()))
    print( mapCap( "agnd", "CPP2", "cnm t1 t2 $LDD 220p M=joe par1=1".split()))

# Format a res.
# Processes tok and returns a final token list to be output.
# Optional cdlTerm adds a 3rd terminal.
# If after "rnm t1 t2 ", there is plain numeric or R=numeric they are DISCARDED.
# W/L assignments are respected.
# (Caller already error checked the 1st minimum 3 fields are there; plus cdlModel is non-null).

def mapRes(cdlTerm, cdlModel, tok, options={}):
    dscale = options['dscale'] if 'dscale' in options else ''
    ignore = options['ignore'] if 'ignore' in options else []
    # strip remaining $* directives
    [ ign, ign, tok ] = mapDiscard(tok)
    # Find explicit w/l, remove from tok.
    # Lookup/discard a R=.
    [w,  tok] = mapLookup(tok, "w",  True)
    [l,  tok] = mapLookup(tok, "l", True)
    [r, tok] = mapLookup(tok, "r", True)
    for p in ignore:
        [ign, tok] = mapLookup(tok, p, True)
    # For just token-slice after modelName, partition into assignments and non-assigns.
    # We ignore the nonassignments. Need remaining assignments for M= par1=.
    [assign, nona] = mapPartAssign(tok[3:])
    if len(nona) > 0:
        r = nona.pop(0)
    tok = tok[0:3]
    if cdlTerm != "":
        tok += [ cdlTerm ]
    if cdlModel != "":
        tok += [ cdlModel ]
    if w != "":
        tok += [ "W=" + w + dscale]
    if l != "":
        tok += [ "L=" + l + dscale]
    # Convert name "short" to zero resistance
    if r == "short":
        tok += [ "0" ]
    tok += assign
    return tok

def test_mapRes():
    print( mapRes( "", "RPP1", "rnm t1 t2 w=2 L=1 M=joe par1=1".split()))
    print( mapRes( "", "RPP1", "rnm t1 t2 444 w=2 L=1 M=joe par1=1".split()))
    print( mapRes( "", "RPP1", "rnm t1 t2 R=444 w=2 L=1 M=joe par1=1".split()))
    print( mapRes( "", "R2", "rnm t1 t2 L=2 W=10 M=joe par1=1".split()))
    print( mapRes( "", "RM2", "rnm t1 t2 area=220p perim=199u perimeter=100u M=joe par1=1".split()))
    print( mapRes( "", "RM2", "rnm t1 t2 M=joe par1=1".split()))
    print( mapRes( "agnd", "RM3", "rnm t1 t2 $LDD 220p M=joe par1=1".split()))
    print( mapRes( "agnd", "RM3", "rnm t1 t2 $LDD 220p L=4 W=12 M=joe par1=1".split()))

# Format a bipolar. cdlTerm is optional. cdlModel is ignored.
# Processes tok and returns a final token list to be output.
# Optional cdlTerm adds an optional 4th terminal.
# If after "qnm t1 t2 t3 model", there are plain numeric (not x=y) they are DISCARDED.
# (Caller already error checked the 1st minimum 5 fields are there; plus cdlModel is null).

def mapBipolar(cdlTerm, cdlModel, tok, options={}):
    # strip remaining $* directives
    ignore = options['ignore'] if 'ignore' in options else []
    [ ign, ign, tok ] = mapDiscard(tok)
    for p in ignore:
        [ign, tok] = mapLookup(tok, p, True)
    # For just token-slice after modelName, partition into assignments and non-assigns.
    # We ignore the nonassignments. Need remaining assignments for M= par1=.
    [assign, nona] = mapPartAssign(tok[5:])
    # Start with "qnm t1 t2 t3". Insert optional 4th term. Then insert modelName.
    model = tok[4]
    tok = tok[0:4]
    if cdlTerm != "":
        tok += [ cdlTerm ]
    tok += [ model ]
    tok += assign
    return tok

def test_mapBipolar():
    print( mapBipolar( "", "any", "qnm t1 t2 t3 QP1 M=joe par1=1".split()))
    print( mapBipolar( "", "", "qnm t1 t2 t3 QP2 M=joe par1=1".split()))
    print( mapBipolar( "", "", "qnm t1 t2 t3 QP2 $EA=12 M=joe par1=1".split()))
    print( mapBipolar( "", "", "qnm t1 t2 t3 QP3 M=joe EA=14 par1=1".split()))
    print( mapBipolar( "agnd", "", "qnm t1 t2 t3 QP4 $LDD 220p M=joe par1=1".split()))
    print( mapBipolar( "agnd", "any", "qnm t1 t2 t3 QP4 $LDD 220p L=4 W=12 M=joe par1=1".split()))

#------------------------------------------------------------------------
# Main routine to do the conversion from CDL format to SPICE format
#------------------------------------------------------------------------

def cdl2spice(fnmIn, fnmOut, options):

    err = 0
    warn = 0

    # Open and read input file

    try:
        with open(fnmIn, 'r') as inFile:
            cdltext = inFile.read()
            # Unwrap continuation lines
            lines = cdltext.replace('\n+', ' ').splitlines()
    except:
        print('cdl2spi.py: failed to open ' + fnmIn + ' for reading.', file=sys.stderr)
        return 1

    # Loop over original CDL:
    #   record existing instanceNames (in subckt-context), for efficient membership
    #   tests later.  Track the subckt-context, instanceNames only need to be unique
    #   within current subckt.

    sub = ""
    for i in lines:
        if i == "":
            continue
        tok = i.split()
        tlen = len(tok)
        if tlen == 0:
            continue
        t0 = tok[0].lower()
        if t0 == '.subckt' and tlen > 1:
            sub = tok[1].lower()
            continue
        if t0 == '.ends':
            sub = ""
            continue
        c0 = tok[0][0].lower()
        if c0 in '.*':
            continue
        # this will ignore primitive-devices (jfet) we don't support.
        # TODO: flag them somewhere else as an ERROR.
        if not c0 in primch2:
            continue
        # a primitive-device or subckt-instance we care about and support
        # For subckt-instances record the instanceName MINUS lead x.
        nm = tok[0]
        if c0 == 'x':
            nm = nm[1:]
        hasInm[ (sub, nm) ] = 1


    # loop over original CDL: do conversions.
    # Track the subckt-context while we go; instanceNames only need to be unique
    # within current subckt.

    sub = ""
    tmp = []
    for i in lines:
        tok = i.split()
        tlen = len(tok)
        # AS-IS: empty line or all (preserved) whitespace
        if tlen == 0:
            tmp += [ i ]
            continue

        # get 1st-token original, as lowercase, and 1st-char of 1st-token lowercase.
        T0 = tok[0]
        t0 = T0.lower()
        c0 = t0[0]

        # AS-IS: comment
        if c0 == '*':
            tmp += [i]
            continue

        # AS-IS: .ends; update subckt-context to outside-of-a-subckt
        if t0 == '.ends':
            sub = ""
            tmp += [i]
            continue

        # change .param to a comment, output it
        if t0 == '.param':
            tmp += ["*"+i]
            continue

        # track .subckt context; process / in .subckt line, and output it.
        if t0 == '.subckt':
            if tlen < 2:
                err+=1
                msg = "*cdl2spi.py: ERROR: Missing subckt name:"
                tmp += [ msg, i ]
                continue
            T1 = tok[1]
            sub = T1.lower()
            tok = mapSubcktDef(tok)
            tmp += [ " ".join(tok) ]
            continue

        # subckt instance line. Process /, map instanceName (exclude x), and output it.
        if c0 == 'x':
            nm = T0[1:]
            if nm == "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Missing subckt instance name:"
                tmp += [ msg, i ]
                continue
            inm = mapInm(sub, nm)
            tok[0] = T0[0] + inm
            tok = mapSubcktInst(tok)
            tmp += [ " ".join(tok) ]
            continue

        # all primitives: need instanceName mapped, including 1st char in name.
        # all primitives: need M=n copied to an added par1=n
        # all primitives: Except for $SUB=... $[...] strip $ from $nm=... parameters.
        # all primitives: Isolate $SUB and $[...] for further processing (in
        # primitive-specific sections).

        cdlTerm=""
        cdlModel=""
        if c0 in primch:
            nm = T0[1:]
            if nm == "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Missing primitive instance name:"
                tmp += [ msg, i ]
                continue
            nm = T0
            nm = mapInm(sub, nm)
            tok[0] = nm
            tok = mapMfactor(tok, options)
            tok = mapCDLparam(tok)
            [cdlTerm, cdlModel, tok] = mapCDLtermModel(tok)

        # diode formats:
        #   dname t1 t2 model <numericA> <numericP> m=...
        # l:dname t1 t2 model {<numericA>} {<numericP>} {m=...} {$SUB=...}
        # out format:
        #   Xdname t1 t2 model area=<numericA> peri=<numericP> m=... par1=...
        # We flag $SUB=... : because so far (for ngspice) we CHOOSE not to support three
        # terminal diodes.
        # CDL-std does not define $[...] as available for diodes, so we silently ignore
        # it.
        # Always 2 terminals and a modelName. 
        # We already have peri=... and area=... and have ambiguity with plain numerics.
        # TODO: generate a warning in case of ambiguity, but prefer plain numerics
        # (with nm= added).

        if c0 == "d":
            tlen = len(tok)
            if tlen < 4:
                err+=1
                msg = "*cdl2spi.py: ERROR: Diode does not have minimum two terminals and model:"
                tmp += [ msg, i ]
                continue
            if cdlTerm != "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Diode does not support $SUB=...:"
                tmp += [ msg, i ]
                continue
            tok = mapDiode(cdlTerm, cdlModel, tok, options)
            # add X to tok0.
            if options['subckt']:
                tok[0] = "X" + tok[0]
            tmp += [ " ".join(tok) ]
            continue

        # mosfet formats:
        #   mname t1 t2 t3 t4 model W=... L=... m=...
        # l:mname t1 t2 t3 t4 model {W=... L=...} {m=...} {$NONSWAP} {$LDD[type]}
        # l:mname t1 t2 t3 t4 model <width> <length> {m=...} {$NONSWAP} {$LDD[type]}
        # output format:
        #   Xmname t1 t2 t3 t4 model W=... L=... m=... par1=...
        # Fixed 4 terminals and a modelName.
        # May already have W= L= and ambiguity with plain numerics.
        # TODO: generate a warning in case of ambiguity, but prefer plain numerics
        # (with nm= added).
        if c0 == "m":
            tlen = len(tok)
            if tlen < 6:
                err+=1
                msg = "*cdl2spi.py: ERROR: Mosfet does not have minimum four terminals and model:"
                tmp += [ msg, i ]
                continue
            if cdlTerm != "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Mosfet does not support $SUB=...:"
                tmp += [ msg, i ]
                continue
            tok = mapMos(cdlTerm, cdlModel, tok, options)
            # add X to tok0.
            if options['subckt']:
                tok[0] = "X" + tok[0]
            tmp += [ " ".join(tok) ]
            continue

        # cap formats:
        #  cname t1 t2   <numeric0> $[model] $SUB=t3 m=...
        #  cname t1 t2   <numeric0> $[model] m=...
        #? cname t1 t2 C=<numeric0> $[model] $SUB=t3 m=...
        #? cname t1 t2   <numeric0> $[model] $SUB=t3 area=<numericA> perimeter=<numericP> m=...
        #? cname t1 t2   <numeric0> $[model] $SUB=t3 area=<numericA> peri=<numericP> m=...
        #l:cname t1 t2  {<numeric0>} {$[model]} {$SUB=t3} {m=...}
        # out formats:
        #  Xcname t1 t2    model area=<numericA> peri=<numericP> m=... par1=...
        #  Xcname t1 t2 t3 model area=<numericA> peri=<numericP> m=... par1=...
        # We require inm, two terminals. Require $[model]. Optional 3rd-term $SUB=...
        # If both peri and perimeter, peri overrides.
        # Both area/peri are optional. The optional [C=]numeric0 is discarded always.

        if c0 == "c":
            tlen = len(tok)
            if tlen < 3:
                err+=1
                msg = "*cdl2spi.py: ERROR: Cap does not have minimum two terminals:"
                tmp += [ msg, i ]
                continue
            if cdlModel == "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Cap missing required $[<model>] directive:"
                tmp += [ msg, i ]
                continue
            tok = mapCap(cdlTerm, cdlModel, tok, options)
            # add X to tok0.
            if options['subckt']:
                tok[0] = "X" + tok[0]
            tmp += [ " ".join(tok) ]
            continue

        # res formats:
        #   rname n1 n2   <numeric> $SUB=t3 $[model] $w=... $l=... m=...
        # c:rname n1 n2 R=<numeric> $[model] w=... l=... m=... $SUB=t3 
        # l:rname n1 n2   {<numeric>} {$SUB=t3} {$[model]} {$w=...} {$l=...} {m=...}
        #  (all after n1,n2 optional)
        #    We require $[model]. And add 3rd term IFF $SUB=.
        # out format:
        #   Xrname n1 n2 t3 model w=... l=... m=... par1=...
        if c0 == "r":
            tlen = len(tok)
            if tlen < 3:
                err+=1
                msg = "*cdl2spi.py: ERROR: Res does not have minimum two terminals:"
                tmp += [ msg, i ]
                continue
            if cdlModel == "":
                err+=1
                msg = "*cdl2spi.py: ERROR: Res missing required $[<model>] directive:"
                tmp += [ msg, i ]
                continue
            tok = mapRes(cdlTerm, cdlModel, tok, options)
            # add X to tok0.
            if options['subckt']:
                tok[0] = "X" + tok[0]
            tmp += [ " ".join(tok) ]
            continue

        # bipolar formats:
        #   qname n1 n2 n3 model <numeric> M=... $EA=...
        #   qname n1 n2 n3 model $EA=... <numeric> M=... 
        #   qname n1 n2 n3 model {$EA=...} {$W=...} {$L=...} {$SUB=...} {M=...}
        # No: l:qname n1 n2 n3 {nsub} model {$EA=...} {$W=...} {$L=...} {$SUB=...} {M=...}
        #   CDL-std adds {nsub} way to add substrate before model: We don't support it.
        #   Add 3rd term IFF $SUB=. We propagate optional W/L (or derived from $W/$L).
        #   EA is emitterSize; not supported by ngspice: deleted.
        #   We require 3-terminals and model. If $[model] is specified, it is ignored
        #   with a warning.
        #
        # out format:
        #   Xqname n1 n2 n3 model M=... par1=...
        if c0 == "q":
            tlen = len(tok)
            if tlen < 5:
                err+=1
                msg = "*cdl2spi.py: ERROR: Bipolar does not have minimum three terminals and a model:"
                tmp += [ msg, i ]
                continue
            if cdlModel != "":
                warn+=1
                msg = "*cdl2spi.py: WARNING: Bipolar does not support $[<model>] directive, model is " + cdlModel + ":"
                tmp += [ msg, i ]
                continue
            tok = mapBipolar(cdlTerm, "", tok, options)
            # add X to tok0.
            if options['subckt']:
                tok[0] = "X" + tok[0]
            tmp += [ " ".join(tok) ]
            continue

        # Anything else. What to do, preserve AS-IS with warning, or 
        # flag them as ERRORs?
        tmp += [ "*cdl2spi.py: ERROR: unrecognized line:", i ]
        err+=1
        # tmp += [ "*cdl2spi.py: WARNING: unrecognized line:", " ".join(tok) ]
        # tmp += [ "*cdl2spi.py: WARNING: unrecognized line:", i ]
        # warn+=1

    # Re-wrap continuation lines at 80 characters
    lines = []
    for line in tmp:
        lines.append('\n+ '.join(textwrap.wrap(line, 80)))

    # Write output

    if fnmOut == sys.stdout:
        for i in lines:
            print(i)
    else:
        try:
            with open(fnmOut, 'w') as outFile:
                for i in lines:
                    print(i, file=outFile)
        except:
            print('cdl2spi.py: failed to open ' + fnmOut + ' for writing.', file=sys.stderr)
            return 1

    # exit status: indicates if there were errors.
    print( "*cdl2spi.py: %d errors, %d warnings" % (err, warn))
    return err

if __name__ == '__main__':

    options = {}

    # Set option defaults
    options['debug'] = False
    options['subckt'] = False
    options['dscale'] = ''
    options['addinm'] = []
    options['ignore'] = []

    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            thisopt = item.split('=')
            optname = thisopt[0][1:]
            optval = '='.join(thisopt[1:])
            if not optname in options:
                print('Unknown option -' + optname + '; ignoring.')
            else:
                lastoptval = options[optname]
                if len(thisopt) == 1:
                    options[optname] = True
                elif lastoptval == '':
                    options[optname] = optval
                else:
                    options[optname].append(optval)
        else:
            arguments.append(item)

    # Supported primitive devices (FET, diode, resistor, capacitor, bipolar)
    primch  = 'mdrcq'
    primch2 = 'mdrcqx'

    if len(arguments) > 0:
        fnmIn = arguments[0]

    if len(arguments) > 1:
        fnmOut = arguments[1]
    else:
        fnmOut = sys.stdout

    if options['debug']:
        test_mapSubcktInst1()
        test_mapSubcktInst2()
        test_mapMfactor()
        test_CDLparam()
        test_CDLtermModel()
        test_mapDiscard()
        test_mapPartAssign()
        test_mapLookup()
        test_mapDiode()
        test_mapMos()
        test_mapCap()
        test_mapRes()
        test_mapBipolar()

    elif len(arguments) > 2 or len(arguments) < 1 :
        print('Usage: cdl2spi.py <cdlFileName> [<spiFileName>]')
        print('   Options:' )
        print('       -debug              run debug tests')
        print('       -dscale=<suffix>    rescale lengths with <suffix>')
        print('       -addinm=<param>     add multiplier parameter <param>')
        print('       -ignore=<param>     ignore parameter <param>')
        print('       -subckt             convert primitive devices to subcircuits')
        sys.exit(1)

    else:
        if options['debug'] == True:
            print('Diagnostic:  options = ' + str(options))
        result = cdl2spice(fnmIn, fnmOut, options)
        sys.exit(result)

