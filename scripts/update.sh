#!/bin/bash
#
# update.sh --
#	Update a package in sources/.  If the package is a git
#	repository, then do a git pull.  (Use download.sh for
#	tarballs.)
#
#	Usage:  update.sh <target_dir>
#
# where:
#
#	<target_dir> is the local name of a git repository directory.
#

set -e

if type "git" > /dev/null; then
    echo "Pulling $1 into $2"
    cd $2
    git pull

else
    echo "ERROR: \"git\" is required to automatically update repositories."
    exit 1
fi

exit 0

