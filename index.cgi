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

use strict;
use warnings;
no warnings 'uninitialized';

use CGI::Tiny;
use Text::Xslate qw(mark_raw);

cgi {
    # "Password" for showing hidden pages. (Not secure!)
    my $pw = "showme";

    my $cgi = $_;
    my ($me) = $0 =~ /\/([^\/]*)$/;   # Name of this script. Use $me in all local URLs.
    my $cnt_path = 'cnt';         # Folder for content files, relative to main script.
    
    ### CHECK IF LOGGED IN ###
    my $logged_in =
	(defined($cgi->cookie("$me-logged_in")) && !(defined($cgi->param('loggin')) && $cgi->param('loggin') eq 'logout'))
	||
	(defined($cgi->param('loggin')) && $cgi->param('loggin') eq $pw)
	? 1
	: 0;
    
    ### CONSTRUCT DATA STRUCTURES ###
    my %file_by_ID;
    my %par_by_ID;
    my %locked_by_ID;
    my %menu ;
    my ($locked, $ID, $par_ID, $order, $name);
    my $cnt_file;
    my @cnt_files = glob("$cnt_path/*");
    foreach my $f (@cnt_files){
	next if $f =~ /(~|#)$/;
	($cnt_file) = $f =~ /\/([^\/]*)$/;
	($locked, $ID, $par_ID, $order, $name) = split(/--/, $cnt_file);
	$name =~ s/_/ /;

	$file_by_ID{$ID} = $cnt_file;
	$par_by_ID{$ID} = $par_ID;
	$locked_by_ID{$ID} = $locked;
	
	$menu{$par_ID}[$order]{'locked'} = $locked;
	$menu{$par_ID}[$order]{'ID'} = $ID;
	$menu{$par_ID}[$order]{'name'} = $name;
    }

    ### IDENTIFY CURRENT PAGE ###
    my $current_page = $cgi->param('page');
    if (!defined($current_page) ||
	!defined($file_by_ID{$current_page}) ||
	(!$logged_in && $locked_by_ID{$current_page} == 1)){
	foreach my $item (@{$menu{'T'}}){
	    if ($item && ${$item}{'locked'} <= $logged_in){
		$current_page = ${$item}{'ID'};
		last;
	    }
	}
    }
    
    ### RETRIEVE PAGE CONTENT FROM CNT FILE ###
    require "./$cnt_path/$file_by_ID{$current_page}";
    my $pnc = page_content($cgi, $me, $current_page, $cgi->param('subpage'), $logged_in, $cnt_path);
    if (defined($pnc->{'p_cont'}{'js_src'})){
	$pnc->{'p_cont'}{'js_src'} = "src=\"" . $pnc->{'p_cont'}{'js_src'} . "\"";
    }
	

    ### CREATE MENU ###
    my $main_menu;
    my $highlight;
    my $this_ID;
    my $this_name;
    my $sub_ID;
    my $sub_name;
    my $sub_current;
    
    if ($pnc->{'current_sub'}){
	$sub_current = $pnc->{'current_sub'};
    }
    elsif ($cgi->param('subpage')){
	$sub_current = $cgi->param('subpage');
    }
    
    foreach my $top_item (@{$menu{'T'}}){
	next unless $top_item;
	next if (${$top_item}{'locked'} && !$logged_in);

	$this_ID = ${$top_item}{'ID'};
	$this_name = ${$top_item}{'name'};
	$highlight = $this_ID eq $current_page && !defined($sub_current) ? '>' : '&nbsp;';
	$main_menu .= "$highlight&nbsp;<a href=\"$me?page=$this_ID\">$this_name</a><br>\n";
	if ($pnc->{'submenu'} && $this_ID eq $current_page){
	    foreach my $sub_item (@{$pnc->{'submenu'}}){
		next unless $sub_item;
		next if (${$sub_item}{'locked'} && !$logged_in);

		$sub_ID = ${$sub_item}{'ID'};
		$sub_name = ${$sub_item}{'name'};
		$highlight = $sub_ID eq $sub_current ? '>' : '&nbsp;';
		$main_menu .= "<span class=\"sub_menu\">&nbsp;&nbsp;$highlight&nbsp;<a href=\"$me?page=$current_page&subpage=$sub_ID\">$sub_name</a></span><br>\n";
	    }
	}
	elsif ($menu{$this_ID} && ($this_ID eq $current_page || $this_ID eq $par_by_ID{$current_page})){
	    foreach my $sub_item (@{$menu{$this_ID}}){
		next unless $sub_item;
		next if (${$sub_item}{'locked'} && !$logged_in);

		$sub_ID = ${$sub_item}{'ID'};
		$sub_name = ${$sub_item}{'name'};
		$highlight = $sub_ID eq $current_page ? '>' : '&nbsp;';
		$main_menu .= "<span class=\"sub_menu\">&nbsp;&nbsp;$highlight&nbsp;<a href=\"$me?page=$sub_ID\">$sub_name</a></span><br>\n";
	    }
	}
    }
    
    ### CREATE LOGIN FORM ###
    my $loggin;
    if (!$logged_in){
	$loggin = "
	<form action=\"$me\" method=\"POST\">
        <input type=\"text\" name=\"loggin\" size=\"12\"><br>
        <input type=\"submit\" value=\"LOG IN\">
        <input type=\"hidden\" name=\"page\" value=\"$current_page\">
        </form>";
    }
    else {
	$loggin = "
	<form action=\"$me\" method=\"POST\">
        <input type=\"submit\" value=\"LOG OUT\">
        <input type=\"hidden\" name=\"loggin\" value=\"logout\">
        <input type=\"hidden\" name=\"page\" value=\"$current_page\">
        </form>";
    }
    
    ### HANDLE COOKIE DIRECTIVES FROM PAGE ###
    if (defined($pnc->{'cookies'})){
	foreach my $cookie (keys %{$pnc->{'cookies'}}){
	    $cgi->add_response_cookie(
		$cookie => $pnc->{'cookies'}{$cookie}{'value'},
		'Expires' => $pnc->{'cookies'}{$cookie}{'expires'},
		);
	}
    }

    ### MANAGE LOGGIN COOKIE ###
    if ($logged_in && !defined($cgi->cookie("$me-logged_in"))){
	$cgi->add_response_cookie(
	    "$me-logged_in" => 1,
	    'Expires' => 0
	    );
    }
    elsif (!$logged_in && defined($cgi->cookie("$me-logged_in"))){
	$cgi->add_response_cookie(
	    "$me-logged_in" => '',
	    'Expires' => CGI::Tiny::epoch_to_date(0)
	    );
    }
    
    ### RENDER AND SEND PAGE ###
    my $tx = Text::Xslate->new(type => 'html');
    $cgi->render(html => $tx->render('index.tmpl',{
	main_menu => mark_raw($main_menu),
	loggin => mark_raw($loggin),
	title => mark_raw($pnc->{'p_cont'}{'title'}),
	style => mark_raw($pnc->{'p_cont'}{'style'}),
	js_src => mark_raw($pnc->{'p_cont'}{'js_src'}),
	javascript => mark_raw($pnc->{'p_cont'}{'javascript'}),
	head => mark_raw($pnc->{'p_cont'}{'head'}),
	center_content => mark_raw($pnc->{'p_cont'}{'center_content'}),
				     }));
}
