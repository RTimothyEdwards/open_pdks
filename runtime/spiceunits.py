#!/usr/bin/env python3
"""spice_units.py: Converts tuple of (unit, value) into standard unit numeric value."""

import re

# set of metric prefixes and the value needed to multiply by to
# get the "standard" unit for SPICE.  Only standard units will
# be written into the SPICE file, for reasons of universal
# compatibility.

prefixtypes = {
	"T": 1E12,  "tera" : 1E12,
	"G": 1E9,   "giga" : 1E9,
	"M": 1E6,   "mega" : 1E6,   "MEG": 1E6, "meg": 1E6,
	"K": 1E3,   "kilo" : 1E3,   "k":1E3,
	"D": 1E1,   "deca" : 1E1,
	"d": 1E-1,  "deci" : 1E-1,
	"c": 1E-2,  "centi": 1E-2,  "%": 1E-2,
	"m": 1E-3,  "milli": 1E-3,
	"u": 1E-6,  "micro": 1E-6,  "\u00b5": 1E-6, "ppm": 1E-6,
	"n": 1E-9,  "nano" : 1E-9,  "ppb": 1E-9,
	"p": 1E-12, "pico" : 1E-12, "ppt": 1E-12,
	"f": 1E-15, "femto": 1E-15,
	"a": 1E-18, "atto" : 1E-15,
}

# set of known unit types, including some with suffixes, along with a
# keyword that can be used to limit the search if an expected type for
# the value is known.  Keys are used in regular expressions, and so
# may use any regular expression syntax.

unittypes = {
	"[Ff]": "capacitance",
	"[Ff]arad[s]*": "capacitance",
	"\u03a9": "resistance", 
	"[Oo]hm[s]*": "resistance",
	"[Vv]": "voltage",
	"[Vv]olt[s]*": "voltage",
	"[Aa]": "current",
	"[Aa]mp[s]*": "current",
	"[Aa]mpere[s]*": "current",
	"[Ss]": "time",
	"[Ss]econd[s]*": "time",
	"[Hh]": "inductance",
	"[Hh]enry[s]*": "inductance",
	"[Hh]enries": "inductance",
	"[Hh]z": "frequency",
	"[Hh]ertz": "frequency",
	"[Mm]": "distance",
	"[Mm]eter[s]*": "distance",
	"[\u00b0]*[Cc]": "temperature",
	"[\u00b0]*[Cc]elsius": "temperature",
	"[\u00b0]*[Kk]": "temperature",
	"[\u00b0]*[Kk]elvin": "temperature",
	"[Ww]": "power",
	"[Ww]att[s]*": "power",
	"[Vv]-rms": "noise",
	"[Vv]olt[s]*-rms": "noise",
	"'[bohd]": "digital",
	"": "none"
}

# Convert string to either integer or float, with priority on integer
# If argument is not a string, just return the argument.

def numeric(s):
    if isinstance(s, str):
        try:
            return int(s)
        except ValueError:
            return float(s)
    else:
        return s

# Define how to convert SI units to spice values
#
# NOTE: spice_unit_unconvert can act on a tuple of (units, value) where
# value is either a single value or a list of values.  spice_unit_convert
# only acts on a tuple with a single value.  This is because the only large
# vectors are produced by ngspice, and these values need unconverting back
# into the units specified by the datasheet.  Values being converted to
# ngspice units are from the datasheet and are only computed a few at a
# time, so handling vectors is not particularly efficient.

def spice_unit_convert(valuet, restrict=[]):
    """Convert SI units into spice values"""
    # valuet is a tuple of (unit, value), where "value" is numeric
    # and "unit" is a string.  "restrict" may be used to require that
    # the value be of a specific class like "time" or "resistance". 

    # Recursive handling of '/' and multiplicatioon dot in expressions
    if '/' in valuet[0]:
        parts = valuet[0].split('/', 1)
        result = numeric(spice_unit_convert([parts[0], valuet[1]], restrict))
        result /= numeric(spice_unit_convert([parts[1], "1.0"], restrict))
        return str(result)

    if '\u22c5' in valuet[0]:	# multiplication dot
        parts = valuet[0].split('\u22c5')
        result = numeric(spice_unit_convert([parts[0], valuet[1]], restrict))
        result *= numeric(spice_unit_convert([parts[1], "1.0"], restrict))
        return str(result)

    if '\u00b2' in valuet[0]:	# squared
        part = valuet[0].split('\u00b2')[0]
        result = numeric(spice_unit_unconvert([part, valuet[1]], restrict))
        result *= numeric(spice_unit_unconvert([part, "1.0"], restrict))
        return str(result)

    if valuet[0] == "":		# null case, no units
        return valuet[1]

    for unitrec in unittypes:	# case of no prefix
        if re.match('^' + unitrec + '$', valuet[0]):
            if restrict:
                if unittypes[unitrec] == restrict.lower():
                    return valuet[1]
            else:
                return valuet[1]

    for prerec in prefixtypes:
        for unitrec in unittypes:
            if re.match('^' + prerec + unitrec + '$', valuet[0]):
                if restrict:
                    if unittypes[unitrec] == restrict.lower():
                        newvalue = numeric(valuet[1]) * prefixtypes[prerec]
                        return str(newvalue)
                else:
                    newvalue = numeric(valuet[1]) * prefixtypes[prerec]
                    return str(newvalue)

    # Check for "%", which can apply to anything.
    if valuet[0][0] == '%':
        newvalue = numeric(valuet[1]) * 0.01
        return str(newvalue)
    
    if restrict:
        raise ValueError('units ' + valuet[0] + ' cannot be parsed as ' + restrict.lower())
    else:
        # raise ValueError('units ' + valuet[0] + ' cannot be parsed')
        # (Assume value is not in SI units and will be passed back as-is)
        return valuet[1]

# Define how to convert spice values back into SI units

def spice_unit_unconvert(valuet, restrict=[]):
    """Convert spice values back into SI units"""
    # valuet is a tuple of (unit, value), where "value" is numeric
    # and "unit" is a string.  "restrict" may be used to require that
    # the value be of a specific class like "time" or "resistance". 

    # Recursive handling of '/' and multiplicatioon dot in expressions
    if '/' in valuet[0]:
        parts = valuet[0].split('/', 1)
        result = spice_unit_unconvert([parts[0], valuet[1]], restrict)
        if isinstance(result, list):
            result = list(item / spice_unit_unconvert([parts[1], 1.0],
			restrict) for item in result)
        else:
            result /= spice_unit_unconvert([parts[1], 1.0], restrict)
        return result

    if '\u22c5' in valuet[0]:	# multiplication dot
        parts = valuet[0].split('\u22c5')
        result = spice_unit_unconvert([parts[0], valuet[1]], restrict)
        if isinstance(result, list):
            result = list(item * spice_unit_unconvert([parts[1], 1.0],
			restrict) for item in result)
        else:
            result *= spice_unit_unconvert([parts[1], 1.0], restrict)
        return result

    if '\u00b2' in valuet[0]:	# squared
        part = valuet[0].split('\u00b2')[0]
        result = spice_unit_unconvert([part, valuet[1]], restrict)
        if isinstance(result, list):
            result = list(item * spice_unit_unconvert([part, 1.0],
			restrict) for item in result)
        else:
            result *= spice_unit_unconvert([part, 1.0], restrict)
        return result

    if valuet[0] == "":		# null case, no units
        return valuet[1]

    for unitrec in unittypes:	# case of no prefix
        if re.match('^' + unitrec + '$', valuet[0]):
            if restrict:
                if unittypes[unitrec] == restrict.lower():
                    return valuet[1]
            else:
                return valuet[1]

    for prerec in prefixtypes:
        for unitrec in unittypes:
            if re.match('^' + prerec + unitrec + '$', valuet[0]):
                if restrict:
                    if unittypes[unitrec] == restrict.lower():
                        if isinstance(valuet[1], list):
                            return list(item / prefixtypes[prerec] for item in valuet[1])
                        else:
                            return valuet[1] / prefixtypes[prerec]
                else:
                    if isinstance(valuet[1], list):
                        return list(item / prefixtypes[prerec] for item in valuet[1])
                    else:
                        return valuet[1] / prefixtypes[prerec]

    # Check for "%", which can apply to anything.
    if valuet[0][0] == '%':
        if isinstance(valuet[1], list):
            return list(item * 100 for item in valuet[1])
        else:
            return valuet[1] * 100
    
    if restrict:
        raise ValueError('units ' + valuet[0] + ' cannot be parsed as ' + restrict.lower())
    else:
        # raise ValueError('units ' + valuet[0] + ' cannot be parsed')
        # (Assume value is not in SI units and will be passed back as-is)
        return valuet[1]
