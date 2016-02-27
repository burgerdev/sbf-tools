#!/bin/bash

set -e

echo "Copyright (C) 2016 Markus Doering"
echo "This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE."
echo "This is free software, and you are welcome to redistribute it under"
echo "certain conditions; for details see LICENSE."
echo ""


PORTA=8000
PORTB=8001
APPDIR="`dirname $0`"
if [[ "$APPDIR" == "" ]]
then
    APPDIR=.
fi


LASTDIR="`pwd`"
cd "$APPDIR"
APPDIR="`pwd`"
cd "$LASTDIR"


echo "This script is meant for development use and should **NEVER** be used"
echo "in production!"
echo ""

if [[ "$1" == "" ]] 
then
    DIRNAME="$APPDIR/data"
    echo "No argument given -> serving data from '$DIRNAME'"
    echo ""
else
    DIRNAME="$1"
fi

cd "$DIRNAME"

if [[ ! -f jquery.min.js ]]
then
    echo "jquery.min.js not found in `pwd`"
    echo "add it manually"
    exit 2
fi


python3 "$APPDIR/server/server.py" -s "$APPDIR/site/site-local.html" "$APPDIR/data/catalog.json" -p $PORTA >rest.out 2>rest.err &

echo "Started REST API server at $PORTA [pid=$!]."

python3 -m http.server $PORTB >http.out 2>http.err &

echo "Started HTTP server (for images) at $PORTB [pid=$!]."
echo "Logs can be found under '`pwd`/*.{out,err}'."

cd "$LASTDIR"

