#!/usr/bin/perl

# ----- POCKET-CMS v. 1 -----
#
# A tiny web content management system.
#
# Homepage: https://github.com/HenningStrandin/Pocket-CMS
#
# Copyright (C) 2020 Henning Strandin (henning.strandin@proton.me)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See <https://www.gnu.org/licenses/>.

# ----- USAGE -----
#
# Run this script before creating a new web page to see the next
# free page ID and the top-level menu order of existing pages.

use strict;

my $cnt_dir = shift;
if (!defined $cnt_dir) {
    print "Usage: $0 <content_directory>\n";
    exit 1;
}

$cnt_dir =~ s{/$}{};

my @cnt_files = glob("$cnt_dir/*");
my $cnt_file;
my ($locked, $ID, $par_ID, $order, $name);
my @IDs;
my $next_no;
my %T_order;

foreach my $f (@cnt_files){
    ($cnt_file) = $f =~ /\/([^(\/~)]*)$/;
    ($locked, $ID, $par_ID, $order, $name) = split(/--/, $cnt_file);
    $name =~ s/_/ /;

    $IDs[$ID] = 1;

    if ($par_ID eq 'T'){
	$T_order{$order} = $name;
    }
}

for (my $i = 0; $i <= @IDs; $i++){
    if (!defined($IDs[$i])){
	$next_no = sprintf("%04d", $i);
	last;
    }
}

print "** Menu Order **\n";
foreach my $o (sort {$a <=> $b} keys %T_order){
    print $o . " " . $T_order{$o} . "\n";
}
print "\n";

print "** New filename:\n";
print "$cnt_dir/[L]--$next_no--[PAR-ID]--[ORDER]--[NAME]\n";
print "\n";
print "L: 0 if visible, 1 if hidden begind \"login.\"\n";
print "PAR-ID: ID of parent page if a subpage, \"T\" otherwise.\n";
print "ORDER: Place in menu ordering.\n";
print "NAME: Name of the page displayed in menu.\n";
