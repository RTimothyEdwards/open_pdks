#!/usr/bin/env python3
#
# --------------------------------------------------------------------
# Convert ngspice models to hspice format
# --------------------------------------------------------------------

import argparse
import os
import re
import sys

NUMERIC_REGEX = r'0-9\.e\-\+'
NUMERIC_ONLY_REGEX = re.compile(f'^[{NUMERIC_REGEX}]+[munpfa]?$', re.MULTILINE)

REGEX_EXPRESSION = r'a-zA-Z,\_\*\+\-\/\(\)\.0-9\?><:'
PARAMS_PATTERN = re.compile(rf'(\S+)\s+=\s+\{{"?([{REGEX_EXPRESSION}]+)"?\}}')
PARAMS_NO_BRACE_PATTERN = re.compile(rf'(\S+)\s+=\s+"?([{REGEX_EXPRESSION}]+)"?')
PARAMS_REPLACE = r"\1 = '\2'"

MULTILINE_PARAMS = re.compile(rf'(\S+)\s+=\s+\{{"?([\s{REGEX_EXPRESSION}]+)"?\}}',
                              re.MULTILINE)

SEMICOLON_PATTERN = re.compile(r"(.+);(.+)")
SEMICOLON_REPLACE = r"*\2\n\1"


def quote_params_with_braces(content, *args, **kwargs):
    """Add quotes to param definitions which are enclosed between curly braces"""
    if "{" not in content:
        return content
    return PARAMS_PATTERN.sub(PARAMS_REPLACE, content)


def quote_non_numeric_params(content, *args, **kwargs):
    """Add quotes around parameter definitions which aren't just numbers"""
    res = []
    for line in content.split("\n"):
        for param_name, param_value in PARAMS_NO_BRACE_PATTERN.findall(line):
            if not NUMERIC_ONLY_REGEX.match(param_value.strip()):
                line = line.replace(param_value, f"'{param_value}'")
        res.append(line)
    return "\n".join(res)


def quote_multiline_params(content, *args, **kwargs):
    """Add quotes to param definitions spanning multiple lines"""
    return MULTILINE_PARAMS.sub(PARAMS_REPLACE, content)


def remove_semicolons(content, *args, **kwargs):
    """Replace comments delineated with ; by * and new line"""
    return SEMICOLON_PATTERN.sub(SEMICOLON_REPLACE, content)


def replace_libs_tech(content, *args, **kwargs):
    """Replace references to libs.tech to newly copied hspice"""
    source_path = "../../libs.tech/ngspice"
    dest_path = ""
    if source_path in content:
        content = content.replace(source_path, dest_path)
    return content


def replace_spi_path(content, *args, **kwargs):
    """Replace references to libs.ref to newly copied spi directory"""
    if options.ef_format:
        lib_path = 'spi/sky130_fd_pr/'
    else:
        lib_path = 'sky130_fd_pr/spice/'
    source_path = f'../../libs.ref/{lib_path}'
    dest_path = 'spi/'
    content = content.replace(source_path, dest_path)
    return content


def generic_filter(input_file_name, output_file_name, filters=None):
    filters = filters or []
    with open(input_file_name, "r") as in_file:
        content = in_file.read()
    with open(output_file_name, "w") as out_file:
        _, extension = os.path.splitext(input_file_name)
        if extension == ".spice":
            for filter_func in filters:
                content = filter_func(content, input_file_name=input_file_name, output_file_name=output_file_name)
        out_file.write(content)


def hspice_filter(input_file_name, out_file_name, _):
    filters = [quote_params_with_braces, quote_non_numeric_params,
               quote_multiline_params, remove_semicolons]
    if "hspice/spi" in input_file_name:
        filters.append(replace_libs_tech)
    else:
        filters.append(replace_spi_path)
    generic_filter(input_file_name, out_file_name, filters=filters)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-ef_format", action="store_true")
    options, other_args = parser.parse_known_args()
    if not len(other_args) > 1:
        print('Usage: convert_hspice.py <in_file> [<outfilename>] [-ef_format]')
        sys.exit(1)
    else:
        input_file_name_ = output_file_name_ = other_args[0]
        if len(other_args) > 1:
            output_file_name_ = other_args[1]

    result = hspice_filter(input_file_name_, output_file_name_, options.ef_format)
    sys.exit(result)
