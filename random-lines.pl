#!/usr/bin/perl

use strict;
use warnings;
use Getopt::Std;

# erwan 5/4/11, modif 24/4/13



sub usage {
	my $fh = shift;
	$fh = *STDOUT if (!defined $fh);
	print $fh "Usage: random-lines.pl [options] <M> <input start line> <input end line>\n";
	print $fh "  reads N lines from STDIN starting at line no <start> and ending at\n";
	print $fh "  line no <end> (inclusive, counting from 1), and randomly selects <M>\n";
	print $fh "  lines which are written to STDOUT.\n";
	print $fh "  Note that the order in which the lines are written is NOT random\n";
	print $fh "  (only the selection of M among N is).\n";
	print $fh "\n";
	print $fh "  -r <file> writes the remaining (non selected) lines to this file.\n";
	print $fh "\n";
}

# PARSING OPTIONS
my %opt;
getopts('hr:', \%opt ) or  ( print STDERR "Error in options" &&  usage(*STDERR) && exit 1);
usage($STDOUT) && exit 0 if $opt{h};
print STDERR "3 arguments expected but ".scalar(@ARGV)." found: ".join(" ; ", @ARGV)  && usage(*STDERR) && exit 1 if  (scalar(@ARGV) != 3);
my $nbOutput = $ARGV[0];
my $min=$ARGV[1];
my $max=$ARGV[2];
my $remainingFile=$opt{r};

my @input = ($min..$max);
my %selected;
die "Error: max-min+1 < nboutput" if ($max-$min+1<$nbOutput);
for (my $i=0; $i< $nbOutput; $i++) {
    my $randomIndex = int(rand(scalar(@input)));
#    print STDERR "debug: selected $randomIndex in  ".scalar(@input)." : ".join(",",@input)." ; selected = ".join(",", (keys %selected))."\n";
    $selected{$input[$randomIndex]} = 1;
    $input[$randomIndex] = $input[0];
    shift @input;
}

my $lineNo=1;
my $checkNb=0;
open(LEFT, ">", "$remainingFile") if (defined($remainingFile));
while (<STDIN>) {
    if (($lineNo >= $min) && ($lineNo <= $max)) {
	if ($selected{$lineNo}) {
#	print STDERR "debug3 lineNo=$lineNo; selected = ".join(",", (sort { $a <=> $b } keys %selected))."\n";
	    print "$_";
	    $checkNb++;
	} elsif (defined($remainingFile)) {
	    print LEFT "$_";
	}
    }
    $lineNo++
}
$lineNo--;
die "Error: lines < max" if ($lineNo < $max);
die "Error: only $checkNb lines" if ($checkNb != $nbOutput);
close(LEFT) if (defined($remainingFile));
