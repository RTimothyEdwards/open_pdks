#!/bin/sh
#
# Example file converts the techname in all magic database files.

for i in `ls *.mag` ; do
    /ef/efabless/bin/preproc.py -DEFXH035A=EFXH035B $i > tmp.out
    mv tmp.out $i ;
done

