#--------------------------------------------------------------------
# Usage:
#   klayout -z \
#       -rd infile=<gds file> \
#       -rd patch=<gds file> \
#       -rd outfile=<gds file> \
#       -r simple_gds_merge.rb
#
# Description:
#   This script will patch the $infile by merging the $patch gds and writing
#   the  result to $outfile.
#--------------------------------------------------------------------

layout = RBA::Layout.new
layout.read($infile)
layout.read($patch)
layout.write($outfile)

