#!/bin/bash
#
# download.sh --
#	Download a tarball from the specified URL to the specified target
#	directory, untar it, and remove the tarball file.
#
#	Usage:  download.sh <url> <target_dir> [<strip>]
#
# where:
#
#	<url> is the URL of the repository to download, in gzipped tarball format
#	<target_dir> is the local name to call the untarred directory.  The
#		tarball will be downloaded to the directory above this,
#		untarred while renaming to <target_dir>, and then the tarball
#		file will be deleted.
#	<strip> is the number of directory levels to strip off the front of the
#		tarball contents.  Defaults to 1 if not specified.
#

# Neither curl or wget are guaranteed to be included in all *nix systems,
# (but most have *one* of them). This tools tries its best to find one.

DL_CMD=
if type "wget" > /dev/null; then
    DL_CMD="wget -qO"
fi

if type "curl" > /dev/null; then
    DL_CMD="curl -sLo"
fi

if [ "$DL_CMD" = "" ]; then
    echo "ERROR: Either curl or wget are required to automatically install tools."
    exit 1
fi

pdir=`dirname $2`
mkdir -p $pdir
cd $pdir

echo "Downloading $1 to $2"
$DL_CMD $2.tar.gz $1

if [ $# -gt 2 ]; then
    snum=$3
else
    snum=1
fi

mkdir -p $2
echo "Untarring and removing $2.tar.gz"
tar -xf $2.tar.gz --strip-components $snum -C $2
rm $2.tar.gz
exit 0
