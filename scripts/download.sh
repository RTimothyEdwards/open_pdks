#!/bin/sh
#
# Neither curl or wget are guaranteed to be included in all *nix systems,
# (but most have *one* of them). This tools tries its best to find one.
#

DL_CMD=
if type "wget" > /dev/null; then
    DL_CMD="wget -qO"
fi

if type "curl" > /dev/null; then
    DL_CMD="curl -sLo"
fi

if [ "$DL_CMD" = "" ]; then
    echo "Either curl or wget are required to automatically install tools."
    exit 1
fi

echo "Downloading $1 to $2..."
$DL_CMD $2 $1
