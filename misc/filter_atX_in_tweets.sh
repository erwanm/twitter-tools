#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: cat <tweets data> | $0 <user ids file>" 1>&2
    echo "  searches and prints (grep) all the lines which contains one of the user ids" 1>&2
    exit 3
fi

useridsFile="$1"
prefixOut="$2"

pattern=$(cat "$useridsFile" | while read user; do
    pattern="$pattern -e @$user"
    echo "$pattern"
done | tail -n 1)
echo "$pattern" 1>&2
grep -i $pattern

