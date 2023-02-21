#!/bin/bash

#set -x


locationFile="places-iso3.tsv"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <work dir/input users> <next index> <until index>"
    echo ""    
    echo "   The <input users> file must be located in the work dir."    
    echo ""    
    echo "  For the input set of users (input text file, one by line first col), collects all the followers/following users,"
    echo "  then filters those who contain the 'older adults' words, then filters those whose location is Ireland."
    echo "  This process is iterated from <next index> to <until index>. Files stored in the same dir as <input users>."
    exit 1
fi


inputUsers="$1"
nextIndex="$2"
untilIndex="$3"


if [ ! -f "$inputUsers" ] ; then
    echo "Error no file $inputUsers"
    exit 1
fi
if [ ! -f "$locationFile" ] ; then
    echo "Error no file $locationFile"
    exit 1
fi


workDir=$(dirname "$inputUsers")
targetDir="$workDir/data"
if [ ! -d "$targetDir" ]; then
    mkdir "$targetDir"
fi

prevFile="$workDir/previous-ids.list"
while [ $nextIndex -le $untilIndex ]; do
    echo "###LOOP nextIndex=$nextIndex ###"
    prefix="$workDir/iter.$nextIndex"
    echo "  Collecting fron Twitter step $nextIndex ..."
    cat "$inputUsers" | cut -f 1 | while read id; do
	if [ ! -s "$targetDir/$id.following.users" ]; then
	    python3 collect-following.py $id "$targetDir/$id.following.users" &>"$targetDir/$id.following.out"
	    if [ $? -ne 0 ]; then
		echo "Error" 1>&2
		exit 3
	    fi
	fi
	if [ ! -s "$targetDir/$id.followers.users" ]; then
	    python3 collect-following.py -r $id "$targetDir/$id.followers.users" &>"$targetDir/$id.followers.out"
	    if [ $? -ne 0 ]; then
		echo "Error" 1>&2
		exit 3
	    fi
	fi
    done
    echo "  $prefix: filtering ..."
    cat "$targetDir"/*.users |  sort -u -k1,1 | grep -i -e grandchild -e grandfather -e grandmother -e granddad -e granny -e grandparent -e retired -e retirement > "$prefix.grandparents"
    newusers="$prefix.grandparents"
    if [ -s  "$prevFile" ]; then
	newusers="$prefix.newusers"
	cat "$prefix.grandparents" | filter-column.pl -n -s "$prevFile" 1 1 >"$newusers"
    fi
    cut -f 1 "$newusers" >>"$prevFile"
    cat "$newusers" | cut -f 5 | python3 filter-user-location.py "$locationFile" >"$prefix.grandparents.country-col" 2>"$prefix.filter-user-location.err"
    paste "$newusers" "$prefix.grandparents.country-col" >"$prefix.grandparents.country"
    cat "$prefix.grandparents.country" | filter-column.pl -v IRL dummy 6 >"$prefix.grandparents.IRL"
    echo -n " New grandparents IRL step $nextIndex = "
    cat "$prefix.grandparents.IRL" | wc -l
    inputUsers="$prefix.grandparents.IRL"
    nextIndex=$(( $nextIndex + 1 ))
done

