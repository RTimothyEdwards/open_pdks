#!/usr/bin/env python3

# This script can be removed when GitHub issue #141 (https://github.com/google/skywater-pdk/issues/141) is fixed.
from os import path
import argparse
import subprocess

parser = argparse.ArgumentParser(
    description='This file fixes the missing diode information from the LEF files of the ms and hs')

parser.add_argument('--skywater_path', '-sp',required=True,
                    help='skywater path')


args = parser.parse_args()
skywater_path = args.skywater_path


hs_lef =  str(skywater_path)+"/sky130_fd_sc_hs/latest/cells/diode/sky130_fd_sc_hs__diode_2.magic.lef"

hs_lef_FileOpener = open(hs_lef, "r")
if(path.exists(hs_lef)):
    if hs_lef_FileOpener.mode == 'r':
        hs_lef_Content = hs_lef_FileOpener.read()
    hs_lef_FileOpener.close()
    hs_lef_Content = hs_lef_Content.replace("CLASS BLOCK","CLASS CORE ANTENNACELL")
    if hs_lef_Content.find("PIN DIODE\n    DIRECTION INPUT ;") == -1:
        hs_lef_Content = hs_lef_Content.replace("PIN DIODE","SYMMETRY X Y ;\n  SITE unit ;\n  PIN DIODE\n    DIRECTION INPUT ;\n    USE SIGNAL ;")
    hs_lef_FileOpener = open(hs_lef,"w")
    hs_lef_FileOpener.write(hs_lef_Content)
    hs_lef_FileOpener.close()


ms_lef =  str(skywater_path)+"/sky130_fd_sc_ms/latest/cells/diode/sky130_fd_sc_ms__diode_2.magic.lef"

ms_lef_FileOpener = open(ms_lef, "r")
if(path.exists(ms_lef)):
    if ms_lef_FileOpener.mode == 'r':
        ms_lef_Content = ms_lef_FileOpener.read()
    ms_lef_FileOpener.close()
    ms_lef_Content = ms_lef_Content.replace("CLASS BLOCK","CLASS CORE ANTENNACELL")
    if ms_lef_Content.find("PIN DIODE\n    DIRECTION INPUT ;") == -1:
        ms_lef_Content = ms_lef_Content.replace("PIN DIODE","SYMMETRY X Y ;\n  SITE unit ;\n  PIN DIODE\n    DIRECTION INPUT ;\n    USE SIGNAL ;")
    ms_lef_FileOpener = open(ms_lef,"w")
    ms_lef_FileOpener.write(ms_lef_Content)
    ms_lef_FileOpener.close()
