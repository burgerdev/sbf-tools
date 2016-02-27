#!/bin/bash

set -e

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


echo "This script is meant for development use and should **NEVER** be used in production!"

if [[ "$1" == "" ]] 
then
    DIRNAME="$APPDIR/data"
    echo "without argument, serving data from directory $DIRNAME"
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

echo "started REST API server at $PORTA [$!]"

python3 -m http.server $PORTB >http.out 2>http.err &

echo "started HTTP server (for images) at $PORTB [$!]"

cd "$LASTDIR"

