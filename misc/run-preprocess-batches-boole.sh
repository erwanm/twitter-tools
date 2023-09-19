#!/bin/bash

#set -x

if [ "$1" == "-d" ]; then
    dryrun='yep'
    shift
fi

if [ $# -ne 3 ] && [ $# -ne 6 ]; then
    echo "Usage: $0 [-d] <input dir> <output dir> <options for preprocess-spacy.py> [<work dir> <batch size> <Ncores>]"
    echo ""    
    echo "  The input dir contains .tsv files containing the conversations tweets WITHOUT header"
    echo "  -d = dry run"
    echo ""
    echo "  Use absolute paths"
    exit 1
fi


inputDir="$1"
outputDir="$2"
options="$3"
workDir="$4"
batchSize="$5"
ncores="$6"

if [ -z "$workDir" ]; then
    workDir="jobs"
    batchSize=100000
    ncores=32
fi

if [ ! -d "$inputDir" ] ; then
    echo "Error no dir $inputDir"
    exit 1
fi
if [ ! -d "$outputDir" ] ; then
    mkdir "$outputDir"
fi
if [ ! -d "$workDir" ] ; then
    mkdir "$workDir"
fi
batchesDir="$workDir/input-batches"
if [ ! -d "$batchesDir" ] ; then
    mkdir "$batchesDir"
else 
    rm -f "$batchesDir"/*
fi
tasksDir="$workDir/tasks"
if [ ! -d "$tasksDir" ] ; then
    mkdir "$tasksDir"
else 
    rm -f "$tasksDir"/*
fi
if [ ! -d "$workDir/out" ]; then
    mkdir "$workDir/out"
fi

find "$inputDir" | xargs cat | split -d -l "$batchSize" -a 5 - "$batchesDir"/
alltasks="$workDir/alltasks"
for f in "$batchesDir"/*; do
    b=$(basename "$f")
    echo "ls $f | python3 /home/moreaue/VirtualEngAge/system/twarc2/preprocess-spacy.py $options \"$outputDir\" >\"$workDir/out/$b.out\" 2>&1 &" 
done > "$alltasks"
split -d -l $ncores -a 4 $alltasks "$tasksDir/"
for f in "$tasksDir"/*; do
    echo '#!/bin/bash' > $f.sh
    echo "source /home/moreaue/init-conda-twarc2.sh" >>$f.sh
    cat $f >> $f.sh
    echo "wait"  >>$f.sh
    rm -f $f
done
if [ -z "$dryrun" ]; then
    for f in "$tasksDir"/*; do
	sbatch --cpus-per-task=32 --mem=62G $f
    done
else
    echo 'Dry run mode, not starting jobs.'
fi
