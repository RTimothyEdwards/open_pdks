#!/bin/bash
#
# download.sh --
#	Download a tarball from the specified URL to the specified target
#	directory, untar it, and remove the tarball file.  If the URL is
#	a repository and not a file, then clone it.
#
#	Usage:  download.sh <url> <target_dir> [<strip>|<commit>|<tag>]
#
# where:
#
#	<url> is the URL of the repository to download.  If the <url> ends
#		in 'gz' then it is assumed to be a gzipped tarball format.
#		Otherwise, it is assumed to be a clonable git repo.
#	<target_dir> is the local name to call the untarred directory.  The
#		tarball will be downloaded to the directory above this,
#		untarred while renaming to <target_dir>, and then the tarball
#		file will be deleted.
#	<strip> is the number of directory levels to strip off the front of the
#		tarball contents.  Defaults to 1 if not specified (only
#		applicable if <url> points to a tarball).
#	<commit> or <tag> is a specific reference commit to clone.  If the
#		<url> is not a git repository, then this option has no effect.
#

# Check if <url> points to a tarball or a repository (note:  this assumes
# the form on github where the filename is spelled out as ".tar.gz" and
# not ".tgz")

function GIT() {
    set -Eeuo pipefail
    RETRIES_NO=5
    RETRY_DELAY=3
    for i in $(seq 1 $RETRIES_NO); do
        git $@ && break
        sleep ${RETRY_DELAY}
        [[ $i -eq $RETRIES_NO ]] && echo "Failed to execute git cmd after $RETRIES_NO retries" && exit 1
    done
}

set -e

if [ "${1: -3}" == ".gz" ] ; then

    # Neither curl or wget are guaranteed to be included in all *nix systems,
    # (but most have *one* of them). This tools tries its best to find one.

    DL_CMD=
    if type "wget" > /dev/null; then
        DL_CMD="wget --tries=5 -qO"
    fi

    if type "curl" > /dev/null; then
        DL_CMD="curl --retry 5 --retry-all-errors -sLo"
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

else

    if type "git" > /dev/null; then
        echo "Cloning $1 to $2"
        if [ $# -gt 2 ]; then
            if [ "$3" == "unknown" ]; then
                GIT clone --depth 1 $1 $2
            else
                # git clone $1 $2
                # git checkout $3
                { GIT clone --branch $3 --single-branch $1 $2; } || \
                { GIT clone $1 $2 && GIT -C $2 checkout $3; }
            fi
        else
            GIT clone --depth 1 $1 $2
        fi

    else
        echo "ERROR: \"git\" is required to automatically install tools."
        exit 1
    fi
fi

exit 0
