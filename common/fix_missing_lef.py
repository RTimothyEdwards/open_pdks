#!/usr/bin/env python3

import re
import os
import sys
import argparse


parser = argparse.ArgumentParser(
    description='This file fixes the missing')

parser.add_argument('--skywater_path', '-sp',required=True,
                    help='skywater path')

parser.add_argument('--modify_hs_ms_diodes', '-mhmd',action='store_true', default=False,
                help="modifies the hs and ms diode information.")

parser.add_argument('--modify_vnb_vpb', '-mvv',action='store_true', default=False,
                help="modifies the vnb and vpb of all cells in all libraries.")


args = parser.parse_args()
skywater_path = args.skywater_path
modify_hs_ms_diodes = args.modify_hs_ms_diodes
modify_vnb_vpb = args.modify_vnb_vpb

libraries = ['sky130_fd_sc_hd','sky130_fd_sc_hdll','sky130_fd_sc_hs','sky130_fd_sc_ms','sky130_fd_sc_ls']

if modify_vnb_vpb:
    for lib in libraries:
        modify_vpb_result_cmd = "sed -i 's/PIN VPB/PIN VPB\nDIRECTION INOUT ;\nUSE POWER ;/g' {lef} ".format(
            lef= skywater_path+"/libraries/"+lib+"/*/cells/*/*.magic.lef"
            )
        subprocess.check_output(modify_vpb_result_cmd.split())

        modify_vnb_result_cmd = "sed -i 's/PIN VNB/PIN VNB\nDIRECTION INOUT ;\nUSE GROUND ;/g' {lef} ".format(
            lef= skywater_path+"/libraries/"+lib+"/*/cells/*/*.magic.lef"
            )
        subprocess.check_output(modify_vnb_result_cmd.split())

if modify_hs_ms_diodes:
    hs_lef =  skywater_path+"/libraries/sky130_fd_sc_hs/latest/cells/diode/sky130_fd_sc_hs__diode_2.magic.lef"
    
    hs_lef_FileOpener = open(hs_lef, "r")
    if(path.exists(hs_lef_FileOpener)):
        if hs_lef_FileOpener.mode == 'r':
            hs_lef_Content = hs_lef_FileOpener.read()
        hs_lef_FileOpener.close()
        sections = hs_lef_Content.split("MACRO sky130_fd_sc_hs__diode_2")
        sections.append(sections[1].split("END sky130_fd_sc_hs__diode_2")[1])
        sections.append(sections[1].split("END sky130_fd_sc_hs__diode_2")[0])
        # now sections[1] contains diode info;
        sections[1] = sections[1].replace("CLASS BLOCK","CLASS CORE ANTENNACELL")
        sections[1] = "\nSYMMETRY X Y ;\nSITE unit ;\n"+sections[1]
        sections[1] = sections[1].replace("PIN DIODE","PIN DIODE\nDIRECTION INPUT ;\nUSE SIGNAL ;\n")
        combined = "MACRO sky130_fd_sc_hs__diode_2".join(sections[0:1])
        combined = combined+"END sky130_fd_sc_hs__diode_2"+ sections[2]
        hs_lef_FileOpener = open(hs_lef,"w")
        hs_lef_FileOpener.write(combined)
        hs_lef_FileOpener.close()


    ms_lef =  skywater_path+"/libraries/sky130_fd_sc_ms/latest/cells/diode/sky130_fd_sc_ms__diode_2.magic.lef"
    
    ms_lef_FileOpener = open(ms_lef, "r")
    if(path.exists(ms_lef_FileOpener)):
        if ms_lef_FileOpener.mode == 'r':
            ms_lef_Content = ms_lef_FileOpener.read()
        ms_lef_FileOpener.close()
        sections = ms_lef_Content.split("MACRO sky130_fd_sc_ms__diode_2")
        sections.append(sections[1].split("END sky130_fd_sc_ms__diode_2")[1])
        sections.append(sections[1].split("END sky130_fd_sc_ms__diode_2")[0])
        # now sections[1] contains diode info;
        sections[1] = sections[1].replace("CLASS BLOCK","CLASS CORE ANTENNACELL")
        sections[1] = "\nSYMMETRY X Y ;\nSITE unit ;\n"+sections[1]
        sections[1] = sections[1].replace("PIN DIODE","PIN DIODE\nDIRECTION INPUT ;\nUSE SIGNAL ;\n")
        combined = "MACRO sky130_fd_sc_ms__diode_2".join(sections[0:1])
        combined = combined+"END sky130_fd_sc_ms__diode_2"+ sections[2]
        ms_lef_FileOpener = open(ms_lef,"w")
        ms_lef_FileOpener.write(combined)
        ms_lef_FileOpener.close()
